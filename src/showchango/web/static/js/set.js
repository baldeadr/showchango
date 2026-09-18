document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("curva-canvas");
  const lista = document.getElementById("lista-pistas");
  if (!canvas || !lista) return;

  const ctx = canvas.getContext("2d");
  const datos = window.__CURVA_INICIAL__;

  const chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: datos.etiquetas,
      datasets: [
        {
          label: "Energía",
          data: datos.energia,
          borderColor: "#ff6b35",
          backgroundColor: "rgba(255, 107, 53, 0.2)",
          stepped: "after",
          tension: 0,
          fill: true,
        },
        {
          label: "Bailabilidad",
          data: datos.bailabilidad,
          borderColor: "#4dd0a1",
          backgroundColor: "rgba(77, 208, 161, 0.2)",
          stepped: "after",
          tension: 0,
          fill: true,
          hidden: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0,
          max: 1,
          grid: { color: "#2a2a30" },
          ticks: { color: "#999" },
        },
        x: {
          grid: { color: "#2a2a30" },
          ticks: { color: "#999" },
        },
      },
      plugins: {
        legend: { labels: { color: "#e6e6e6" } },
      },
    },
  });

  Sortable.create(lista, {
    animation: 150,
    handle: ".handle",
    onEnd: () => {
      const orden = Array.from(lista.children).map((li) => li.dataset.id);
      fetch("/set/reordenar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ orden }),
      })
        .then((r) => {
          if (!r.ok) throw new Error("Error al reordenar");
          return r.json();
        })
        .then((nuevosDatos) => {
          chart.data.labels = nuevosDatos.etiquetas;
          chart.data.datasets[0].data = nuevosDatos.energia;
          chart.data.datasets[1].data = nuevosDatos.bailabilidad;
          chart.update();
        })
        .catch((err) => {
          console.error(err);
          alert("No se pudo guardar el nuevo orden.");
        });
    },
  });
});
