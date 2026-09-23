/* js/pages/hr-applications.js */
const NEXT_STATES = {
  applied: ["ats_analysis", "rejected"],
  ats_analysis: ["shortlisted", "rejected"],
  shortlisted: ["hr_screening", "rejected"],
  hr_screening: ["technical_round", "rejected"],
  technical_round: ["coding_round", "rejected"],
  coding_round: ["managerial_round", "rejected"],
  managerial_round: ["final_hr", "rejected"],
  final_hr: ["selected", "rejected"],
  selected: [],
  rejected: [],
};
const STATUS_LABEL = {
  applied: "Applied", ats_analysis: "ATS analysis", shortlisted: "Shortlisted",
  hr_screening: "HR screening", technical_round: "Technical round", coding_round: "Coding round",
  managerial_round: "Managerial round", final_hr: "Final HR", selected: "Selected", rejected: "Rejected",
};

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "hr", activePage: "applications", title: "Applications" });
  await loadJobFilter();
  loadApplications();
  document.getElementById("filter-btn").addEventListener("click", loadApplications);
});

async function loadJobFilter() {
  try {
    const data = await apiFetch("/api/jobs/");
    const jobs = Array.isArray(data) ? data : data.results || [];
    document.getElementById("f-job").innerHTML =
      `<option value="">All jobs</option>` + jobs.map(j => `<option value="${j.id}">${escapeHtml(j.title)}</option>`).join("");
  } catch (err) { /* non-critical */ }
}

async function loadApplications() {
  const tbody = document.getElementById("app-tbody");
  tbody.innerHTML = loadingRow(6);
  const params = new URLSearchParams();
  const job = document.getElementById("f-job").value;
  const status = document.getElementById("f-status").value;
  if (job) params.set("job", job);
  if (status) params.set("status", status);
  try {
    const data = await apiFetch(`/api/applications/?${params}`);
    const list = Array.isArray(data) ? data : data.results || [];
    if (list.length === 0) {
      tbody.innerHTML = emptyRow(6, "No applications match these filters.");
      return;
    }
    tbody.innerHTML = list.map(a => {
      const next = NEXT_STATES[a.status] || [];
      const controls = next.length
        ? `<select id="next-${a.id}" style="display:inline-block; width:auto; margin-right:6px;">
             ${next.map(s => `<option value="${s}">${STATUS_LABEL[s]}</option>`).join("")}
           </select>
           <button class="btn btn-outline btn-sm" onclick="moveApplication(${a.id})">Move</button>`
        : `<span class="hint">Final stage</span>`;
      return `
        <tr>
          <td><strong>${escapeHtml(a.candidate_username)}</strong></td>
          <td>${escapeHtml(a.job_title)}</td>
          <td>${escapeHtml(a.department_name || "—")}</td>
          <td><span class="badge ${statusBadgeClass(a.status)}">${STATUS_LABEL[a.status] || a.status}</span></td>
          <td>${fmtDate(a.applied_at)}</td>
          <td>${controls}</td>
        </tr>`;
    }).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(6, "Couldn't load applications.");
    toastError(err);
  }
}

async function moveApplication(id) {
  const select = document.getElementById(`next-${id}`);
  const status = select.value;
  try {
    await apiFetch(`/api/applications/${id}/status/`, { method: "PATCH", body: { status } });
    toast(`Moved to ${STATUS_LABEL[status] || status}`, "success");
    loadApplications();
  } catch (err) {
    toastError(err);
  }
}
