/* js/pages/candidate-resume.js */
let myCandidateId = null;
let scoreResumeId = null;

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "candidate", activePage: "resume-upload", title: "Resume" });
  try {
    const me = await apiFetch("/api/candidates/me/");
    myCandidateId = me.id;
  } catch (e) { /* non-fatal for the upload flow itself */ }

  loadResumes();
  document.getElementById("upload-form").addEventListener("submit", uploadResume);
  document.getElementById("score-submit-btn").addEventListener("click", submitScore);
});

async function loadResumes() {
  const tbody = document.getElementById("resume-tbody");
  tbody.innerHTML = loadingRow(5);
  try {
    const data = await apiFetch("/api/resumes/");
    const list = Array.isArray(data) ? data : data.results || [];
    if (list.length === 0) {
      tbody.innerHTML = emptyRow(5, "No resume uploaded yet.");
      return;
    }
    tbody.innerHTML = list.map(r => `
      <tr>
        <td><strong>${escapeHtml(r.original_filename)}</strong></td>
        <td>${escapeHtml(r.parsed_name || "—")}</td>
        <td><span class="badge ${statusBadgeClass(r.parsing_status)}">${escapeHtml(r.parsing_status)}</span></td>
        <td>${fmtDateTime(r.uploaded_at)}</td>
        <td class="table-actions">
          <button class="btn btn-ghost btn-sm" onclick="extractSkills(${r.id})">Extract skills</button>
          <button class="btn btn-ghost btn-sm" onclick="openScoreModal(${r.id})">Calculate ATS score</button>
          <button class="btn btn-ghost btn-sm" onclick="recommendDept()">Recommend dept.</button>
        </td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(5, "Couldn't load your resumes.");
    toastError(err);
  }
}

async function uploadResume(e) {
  e.preventDefault();
  hideFormError("upload-error");
  const fileInput = document.getElementById("resume-file");
  const file = fileInput.files[0];
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) {
    showFormError("upload-error", { message: "File is larger than 5MB." });
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  const btn = document.getElementById("upload-btn");
  btn.disabled = true;
  btn.textContent = "Uploading…";
  try {
    await apiFetch("/api/resumes/upload/", { method: "POST", body: formData, isForm: true });
    toast("Resume uploaded and parsed", "success");
    fileInput.value = "";
    loadResumes();
  } catch (err) {
    showFormError("upload-error", err);
  } finally {
    btn.disabled = false;
    btn.textContent = "Upload resume";
  }
}

async function extractSkills(resumeId) {
  try {
    const res = await apiFetch(`/api/ats/resumes/${resumeId}/extract-skills/`, { method: "POST" });
    toast(`Extracted ${res.count} skill(s)`, "success");
  } catch (err) {
    toastError(err);
  }
}

async function openScoreModal(resumeId) {
  scoreResumeId = resumeId;
  hideFormError("score-error");
  document.getElementById("score-result").innerHTML = "";
  try {
    const data = await apiFetch("/api/jobs/"); // candidate sees open jobs only
    const jobs = Array.isArray(data) ? data : data.results || [];
    document.getElementById("score-job").innerHTML = jobs.map(j => `<option value="${j.id}">${escapeHtml(j.title)}</option>`).join("");
  } catch (err) { toastError(err); }
  openModal("score-modal");
}

async function submitScore() {
  hideFormError("score-error");
  const jobId = Number(document.getElementById("score-job").value);
  const btn = document.getElementById("score-submit-btn");
  btn.disabled = true;
  try {
    const r = await apiFetch("/api/ats/score/", { method: "POST", body: { resume_id: scoreResumeId, job_id: jobId } });
    document.getElementById("score-result").innerHTML = `
      <h1 style="margin:6px 0;">${r.overall_score}<span style="font-size:14px; color:var(--ink-faint); font-weight:500;"> / 100</span></h1>
      <p class="hint">Skills ${r.skills_match_pct}% · Experience ${r.experience_match_pct}% · Education ${r.education_match_pct}%</p>`;
  } catch (err) {
    // Backend returns 400 if skills weren't extracted first — message surfaces that clearly.
    showFormError("score-error", err);
  } finally {
    btn.disabled = false;
  }
}

async function recommendDept() {
  if (!myCandidateId) { toast("Couldn't find your candidate profile.", "error"); return; }
  try {
    const r = await apiFetch(`/api/ats/candidates/${myCandidateId}/recommend-department/`, { method: "POST" });
    toast(`Recommended: ${r.recommended_department} (${r.confidence}%)`, "success");
  } catch (err) {
    toastError(err);
  }
}
