/* js/pages/admin-analytics.js */
document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "admin", activePage: "analytics", title: "Analytics" });
  try {
    const d = await apiFetch("/api/analytics/overview/");

    new Chart(document.getElementById("dept-bar"), {
      type: "bar",
      data: {
        labels: d.department_wise_candidates.map(x => x.department),
        datasets: [{ label: "Candidates", data: d.department_wise_candidates.map(x => x.count), backgroundColor: "#2E4374", borderRadius: 4 }],
      },
      options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } },
    });

    new Chart(document.getElementById("funnel-chart"), {
      type: "bar",
      data: {
        labels: ["Total", "Shortlisted", "Interviews", "Selected", "Rejected", "Pending"],
        datasets: [{
          data: [d.total_candidates, d.shortlisted, d.interviews_scheduled, d.selected, d.rejected, d.pending],
          backgroundColor: ["#2E4374", "#B8860B", "#2E6FBB", "#1F8A70", "#C1121F", "#8993A6"],
          borderRadius: 4,
        }],
      },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });

    document.getElementById("dept-tbody").innerHTML = d.department_wise_candidates.map(x => `
      <tr><td>${escapeHtml(x.department)}</td><td>${x.count}</td></tr>`).join("") || emptyRow(2);
  } catch (err) {
    toastError(err);
  }
});
