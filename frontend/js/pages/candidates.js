/* js/pages/candidates.js — shared by admin/candidates.html and hr/candidates.html */
const CAND_ROLE = document.body.dataset.role;

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: CAND_ROLE, activePage: "candidates", title: "Candidates" });
  await loadDeptFilter();
  loadCandidates();

  document.getElementById("search-btn").addEventListener("click", loadCandidates);
  document.getElementById("clear-btn").addEventListener("click", () => {
    ["f-name", "f-email", "f-skill", "f-min-ats"].forEach(id => document.getElementById(id).value = "");
    document.getElementById("f-department").value = "";
    document.getElementById("f-app-status").value = "";
    loadCandidates();
  });
});

async function loadDeptFilter() {
  try {
    const data = await apiFetch("/api/departments/");
    const depts = Array.isArray(data) ? data : data.results || [];
    document.getElementById("f-department").innerHTML =
      `<option value="">Any</option>` + depts.map(d => `<option value="${d.id}">${escapeHtml(d.name)}</option>`).join("");
  } catch (err) { /* non-critical */ }
}

function buildCandQuery() {
  const params = new URLSearchParams();
  const name = document.getElementById("f-name").value.trim();
  const email = document.getElementById("f-email").value.trim();
  const skill = document.getElementById("f-skill").value.trim();
  const dept = document.getElementById("f-department").value;
  const minAts = document.getElementById("f-min-ats").value;
  const appStatus = document.getElementById("f-app-status").value;
  if (name) params.set("name", name);
  if (email) params.set("email", email);
  if (skill) params.set("skill", skill);
  if (dept) params.set("department", dept);
  if (minAts) params.set("min_ats_score", minAts);
  if (appStatus) params.set("application_status", appStatus);
  return params;
}

async function loadCandidates() {
  const tbody = document.getElementById("cand-tbody");
  tbody.innerHTML = loadingRow(6);
  const params = buildCandQuery();
  const usingSearch = [...params.keys()].length > 0;
  try {
    const data = await apiFetch(usingSearch ? `/api/candidates/search/?${params}` : "/api/candidates/");
    const list = Array.isArray(data) ? data : data.results || [];
    if (list.length === 0) {
      tbody.innerHTML = emptyRow(6, "No candidates match.");
      return;
    }
    tbody.innerHTML = list.map(c => `
      <tr>
        <td><strong>${escapeHtml(c.user?.username || c.username || "—")}</strong></td>
        <td>${escapeHtml(c.user?.email || c.email || "—")}</td>
        <td>${escapeHtml(c.phone || "—")}</td>
        <td>${escapeHtml(c.recommended_department_name || "—")}</td>
        <td>${c.recommended_department_confidence != null ? c.recommended_department_confidence + "%" : "—"}</td>
        <td><a class="btn btn-ghost btn-sm" href="candidate-detail.html?id=${c.id}">View</a></td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(6, "Couldn't load candidates.");
    toastError(err);
  }
}
