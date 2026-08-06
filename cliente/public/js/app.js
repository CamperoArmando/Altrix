// Filtro de búsqueda (nombre / categoría), sin recargar la página
const buscador = document.getElementById("buscador");
if (buscador) {
  buscador.addEventListener("input", () => {
    const q = buscador.value.trim().toLowerCase();
    document.querySelectorAll(".producto-row").forEach((row) => {
      const nombre = row.dataset.nombre || "";
      const categoria = row.dataset.categoria || "";
      const coincide = nombre.includes(q) || categoria.includes(q);
      row.style.display = coincide ? "" : "none";
    });
  });
}

// Abre/cierra el panel de editar + vender de cada fila
document.querySelectorAll(".toggle-panel").forEach((btn) => {
  btn.addEventListener("click", () => {
    const row = btn.closest(".producto-row");
    const panel = row.querySelector(".panel-secundario");
    panel.classList.toggle("activo");
  });
});

// Confirmación antes de eliminar
document.querySelectorAll(".form-eliminar").forEach((form) => {
  form.addEventListener("submit", (e) => {
    if (!confirm("¿Eliminar este producto? Podrás seguir viéndolo en ventas anteriores, pero dejará de aparecer en el catálogo.")) {
      e.preventDefault();
    }
  });
});
