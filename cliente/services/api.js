const axios = require("axios");

// En Docker, el cliente debe llamar al servidor por su nombre de servicio
// ("servidor"), no por localhost. Fuera de Docker sigue apuntando a localhost.
const BASE_URL = process.env.API_URL || "http://localhost:5000";

// El token viaja por parámetro (no como variable global) porque este
// mismo proceso Node atiende a varios usuarios con sesiones distintas.
function authHeader(token) {
    return token ? { Authorization: `Bearer ${token}` } : {};
}

const api = {
    login: (email, password) => axios.post(`${BASE_URL}/auth/login`, { email, password }),
    me: (token) => axios.get(`${BASE_URL}/auth/me`, { headers: authHeader(token) }),

    // Productos
    listar: (token) => axios.get(`${BASE_URL}/productos`, { headers: authHeader(token) }),
    consultar: (id, token) => axios.get(`${BASE_URL}/productos/${id}`, { headers: authHeader(token) }),
    alta: (datos, token) => axios.post(`${BASE_URL}/productos`, datos, { headers: authHeader(token) }),
    baja: (id, token) => axios.delete(`${BASE_URL}/productos/${id}`, { headers: authHeader(token) }),
    modificar: (id, datos, token) => axios.put(`${BASE_URL}/productos/${id}`, datos, { headers: authHeader(token) }),

    // Categorías (HU-06)
    listarCategorias: (token) => axios.get(`${BASE_URL}/categorias`, { headers: authHeader(token) }),
    altaCategoria: (datos, token) => axios.post(`${BASE_URL}/categorias`, datos, { headers: authHeader(token) }),
    modificarCategoria: (id, datos, token) => axios.put(`${BASE_URL}/categorias/${id}`, datos, { headers: authHeader(token) }),
    bajaCategoria: (id, token) => axios.delete(`${BASE_URL}/categorias/${id}`, { headers: authHeader(token) }),

    // Ventas (HU-05, HU-09)
    registrarVenta: (datos, token) => axios.post(`${BASE_URL}/ventas`, datos, { headers: authHeader(token) }),
    historialVentas: (params, token) => axios.get(`${BASE_URL}/ventas`, { params, headers: authHeader(token) })
};

module.exports = api;
