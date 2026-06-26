function showTab(type) {
  const tabs = ['standard', 'fuzzy', 'charts'];
  tabs.forEach(t => {
    const contentEl = document.getElementById(t === 'standard' || t === 'fuzzy' ? 'form-' + t : 'content-' + t);
    const tabEl = document.getElementById('tab-' + t);
    if (t === type) {
      if (contentEl) {
        contentEl.style.display = (t === 'standard') ? 'flex' : 'block';
      }
      if (tabEl) {
        tabEl.classList.add('active-tab');
      }
    } else {
      if (contentEl) {
        contentEl.style.display = 'none';
      }
      if (tabEl) {
        tabEl.classList.remove('active-tab');
      }
    }
  });
}

// Data koordinat kurva fuzzy
const chartDataSets = {
  bug: {
    title: "Kepadatan Bug / Jam",
    datasets: [
      {
        label: "Sangat Bersih",
        data: [{x: 0, y: 1}, {x: 1, y: 1}, {x: 3, y: 0}],
        borderColor: "#66c0f4",
        backgroundColor: "rgba(102, 192, 244, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Wajar",
        data: [{x: 2, y: 0}, {x: 4, y: 1}, {x: 6, y: 1}, {x: 8, y: 0}],
        borderColor: "#eb9928",
        backgroundColor: "rgba(235, 153, 40, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Rusak",
        data: [{x: 7, y: 0}, {x: 9, y: 1}, {x: 15, y: 1}],
        borderColor: "#e35b5b",
        backgroundColor: "rgba(227, 91, 91, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      }
    ]
  },
  fps: {
    title: "Rata-rata FPS",
    datasets: [
      {
        label: "Patah-patah",
        data: [{x: 0, y: 1}, {x: 20, y: 1}, {x: 30, y: 0}],
        borderColor: "#e35b5b",
        backgroundColor: "rgba(227, 91, 91, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Stabil",
        data: [{x: 20, y: 0}, {x: 30, y: 1}, {x: 45, y: 1}, {x: 55, y: 0}],
        borderColor: "#eb9928",
        backgroundColor: "rgba(235, 153, 40, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Lancar",
        data: [{x: 45, y: 0}, {x: 60, y: 1}, {x: 120, y: 1}],
        borderColor: "#66c0f4",
        backgroundColor: "rgba(102, 192, 244, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      }
    ]
  },
  wish: {
    title: "Jumlah Wishlist",
    datasets: [
      {
        label: "Sedikit",
        data: [{x: 0, y: 1}, {x: 4000, y: 1}, {x: 6000, y: 0}],
        borderColor: "#e35b5b",
        backgroundColor: "rgba(227, 91, 91, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Menjanjikan",
        data: [{x: 4000, y: 0}, {x: 10000, y: 1}, {x: 15000, y: 1}, {x: 22000, y: 0}],
        borderColor: "#eb9928",
        backgroundColor: "rgba(235, 153, 40, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Meledak",
        data: [{x: 18000, y: 0}, {x: 25000, y: 1}, {x: 50000, y: 1}],
        borderColor: "#66c0f4",
        backgroundColor: "rgba(102, 192, 244, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      }
    ]
  },
  budget: {
    title: "Sisa Anggaran (%)",
    datasets: [
      {
        label: "Kritis",
        data: [{x: 0, y: 1}, {x: 8, y: 1}, {x: 12, y: 0}],
        borderColor: "#e35b5b",
        backgroundColor: "rgba(227, 91, 91, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Aman",
        data: [{x: 8, y: 0}, {x: 15, y: 1}, {x: 35, y: 1}, {x: 45, y: 0}],
        borderColor: "#eb9928",
        backgroundColor: "rgba(235, 153, 40, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Melimpah",
        data: [{x: 35, y: 0}, {x: 45, y: 1}, {x: 100, y: 1}],
        borderColor: "#66c0f4",
        backgroundColor: "rgba(102, 192, 244, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      }
    ]
  },
  quality: {
    title: "Kualitas Kelayakan Rilis (Output)",
    datasets: [
      {
        label: "Tunda",
        data: [{x: 0, y: 1}, {x: 35, y: 1}, {x: 45, y: 0}],
        borderColor: "#e35b5b",
        backgroundColor: "rgba(227, 91, 91, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Akses Awal",
        data: [{x: 35, y: 0}, {x: 50, y: 1}, {x: 65, y: 1}, {x: 80, y: 0}],
        borderColor: "#eb9928",
        backgroundColor: "rgba(235, 153, 40, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      },
      {
        label: "Siap Rilis",
        data: [{x: 70, y: 0}, {x: 85, y: 1}, {x: 100, y: 1}],
        borderColor: "#a4d007",
        backgroundColor: "rgba(164, 208, 7, 0.15)",
        borderWidth: 2,
        fill: true,
        tension: 0
      }
    ]
  }
};

let myChart;

function initFuzzyChart() {
  const chartCanvas = document.getElementById('fuzzyChart');
  if (!chartCanvas) return; // Guard jika elemen belum ada di DOM

  const ctx = chartCanvas.getContext('2d');
  myChart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: chartDataSets.bug.datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: chartDataSets.bug.title,
          color: '#c7d5e0',
          font: {
            family: 'Inter',
            size: 14,
            weight: 'bold'
          }
        },
        legend: {
          labels: {
            color: '#8f98a0',
            font: {
              family: 'Inter',
              size: 11
            }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': (x: ' + context.parsed.x + ', μ: ' + context.parsed.y.toFixed(2) + ')';
            }
          }
        }
      },
      scales: {
        x: {
          type: 'linear',
          position: 'bottom',
          grid: {
            color: 'rgba(255, 255, 255, 0.05)'
          },
          ticks: {
            color: '#8f98a0',
            font: {
              family: 'Inter',
              size: 10
            }
          }
        },
        y: {
          min: 0,
          max: 1.1,
          grid: {
            color: 'rgba(255, 255, 255, 0.05)'
          },
          ticks: {
            color: '#8f98a0',
            stepSize: 0.2,
            font: {
              family: 'Inter',
              size: 10
            }
          },
          title: {
            display: true,
            text: 'Derajat Keanggotaan (μ)',
            color: '#8f98a0',
            font: {
              family: 'Inter',
              size: 10
            }
          }
        }
      }
    }
  });
}

function switchChart(variable) {
  if (!myChart) return;
  const tabs = ['bug', 'fps', 'wish', 'budget', 'quality'];
  tabs.forEach(t => {
    const btn = document.getElementById('btn-chart-' + t);
    if (btn) {
      if (t === variable) {
        btn.classList.add('active-chart-tab');
      } else {
        btn.classList.remove('active-chart-tab');
      }
    }
  });

  myChart.data.datasets = chartDataSets[variable].datasets;
  myChart.options.plugins.title.text = chartDataSets[variable].title;
  myChart.update();
}

document.addEventListener("DOMContentLoaded", function() {
  initFuzzyChart();
});
