/* js/pages/candidate-dashboard.js */
document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "candidate", activePage: "dashboard", title: "Dashboard" });
  const user = getUser();
  document.getElementById("welcome-head").textContent = `Welcome back, ${user.username}`;

  try {
    const summary = await apiFetch("/api/analytics/candidate-summary/");
    const cards = document.querySelectorAll("#stat-grid .stat-card .value");
    const values = [summary.applied_jobs, summary.shortlisted, summary.interviews, summary.completed_interviews];
    cards.forEach((el, i) => el.textContent = values[i] ?? 0);
  } catch (err) { toastError(err); }

  const tbody = document.getElementById("app-tbody");
  tbody.innerHTML = loadingRow(4);
  try {
    const data = await apiFetch("/api/applications/");
    const list = (Array.isArray(data) ? data : data.results || []).slice(0, 5);
    if (list.length === 0) {
      tbody.innerHTML = emptyRow(4, "You haven't applied to any jobs yet.");
      return;
    }
    tbody.innerHTML = list.map(a => `
      <tr>
        <td><strong>${escapeHtml(a.job_title)}</strong></td>
        <td>${escapeHtml(a.department_name || "—")}</td>
        <td><span class="badge ${statusBadgeClass(a.status)}">${escapeHtml(a.status.replace("_", " "))}</span></td>
        <td>${fmtDate(a.applied_at)}</td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(4, "Couldn't load applications.");
  }
});
