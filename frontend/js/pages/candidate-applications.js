/* js/pages/candidate-applications.js */
document.addEventListener("DOMContentLoaded", () => {
  renderShell({ role: "candidate", activePage: "applications", title: "My applications" });
  loadApplications();
});

async function loadApplications() {
  const tbody = document.getElementById("app-tbody");
  tbody.innerHTML = loadingRow(5);
  try {
    const data = await apiFetch("/api/applications/");
    const list = Array.isArray(data) ? data : data.results || [];
    if (list.length === 0) {
      tbody.innerHTML = emptyRow(5, "You haven't applied to any jobs yet — browse open jobs to get started.");
      return;
    }
    tbody.innerHTML = list.map(a => `
      <tr>
        <td><strong>${escapeHtml(a.job_title)}</strong></td>
        <td>${escapeHtml(a.department_name || "—")}</td>
        <td><span class="badge ${statusBadgeClass(a.status)}">${escapeHtml(a.status.replace("_", " "))}</span></td>
        <td>${fmtDate(a.applied_at)}</td>
        <td>${fmtDate(a.updated_at)}</td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(5, "Couldn't load your applications.");
    toastError(err);
  }
}
