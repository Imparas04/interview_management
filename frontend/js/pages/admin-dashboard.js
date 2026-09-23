/* js/pages/admin-dashboard.js */
document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "admin", activePage: "dashboard", title: "Overview" });

  try {
    const d = await apiFetch("/api/analytics/overview/");
    const cards = document.querySelectorAll("#stat-grid .stat-card .value");
    const values = [d.total_candidates, d.shortlisted, d.interviews_scheduled, d.selected, d.rejected, d.pending];
    cards.forEach((el, i) => el.textContent = values[i] ?? 0);

    const deptLabels = d.department_wise_candidates.map(x => x.department);
    const deptCounts = d.department_wise_candidates.map(x => x.count);
    new Chart(document.getElementById("dept-chart"), {
      type: "bar",
      data: { labels: deptLabels, datasets: [{ label: "Candidates", data: deptCounts, backgroundColor: "#2E4374", borderRadius: 4 }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });

    new Chart(document.getElementById("status-chart"), {
      type: "doughnut",
      data: {
        labels: ["Shortlisted", "Interviews", "Selected", "Rejected", "Pending"],
        datasets: [{
          data: [d.shortlisted, d.interviews_scheduled, d.selected, d.rejected, d.pending],
          backgroundColor: ["#B8860B", "#2E6FBB", "#1F8A70", "#C1121F", "#8993A6"],
        }],
      },
      options: { responsive: true, plugins: { legend: { position: "bottom" } } },
    });
  } catch (err) {
    toastError(err);
  }
});
