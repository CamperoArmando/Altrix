const express = require("express");
const path = require("path");
const cookieParser = require("cookie-parser");
const api = require("../services/api");

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "../views"));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, "../public")));

// Exige sesión iniciada (token guardado en cookie httpOnly).
function requireAuth(req, res, next) {
    const token = req.cookies.token;
    if (!token) return res.redirect("/login");
    req.token = token;
    next();
}

function mensajeDesdeQuery(req) {
    if (req.query.error) return { tipo: "error", texto: req.query.error };
    if (req.query.ok) return { tipo: "ok", texto: req.query.ok };
    return null;
}

// ---------- Autenticación ----------

app.get("/login", (req, res) => {
    res.render("login", { error: null });
});

app.post("/login", async (req, res) => {
    try {
        const r = await api.login(req.body.email, req.body.password);
        res.cookie("token", r.data.token, { httpOnly: true, sameSite: "lax" });
        res.redirect("/");
    } catch (error) {
        const msg = error.response?.data?.error || "No se pudo iniciar sesión. Intenta de nuevo.";
        res.render("login", { error: msg });
    }
});

app.get("/logout", (req, res) => {
    res.clearCookie("token");
    res.redirect("/login");
});

// ---------- Productos ----------

app.get("/", requireAuth, async (req, res) => {
    try {
        const [productosRes, meRes, categoriasRes] = await Promise.all([
            api.listar(req.token),
            api.me(req.token),
            api.listarCategorias(req.token)
        ]);
        res.render("index", {
            productos: productosRes.data,
            usuario: meRes.data,
            categorias: categoriasRes.data,
            mensaje: mensajeDesdeQuery(req)
        });
    } catch (error) {
        if (error.response?.status === 401) {
            res.clearCookie("token");
            return res.redirect("/login");
        }
        res.render("index", { productos: [], usuario: null, categorias: [], mensaje: null });
    }
});

app.post("/alta", requireAuth, async (req, res) => {
    try {
        const datos = {
            nombre: req.body.nombre,
            precio: parseFloat(req.body.precio),
            cantidad: parseInt(req.body.cantidad),
            categoria: req.body.categoria
        };
        await api.alta(datos, req.token);
    } catch (error) {
        console.error("Error en alta:", error.response?.data || error.message);
    }
    res.redirect("/");
});

app.post("/baja/:id", requireAuth, async (req, res) => {
    try {
        await api.baja(parseInt(req.params.id), req.token);
    } catch (error) {
        console.error("Error en baja:", error.response?.data || error.message);
    }
    res.redirect("/");
});

app.post("/modificar/:id", requireAuth, async (req, res) => {
    try {
        const datos = {
            nombre: req.body.nombre,
            precio: parseFloat(req.body.precio),
            cantidad: parseInt(req.body.cantidad),
            categoria: req.body.categoria
        };
        await api.modificar(parseInt(req.params.id), datos, req.token);
    } catch (error) {
        console.error("Error en modificar:", error.response?.data || error.message);
    }
    res.redirect("/");
});

// ---------- Ventas (HU-05, HU-09) ----------

app.post("/ventas/:id", requireAuth, async (req, res) => {
    try {
        await api.registrarVenta(
            { producto_id: parseInt(req.params.id), cantidad: parseInt(req.body.cantidad) },
            req.token
        );
        res.redirect("/?ok=Venta registrada correctamente");
    } catch (error) {
        const msg = error.response?.data?.error || "No se pudo registrar la venta.";
        res.redirect(`/?error=${encodeURIComponent(msg)}`);
    }
});

app.get("/ventas", requireAuth, async (req, res) => {
    try {
        const filtros = {
            desde: req.query.desde || "",
            hasta: req.query.hasta || "",
            producto_id: req.query.producto_id || ""
        };
        const [ventasRes, meRes, productosRes] = await Promise.all([
            api.historialVentas(
                { desde: filtros.desde || undefined, hasta: filtros.hasta || undefined, producto_id: filtros.producto_id || undefined },
                req.token
            ),
            api.me(req.token),
            api.listar(req.token)
        ]);
        res.render("ventas", {
            ventas: ventasRes.data,
            usuario: meRes.data,
            productos: productosRes.data,
            filtros
        });
    } catch (error) {
        if (error.response?.status === 401) {
            res.clearCookie("token");
            return res.redirect("/login");
        }
        if (error.response?.status === 403) {
            return res.redirect("/?error=" + encodeURIComponent("No tienes permisos para ver el historial de ventas"));
        }
        res.render("ventas", { ventas: [], usuario: null, productos: [], filtros: {} });
    }
});

// ---------- Categorías (HU-06) ----------

app.get("/categorias", requireAuth, async (req, res) => {
    try {
        const [categoriasRes, meRes] = await Promise.all([
            api.listarCategorias(req.token),
            api.me(req.token)
        ]);
        res.render("categorias", {
            categorias: categoriasRes.data,
            usuario: meRes.data,
            mensaje: mensajeDesdeQuery(req)
        });
    } catch (error) {
        if (error.response?.status === 401) {
            res.clearCookie("token");
            return res.redirect("/login");
        }
        res.render("categorias", { categorias: [], usuario: null, mensaje: null });
    }
});

app.post("/categorias", requireAuth, async (req, res) => {
    try {
        await api.altaCategoria({ nombre: req.body.nombre, descripcion: req.body.descripcion }, req.token);
        res.redirect("/categorias");
    } catch (error) {
        const msg = error.response?.data?.error || "No se pudo crear la categoría.";
        res.redirect(`/categorias?error=${encodeURIComponent(msg)}`);
    }
});

app.post("/categorias/:id", requireAuth, async (req, res) => {
    try {
        await api.modificarCategoria(
            parseInt(req.params.id),
            { nombre: req.body.nombre, descripcion: req.body.descripcion },
            req.token
        );
        res.redirect("/categorias");
    } catch (error) {
        const msg = error.response?.data?.error || "No se pudo modificar la categoría.";
        res.redirect(`/categorias?error=${encodeURIComponent(msg)}`);
    }
});

app.post("/categorias/:id/eliminar", requireAuth, async (req, res) => {
    try {
        await api.bajaCategoria(parseInt(req.params.id), req.token);
        res.redirect("/categorias");
    } catch (error) {
        const msg = error.response?.data?.error || "No se pudo eliminar la categoría.";
        res.redirect(`/categorias?error=${encodeURIComponent(msg)}`);
    }
});

app.listen(3000, () => {
    console.log("Cliente corriendo en http://localhost:3000");
});
