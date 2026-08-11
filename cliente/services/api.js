const axios = require("axios");

// URLs de los servicios REST publicados en producción.
// Servicio 1: API principal Flask — desplegado en Railway
// https://altrix-production-421e.up.railway.app
// Servicio 2: Microservicio de alertas Go — desplegado en Render
// https://altrix-alertas-go.onrender.com
//
// En producción estas URLs llegan por variable de entorno (configuradas en
// Railway). En desarrollo local se usan los valores por defecto (localhost).
const BASE_URL = process.env.API_URL || "https://altrix-production-421e.up.railway.app";
const ALERTAS_URL = process.env.ALERTAS_URL || "https://altrix-alertas-go.onrender.com";

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
    historialVentas: (params, token) => axios.get(`${BASE_URL}/ventas`, { params, headers: authHeader(token) }),

    // Alertas de stock — microservicio en Go (segundo lenguaje de backend)
    alertasStock: (token) => axios.get(`${ALERTAS_URL}/alertas/stock-bajo`, { headers: authHeader(token) })
};

module.exports = api;