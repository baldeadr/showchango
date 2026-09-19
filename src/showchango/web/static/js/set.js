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

  const maxTiempo = datos.puntos_energia.length > 0
    ? Math.max(...datos.puntos_energia.map((p) => p.x), 1)
    : 1;

  const chart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          label: "Energía",
          data: datos.puntos_energia,
          pointRadius: 0,
          borderColor: "#ff6b35",
          backgroundColor: "rgba(255, 107, 53, 0.2)",
          stepped: "before",
          tension: 0,
          fill: true,
        },
        {
          label: "Energía",
          type: "scatter",
          data: datos.marcadores_energia,
          pointRadius: 5,
          pointBackgroundColor: "#ff6b35",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
        },
        {
          label: "Bailabilidad",
          data: datos.puntos_bailabilidad,
          pointRadius: 0,
          borderColor: "#4dd0a1",
          backgroundColor: "rgba(77, 208, 161, 0.2)",
          stepped: "before",
          tension: 0,
          fill: true,
          hidden: true,
        },
        {
          label: "Bailabilidad",
          type: "scatter",
          data: datos.marcadores_bailabilidad,
          pointRadius: 5,
          pointBackgroundColor: "#4dd0a1",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
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
          filter: (item) => item.dataset.type === "scatter",
          callbacks: {
            title: (items) => {
              const idx = items[0]?.dataIndex;
              return idx !== undefined ? datos.titulos[idx] : "";
            },
            label: (item) => {
              const idx = item.dataIndex;
              const duracionS = datos.duraciones_s[idx];
              const lineas = [`${item.dataset.label}: ${item.parsed.y}`];
              if (duracionS !== undefined) {
                const m = Math.floor(duracionS / 60);
                const s = Math.floor(duracionS % 60)
                  .toString()
                  .padStart(2, "0");
                lineas.push(`Duración: ${m}:${s}`);
              }
              return lineas;
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
          datos.duraciones_s = nuevosDatos.duraciones_s;
          chart.data.datasets[0].data = nuevosDatos.puntos_energia;
          chart.data.datasets[1].data = nuevosDatos.marcadores_energia;
          chart.data.datasets[2].data = nuevosDatos.puntos_bailabilidad;
          chart.data.datasets[3].data = nuevosDatos.marcadores_bailabilidad;
          chart.options.scales.x.max = nuevosDatos.puntos_energia.length > 0
            ? Math.max(...nuevosDatos.puntos_energia.map((p) => p.x), 1)
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
