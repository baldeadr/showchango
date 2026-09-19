document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("curva-canvas");
  const lista = document.getElementById("lista-pistas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const datos = window.__CURVA_INICIAL__;

  function formatearMinutos(minutos) {
    const m = Math.floor(minutos);
    const s = Math.floor((minutos - m) * 60)
      .toString()
      .padStart(2, "0");
    return `${m}:${s}`;
  }

  const maxTiempo = datos.tiempos_min.length > 0
    ? Math.max(...datos.tiempos_min, 1)
    : 1;

  const chart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          label: "Energía",
          data: datos.puntos_energia,
          borderColor: "#ff6b35",
          backgroundColor: "rgba(255, 107, 53, 0.2)",
          stepped: "after",
          tension: 0,
          fill: true,
        },
        {
          label: "Bailabilidad",
          data: datos.puntos_bailabilidad,
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
      parsing: false,
      scales: {
        y: {
          min: 0,
          max: 1,
          grid: { color: "#2a2a30" },
          ticks: { color: "#999" },
        },
        x: {
          type: "linear",
          min: 0,
          max: maxTiempo,
          title: { display: true, text: "Tiempo del show", color: "#999" },
          grid: { color: "#2a2a30" },
          ticks: {
            color: "#999",
            callback: (valor) => formatearMinutos(valor),
          },
        },
      },
      plugins: {
        legend: { labels: { color: "#e6e6e6" } },
        tooltip: {
          callbacks: {
            title: (items) => {
              const idx = items[0]?.dataIndex;
              return idx !== undefined ? datos.titulos[idx] : "";
            },
          },
        },
      },
    },
  });

  if (!lista) return;

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
          datos.titulos = nuevosDatos.titulos;
          datos.tiempos_min = nuevosDatos.tiempos_min;
          chart.data.datasets[0].data = nuevosDatos.puntos_energia;
          chart.data.datasets[1].data = nuevosDatos.puntos_bailabilidad;
          chart.options.scales.x.max = nuevosDatos.tiempos_min.length > 0
            ? Math.max(...nuevosDatos.tiempos_min, 1)
            : 1;
          chart.update();
        })
        .catch((err) => {
          console.error(err);
          alert("No se pudo guardar el nuevo orden.");
        });
    },
  });
});
