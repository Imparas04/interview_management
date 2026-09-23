/* js/pages/hr-ranking.js — shared by hr/ranking.html and admin/ranking.html */
const RANK_ROLE = document.body.dataset.role;

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: RANK_ROLE, activePage: "jobs", title: "Candidate ranking" });
  await loadJobsIntoSelect();
  const preselect = new URLSearchParams(window.location.search).get("job");
  if (preselect) document.getElementById("f-job").value = preselect;
  loadRanking();
  document.getElementById("f-job").addEventListener("change", loadRanking);
});

async function loadJobsIntoSelect() {
  try {
    const data = await apiFetch("/api/jobs/");
    const jobs = Array.isArray(data) ? data : data.results || [];
    document.getElementById("f-job").innerHTML = jobs.map(j => `<option value="${j.id}">${escapeHtml(j.title)}</option>`).join("");
  } catch (err) { toastError(err); }
}

async function loadRanking() {
  const jobId = document.getElementById("f-job").value;
  const tbody = document.getElementById("rank-tbody");
  if (!jobId) { tbody.innerHTML = emptyRow(5, "No jobs available."); return; }
  tbody.innerHTML = loadingRow(5);
  try {
    const data = await apiFetch(`/api/applications/rank/?job=${jobId}`);
    const list = Array.isArray(data) ? data : data.results || [];
    if (list.length === 0) {
      tbody.innerHTML = emptyRow(5, "No ranked candidates for this job yet.");
      return;
    }
    tbody.innerHTML = list.map(r => `
      <tr>
        <td><strong>#${r.rank}</strong></td>
        <td>${escapeHtml(r.candidate)}</td>
        <td>${escapeHtml(r.department || "—")}</td>
        <td><span class="badge badge-gold">${r.ats_score}</span></td>
        <td><span class="badge ${statusBadgeClass(r.status)}">${escapeHtml((r.status || "").replace("_", " "))}</span></td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(5, "Couldn't load ranking.");
    toastError(err);
  }
}
