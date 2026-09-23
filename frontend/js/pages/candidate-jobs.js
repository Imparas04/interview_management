/* js/pages/candidate-jobs.js */
let applyJobId = null;

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "candidate", activePage: "jobs", title: "Browse jobs" });
  await loadDeptFilter();
  loadJobs();
  document.getElementById("filter-btn").addEventListener("click", loadJobs);
  document.getElementById("apply-submit-btn").addEventListener("click", submitApplication);
});

async function loadDeptFilter() {
  try {
    const data = await apiFetch("/api/departments/");
    const depts = Array.isArray(data) ? data : data.results || [];
    document.getElementById("f-department").innerHTML =
      `<option value="">All</option>` + depts.map(d => `<option value="${d.id}">${escapeHtml(d.name)}</option>`).join("");
  } catch (err) { /* non-critical */ }
}

async function loadJobs() {
  const wrap = document.getElementById("jobs-list");
  wrap.innerHTML = `<div class="loading-row"><span class="spinner"></span>Loading…</div>`;
  const params = new URLSearchParams();
  const dep = document.getElementById("f-department").value;
  const search = document.getElementById("f-search").value.trim();
  if (dep) params.set("department", dep);
  if (search) params.set("search", search);
  try {
    const data = await apiFetch(`/api/jobs/?${params}`); // backend already scopes candidates to status=open
    const jobs = Array.isArray(data) ? data : data.results || [];
    if (jobs.length === 0) {
      wrap.innerHTML = `<div class="card">No open jobs match these filters right now.</div>`;
      return;
    }
    wrap.innerHTML = jobs.map(j => `
      <div class="card" style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap;">
          <div>
            <h3 style="margin-bottom:4px;">${escapeHtml(j.title)}</h3>
            <p class="hint" style="margin-bottom:8px;">${escapeHtml(j.department_name || "—")} · ${escapeHtml((j.job_type || "").replace("_", " "))} · ${escapeHtml(j.location || "Location N/A")}</p>
          </div>
          <button class="btn btn-primary btn-sm" style="height:fit-content;" onclick="openApplyModal(${j.id}, '${escapeHtml(j.title).replace(/'/g, "\\'")}')">Apply</button>
        </div>
        <p>${escapeHtml((j.description || "").slice(0, 220))}${(j.description || "").length > 220 ? "…" : ""}</p>
        <p class="hint">Deadline: ${fmtDate(j.application_deadline)} · Openings: ${j.num_openings} · Experience: ${j.experience_min}-${j.experience_max} yrs</p>
      </div>`).join("");
  } catch (err) {
    wrap.innerHTML = `<div class="card">Couldn't load jobs.</div>`;
    toastError(err);
  }
}

async function openApplyModal(jobId, title) {
  applyJobId = jobId;
  hideFormError("apply-error");
  document.getElementById("apply-modal-title").textContent = `Apply — ${title}`;
  try {
    const data = await apiFetch("/api/resumes/");
    const list = Array.isArray(data) ? data : data.results || [];
    document.getElementById("apply-resume").innerHTML = list.length
      ? list.map(r => `<option value="${r.id}">${escapeHtml(r.original_filename)}</option>`).join("")
      : `<option value="">No resume uploaded</option>`;
  } catch (err) { toastError(err); }
  openModal("apply-modal");
}

async function submitApplication() {
  hideFormError("apply-error");
  const resumeId = document.getElementById("apply-resume").value;
  if (!resumeId) {
    showFormError("apply-error", { message: "Upload a resume before applying." });
    return;
  }
  const btn = document.getElementById("apply-submit-btn");
  btn.disabled = true;
  try {
    await apiFetch("/api/applications/", { method: "POST", body: { job: applyJobId, resume: Number(resumeId) } });
    toast("Application submitted", "success");
    closeModal("apply-modal");
  } catch (err) {
    // Backend returns 400 for a duplicate application to the same job — message surfaces that.
    showFormError("apply-error", err);
  } finally {
    btn.disabled = false;
  }
}
