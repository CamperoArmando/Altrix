// Servicio de alertas de stock (Go).
//
// Segundo lenguaje de backend del proyecto Altrix, junto al servidor
// principal en Python/Flask. Este servicio NO se conecta directo a la
// base de datos: consume la API REST de Flask (GET /productos) y calcula
// qué productos están en o por debajo de su stock mínimo. El token JWT
// que manda el cliente se reenvía tal cual a Flask, así que la
// autenticación/autorización real la sigue resolviendo un solo lugar
// (el servidor Python) y no hay que duplicar la lógica de JWT aquí.
package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

// Debe coincidir con lo que expone Producto.get_info() en el servidor Flask.
type Producto struct {
	ID          int     `json:"id"`
	Nombre      string  `json:"nombre"`
	Precio      float64 `json:"precio"`
	Cantidad    int     `json:"cantidad"`
	Categoria   string  `json:"categoria"`
	StockMinimo int     `json:"stock_minimo"`
	Activo      bool    `json:"activo"`
}

type Alerta struct {
	Producto
	Faltante int    `json:"faltante"` // cuánto falta para llegar al stock mínimo
	Nivel    string `json:"nivel"`    // "agotado" | "critico"
}

type RespuestaAlertas struct {
	Total   int      `json:"total"`
	Alertas []Alerta `json:"alertas"`
}

type ErrorResp struct {
	Error string `json:"error"`
}

var flaskURL string
var httpClient = &http.Client{Timeout: 8 * time.Second}

func main() {
	flaskURL = os.Getenv("FLASK_URL")
	if flaskURL == "" {
		flaskURL = "http://servidor:5000"
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/health", handlerHealth)
	mux.HandleFunc("/alertas/stock-bajo", handlerAlertasStock)

	puerto := os.Getenv("PORT")
	if puerto == "" {
		puerto = "5001"
	}

	log.Printf("Servicio de alertas (Go) escuchando en :%s — consultando Flask en %s", puerto, flaskURL)
	if err := http.ListenAndServe(":"+puerto, mux); err != nil {
		log.Fatal(err)
	}
}

func handlerHealth(w http.ResponseWriter, r *http.Request) {
	responderJSON(w, http.StatusOK, map[string]string{"status": "ok", "servicio": "alertas-go"})
}

func handlerAlertasStock(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		responderJSON(w, http.StatusMethodNotAllowed, ErrorResp{Error: "Método no permitido"})
		return
	}

	auth := r.Header.Get("Authorization")
	if auth == "" {
		responderJSON(w, http.StatusUnauthorized, ErrorResp{Error: "No autenticado"})
		return
	}

	productos, status, err := obtenerProductos(auth)
	if err != nil {
		responderJSON(w, http.StatusBadGateway, ErrorResp{Error: "No se pudo consultar el servidor de productos: " + err.Error()})
		return
	}
	if status != http.StatusOK {
		// Propaga tal cual el 401/403 (u otro error) que haya dado Flask.
		responderJSON(w, status, ErrorResp{Error: "El servidor de productos respondió " + strconv.Itoa(status)})
		return
	}

	alertas := calcularAlertas(productos)
	responderJSON(w, http.StatusOK, RespuestaAlertas{Total: len(alertas), Alertas: alertas})
}

func obtenerProductos(authHeader string) ([]Producto, int, error) {
	req, err := http.NewRequest(http.MethodGet, flaskURL+"/productos", nil)
	if err != nil {
		return nil, 0, err
	}
	req.Header.Set("Authorization", authHeader)

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, resp.StatusCode, nil
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, 0, err
	}

	var productos []Producto
	if err := json.Unmarshal(body, &productos); err != nil {
		return nil, 0, err
	}
	return productos, http.StatusOK, nil
}

func calcularAlertas(productos []Producto) []Alerta {
	alertas := make([]Alerta, 0)
	for _, p := range productos {
		if !p.Activo {
			continue
		}
		minimo := p.StockMinimo
		if minimo <= 0 {
			minimo = 5 // mismo default que el modelo Producto en Flask
		}
		if p.Cantidad > minimo {
			continue
		}
		nivel := "critico"
		if p.Cantidad == 0 {
			nivel = "agotado"
		}
		alertas = append(alertas, Alerta{
			Producto: p,
			Faltante: minimo - p.Cantidad,
			Nivel:    nivel,
		})
	}
	return alertas
}

func responderJSON(w http.ResponseWriter, status int, cuerpo interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(cuerpo)
}
