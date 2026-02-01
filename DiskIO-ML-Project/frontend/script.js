// --- CHART INITIALIZATION ---
const MAX_DATA_POINTS = 20;
let labels = [];

// common options for smooth updates
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 500 },
  scales: {
    x: { display: false },
    y: { beginAtZero: true }
  },
  elements: {
    line: { tension: 0.4 }, // smooth lines
    point: { radius: 2 }
  }
};

const diskIOChart = new Chart(document.getElementById("diskIOChart"), {
  type: "line",
  data: {
    labels: labels,
    datasets: [
      { label: "Read Bytes", borderColor: "#3498db", data: [], fill: false },
      { label: "Write Bytes", borderColor: "#e67e22", data: [], fill: false }
    ]
  },
  options: chartOptions
});

const systemUsageChart = new Chart(document.getElementById("systemUsageChart"), {
  type: "line",
  data: {
    labels: labels,
    datasets: [
      { label: "CPU Usage %", borderColor: "#e74c3c", data: [], fill: false },
      { label: "Memory Usage %", borderColor: "#2ecc71", data: [], fill: false }
    ]
  },
  options: chartOptions
});

const predictionChart = new Chart(document.getElementById("predictionChart"), {
  type: "line",
  data: {
    labels: labels,
    datasets: [
      { label: "Predicted Load (MB)", borderColor: "#9b59b6", data: [], fill: true, backgroundColor: "rgba(155, 89, 182, 0.1)" }
    ]
  },
  options: chartOptions
});

async function loadData() {
  try {
    const res = await fetch("http://127.0.0.1:8000/metrics");

    if (!res.ok) throw new Error("API not responding");

    const data = await res.json();

    // ✅ Safety checks
    const getValue = (val, suffix = "") => (val !== undefined && val !== null) ? val + suffix : "--";

    document.getElementById("read").innerText = getValue(data.read_bytes, " B");
    document.getElementById("write").innerText = getValue(data.write_bytes, " B");
    document.getElementById("cpu").innerText = getValue(data.cpu_usage, " %");
    document.getElementById("memory").innerText = getValue(data.memory_usage, " %");
    document.getElementById("prediction").innerText = getValue(data.predicted_disk_load_mb, " MB");

    const statusEl = document.getElementById("status");
    const statusVal = data.status || "--";
    statusEl.innerText = statusVal;

    // ✅ Status color logic
    if (statusVal === "NORMAL") {
      statusEl.style.color = "white";
      statusEl.style.backgroundColor = "#2ecc71";
    } else if (statusVal === "WARNING") {
      statusEl.style.color = "white";
      statusEl.style.backgroundColor = "#f39c12";
    } else if (statusVal === "CRITICAL") {
      statusEl.style.color = "white";
      statusEl.style.backgroundColor = "#e74c3c";
    } else {
      statusEl.style.color = "white";
      statusEl.style.backgroundColor = "grey";
    }

    // --- CHART UPDATE LOGIC ---
    const now = new Date().toLocaleTimeString();

    // Add new values
    labels.push(now);
    diskIOChart.data.datasets[0].data.push(data.read_bytes);
    diskIOChart.data.datasets[1].data.push(data.write_bytes);
    systemUsageChart.data.datasets[0].data.push(data.cpu_usage);
    systemUsageChart.data.datasets[1].data.push(data.memory_usage);
    predictionChart.data.datasets[0].data.push(data.predicted_disk_load_mb);

    // Keep last 20 points
    if (labels.length > MAX_DATA_POINTS) {
      labels.shift();
      diskIOChart.data.datasets[0].data.shift();
      diskIOChart.data.datasets[1].data.shift();
      systemUsageChart.data.datasets[0].data.shift();
      systemUsageChart.data.datasets[1].data.shift();
      predictionChart.data.datasets[0].data.shift();
    }

    diskIOChart.update('none'); // Update without full animation for performance
    systemUsageChart.update('none');
    predictionChart.update('none');

    console.log("Chart update:", data);

  } catch (err) {
    console.error("Error fetching data:", err);
    ["read", "write", "cpu", "memory", "prediction", "status"].forEach(id => {
      document.getElementById(id).innerText = "--";
    });
  }
}

// Initial fetch and interval
loadData();
setInterval(loadData, 1000);


