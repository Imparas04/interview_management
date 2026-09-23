/* js/pages/jobs.js — shared by admin/jobs.html and hr/jobs.html */
const JOB_ROLE = document.body.dataset.role;
let jobsCache = [];
let deptCache = [];
let skillDraft = []; // [{skill_name, weight}]

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: JOB_ROLE, activePage: "jobs", title: "Jobs" });
  await loadDepartmentsIntoSelects();
  loadJobs();

  document.getElementById("add-btn").addEventListener("click", () => openJobModal(null));
  document.getElementById("job-modal-close").addEventListener("click", () => closeModal("job-modal"));
  document.getElementById("job-cancel-btn").addEventListener("click", () => closeModal("job-modal"));
  document.getElementById("job-form").addEventListener("submit", saveJob);
  document.getElementById("add-skill-btn").addEventListener("click", addSkillToDraft);
  document.getElementById("filter-btn").addEventListener("click", loadJobs);
});

async function loadDepartmentsIntoSelects() {
  try {
    const data = await apiFetch("/api/departments/");
    deptCache = Array.isArray(data) ? data : data.results || [];
    const opts = deptCache.map(d => `<option value="${d.id}">${escapeHtml(d.name)}</option>`).join("");
    document.getElementById("job-department").innerHTML = opts;
    document.getElementById("f-department").innerHTML = `<option value="">All</option>${opts}`;
  } catch (err) { toastError(err); }
}

function buildQuery() {
  const params = new URLSearchParams();
  const dep = document.getElementById("f-department").value;
  const status = document.getElementById("f-status").value;
  const search = document.getElementById("f-search").value.trim();
  if (dep) params.set("department", dep);
  if (status) params.set("status", status);
  if (search) params.set("search", search);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

async function loadJobs() {
  const tbody = document.getElementById("job-tbody");
  tbody.innerHTML = loadingRow(7);
  try {
    const data = await apiFetch(`/api/jobs/${buildQuery()}`);
    jobsCache = Array.isArray(data) ? data : data.results || [];
    if (jobsCache.length === 0) {
      tbody.innerHTML = emptyRow(7, "No jobs match these filters.");
      return;
    }
    tbody.innerHTML = jobsCache.map(j => `
      <tr>
        <td><strong>${escapeHtml(j.title)}</strong></td>
        <td>${escapeHtml(j.department_name || "—")}</td>
        <td>${escapeHtml((j.job_type || "").replace("_", " "))}</td>
        <td>${j.num_openings}</td>
        <td><span class="badge ${statusBadgeClass(j.status)}">${escapeHtml(j.status)}</span></td>
        <td>${fmtDate(j.application_deadline)}</td>
        <td class="table-actions">
          <a class="btn btn-ghost btn-sm" href="ranking.html?job=${j.id}">Rank</a>
          <button class="btn btn-ghost btn-sm" onclick="openJobModal(${j.id})">Edit</button>
          <button class="btn btn-ghost btn-sm" style="color:var(--warn);" onclick="deleteJob(${j.id})">Delete</button>
        </td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(7, "Couldn't load jobs.");
    toastError(err);
  }
}

function renderSkillDraft() {
  document.getElementById("skills-list").innerHTML = skillDraft.map((s, i) => `
    <span class="skills-tag">${escapeHtml(s.skill_name)} · w${s.weight}
      <button type="button" onclick="removeSkillDraft(${i})">&times;</button>
    </span>`).join("") || `<span class="hint">No skills added yet.</span>`;
}
function addSkillToDraft() {
  const nameEl = document.getElementById("skill-name-input");
  const weightEl = document.getElementById("skill-weight-input");
  const name = nameEl.value.trim();
  if (!name) return;
  skillDraft.push({ skill_name: name, weight: Number(weightEl.value) || 1 });
  nameEl.value = "";
  weightEl.value = "1";
  renderSkillDraft();
}
function removeSkillDraft(i) {
  skillDraft.splice(i, 1);
  renderSkillDraft();
}

function openJobModal(id) {
  hideFormError("job-form-error");
  document.getElementById("job-form").reset();
  skillDraft = [];
  if (id) {
    const j = jobsCache.find(x => x.id === id);
    document.getElementById("job-modal-title").textContent = "Edit job";
    document.getElementById("job-id").value = j.id;
    document.getElementById("job-title").value = j.title;
    document.getElementById("job-department").value = j.department;
    document.getElementById("job-type").value = j.job_type;
    document.getElementById("job-description").value = j.description || "";
    document.getElementById("job-exp-min").value = j.experience_min ?? 0;
    document.getElementById("job-exp-max").value = j.experience_max ?? 0;
    document.getElementById("job-education").value = j.education_required || "";
    document.getElementById("job-openings").value = j.num_openings ?? 1;
    document.getElementById("job-location").value = j.location || "";
    document.getElementById("job-deadline").value = j.application_deadline || "";
    document.getElementById("job-keywords").value = j.keywords || "";
    document.getElementById("job-status").value = j.status;
    skillDraft = (j.required_skills || []).map(s => ({ skill_name: s.skill_name, weight: s.weight }));
  } else {
    document.getElementById("job-modal-title").textContent = "Post a job";
    document.getElementById("job-id").value = "";
  }
  renderSkillDraft();
  openModal("job-modal");
}

async function saveJob(e) {
  e.preventDefault();
  hideFormError("job-form-error");
  const id = document.getElementById("job-id").value;
  const body = {
    title: document.getElementById("job-title").value.trim(),
    department: Number(document.getElementById("job-department").value),
    job_type: document.getElementById("job-type").value,
    description: document.getElementById("job-description").value.trim(),
    experience_min: Number(document.getElementById("job-exp-min").value) || 0,
    experience_max: Number(document.getElementById("job-exp-max").value) || 0,
    education_required: document.getElementById("job-education").value.trim(),
    num_openings: Number(document.getElementById("job-openings").value) || 1,
    location: document.getElementById("job-location").value.trim(),
    application_deadline: document.getElementById("job-deadline").value || null,
    keywords: document.getElementById("job-keywords").value.trim(),
    status: document.getElementById("job-status").value,
    required_skills: skillDraft,
  };
  const btn = document.getElementById("job-save-btn");
  btn.disabled = true;
  try {
    if (id) {
      await apiFetch(`/api/jobs/${id}/`, { method: "PATCH", body });
      toast("Job updated", "success");
    } else {
      await apiFetch("/api/jobs/", { method: "POST", body });
      toast("Job posted", "success");
    }
    closeModal("job-modal");
    loadJobs();
  } catch (err) {
    showFormError("job-form-error", err);
  } finally {
    btn.disabled = false;
  }
}

async function deleteJob(id) {
  if (!confirm("Delete this job posting? This cannot be undone.")) return;
  try {
    await apiFetch(`/api/jobs/${id}/`, { method: "DELETE" });
    toast("Job deleted", "success");
    loadJobs();
  } catch (err) {
    toastError(err);
  }
}
