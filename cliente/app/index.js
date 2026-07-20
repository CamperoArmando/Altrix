

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "../views"));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get("/", async (req, res) => {
    try {
        const response = await api.listar();
        res.render("index", { productos: response.data });
    } catch (error) {
        res.render("index", { productos: [] });
    }
});

app.post("/alta", async (req, res) => {
    try {
        const datos = {
            nombre: req.body.nombre,
            precio: parseFloat(req.body.precio),
            cantidad: parseInt(req.body.cantidad),
            categoria: req.body.categoria
        };
        await api.alta(datos);
    } catch (error) {
        console.error("Error en alta:", error.message);
    }
    res.redirect("/");
});

app.post("/baja/:id", async (req, res) => {
    try {
        await api.baja(parseInt(req.params.id));
    } catch (error) {
        console.error("Error en baja:", error.message);
    }
    res.redirect("/");
});

app.post("/modificar/:id", async (req, res) => {
    try {
        const datos = {
            nombre: req.body.nombre,
            precio: parseFloat(req.body.precio),
            cantidad: parseInt(req.body.cantidad),
            categoria: req.body.categoria
        };
        await api.modificar(parseInt(req.params.id), datos);
    } catch (error) {
        console.error("Error en modificar:", error.message);
    }
    res.redirect("/");
});

app.post("/vender/:id", async (req, res) => {
    try {
        await api.vender(parseInt(req.params.id), parseInt(req.body.cantidad));
    } catch (error) {
        console.error("Error en vender:", error.message);
    }
    res.redirect("/");
});

app.listen(3000, () => {
    console.log("Cliente corriendo en http://localhost:3000");
});