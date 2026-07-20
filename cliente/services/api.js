const axios = require("axios");

// En Docker, el cliente debe llamar al servidor por su nombre de servicio
// ("servidor"), no por localhost. Fuera de Docker sigue apuntando a localhost.
const BASE_URL = process.env.API_URL || "http://localhost:5000";

const api = {
    listar: () => axios.get(`${BASE_URL}/productos`),
    consultar: (id) => axios.get(`${BASE_URL}/productos/${id}`),
    alta: (datos) => axios.post(`${BASE_URL}/productos`, datos),
    baja: (id) => axios.delete(`${BASE_URL}/productos/${id}`),
    modificar: (id, datos) => axios.put(`${BASE_URL}/productos/${id}`, datos),
    vender: (id, cantidad) => axios.put(`${BASE_URL}/productos/${id}/vender`, { cantidad })
};

module.exports = api;