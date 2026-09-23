/* js/pages/candidate-detail.js — shared candidate profile view */
const CD_ROLE = document.body.dataset.role;
const CD_ACTIVE_PAGE = document.body.dataset.page;
const candidateId = new URLSearchParams(window.location.search).get("id");

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: CD_ROLE, activePage: CD_ACTIVE_PAGE, title: "Candidate profile" });
  if (!candidateId) {
    document.getElementById("profile-body").textContent = "No candidate id in the URL.";
    return;
  }
  loadProfile();
  loadSkills();
  loadApplicationsForCandidate();
});

async function loadProfile() {
  try {
    const c = await apiFetch(`/api/candidates/${candidateId}/`);
    document.getElementById("cand-name").textContent = c.user?.username || "Candidate";
    document.getElementById("cand-sub").textContent = c.user?.email || "";
    document.getElementById("profile-body").innerHTML = `
      <p><strong>Phone:</strong> ${escapeHtml(c.phone || "—")}</p>
      <p><strong>Address:</strong> ${escapeHtml(c.address || "—")}</p>
      <p><strong>Date of birth:</strong> ${fmtDate(c.date_of_birth)}</p>
      <p><strong>Summary:</strong> ${escapeHtml(c.summary || "—")}</p>
      <p><strong>LinkedIn:</strong> ${c.linkedin_url ? `<a href="${escapeHtml(c.linkedin_url)}" target="_blank" rel="noopener">${escapeHtml(c.linkedin_url)}</a>` : "—"}</p>
      <p><strong>Portfolio:</strong> ${c.portfolio_url ? `<a href="${escapeHtml(c.portfolio_url)}" target="_blank" rel="noopener">${escapeHtml(c.portfolio_url)}</a>` : "—"}</p>`;

    const explanation = c.recommended_department_explanation || {};
    const scores = explanation.all_department_scores || {};
    const rows = Object.entries(scores).sort((a, b) => b[1] - a[1]).slice(0, 6);
    document.getElementById("dept-rec-body").innerHTML = c.recommended_department_name ? `
      <p><strong>${escapeHtml(c.recommended_department_name)}</strong> — ${c.recommended_department_confidence}% confidence</p>
      ${rows.map(([name, score]) => `
        <div style="margin-bottom:8px;">
          <div style="display:flex; justify-content:space-between; font-size:12.5px; color:var(--ink-soft); margin-bottom:3px;">
            <span>${escapeHtml(name)}</span><span>${score}%</span>
          </div>
          <div class="progress-track"><div class="progress-fill" style="width:${Math.min(score, 100)}%;"></div></div>
        </div>`).join("")}
    ` : `<p>No recommendation yet — candidate hasn't run department recommendation.</p>`;
  } catch (err) {
    document.getElementById("profile-body").textContent = "Couldn't load this candidate.";
    toastError(err);
  }
}

async function loadSkills() {
  const el = document.getElementById("skills-body");
  try {
    const data = await apiFetch(`/api/ats/candidates/${candidateId}/skills/`);
    const skills = data.extracted_skills || data.skills || [];
    el.innerHTML = skills.length
      ? skills.map(s => `<span class="skills-tag">${escapeHtml(s)}</span>`).join("")
      : `<p>No skills extracted yet.</p>`;
  } catch (err) {
    el.textContent = "No skills on file yet.";
  }
}

async function loadApplicationsForCandidate() {
  const tbody = document.getElementById("apps-tbody");
  tbody.innerHTML = loadingRow(6);
  try {
    const data = await apiFetch("/api/applications/");
    const all = Array.isArray(data) ? data : data.results || [];
    const mine = all.filter(a => String(a.candidate) === String(candidateId));
    if (mine.length === 0) {
      tbody.innerHTML = emptyRow(6, "This candidate hasn't applied to any jobs yet.");
      return;
    }
    tbody.innerHTML = mine.map(a => `
      <tr>
        <td><strong>${escapeHtml(a.job_title)}</strong></td>
        <td>${escapeHtml(a.department_name || "—")}</td>
        <td><span class="badge ${statusBadgeClass(a.status)}">${escapeHtml(a.status.replace("_", " "))}</span></td>
        <td><button class="btn btn-ghost btn-sm" onclick="downloadResume(${a.resume})">Download</button></td>
        <td id="ats-cell-${a.id}">
          <button class="btn btn-ghost btn-sm" onclick="viewAts(${a.resume}, ${a.job}, ${a.id})">View score</button>
        </td>
        <td></td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(6, "Couldn't load applications.");
    toastError(err);
  }
}

async function downloadResume(resumeId) {
  try {
    const access = localStorage.getItem("access");
    const res = await fetch(`${API_BASE}/api/resumes/${resumeId}/download/`, {
      headers: { Authorization: `Bearer ${access}` },
    });
    if (!res.ok) throw new Error("download failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `resume-${resumeId}`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    toast("Couldn't download this resume.", "error");
  }
}

async function viewAts(resumeId, jobId, appId) {
  try {
    const data = await apiFetch(`/api/ats/results/?resume=${resumeId}`);
    const list = Array.isArray(data) ? data : data.results || [];
    const result = list.find(r => r.job === jobId) || list[0];
    if (!result) {
      toast("No ATS score calculated for this application yet.", "error");
      return;
    }
    const cell = document.getElementById(`ats-cell-${appId}`);
    if (cell) cell.innerHTML = `<span class="badge badge-gold">${result.overall_score}</span>`;
    renderAtsModal(result);
    openModal("ats-modal");
  } catch (err) {
    toastError(err);
  }
}

function renderAtsModal(r) {
  const rows = [
    ["Skills", r.skills_match_pct], ["Experience", r.experience_match_pct], ["Education", r.education_match_pct],
    ["Projects", r.projects_pct], ["Certifications", r.certifications_pct], ["Keywords", r.keywords_pct],
  ];
  const skillsInfo = r.explanation?.skills || {};
  document.getElementById("ats-modal-body").innerHTML = `
    <p><strong>${escapeHtml(r.candidate_username)}</strong> for <strong>${escapeHtml(r.job_title)}</strong></p>
    <h1 style="margin:6px 0 16px;">${r.overall_score}<span style="font-size:16px; color:var(--ink-faint); font-weight:500;"> / 100</span></h1>
    ${rows.map(([label, val]) => `
      <div style="margin-bottom:10px;">
        <div style="display:flex; justify-content:space-between; font-size:12.5px; color:var(--ink-soft); margin-bottom:3px;">
          <span>${label}</span><span>${val}%</span>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:${Math.min(val, 100)}%;"></div></div>
      </div>`).join("")}
    ${skillsInfo.matched ? `
      <div class="field">
        <label>Matched skills</label>
        ${skillsInfo.matched.map(s => `<span class="skills-tag" style="background:var(--success-tint); color:var(--success);">${escapeHtml(s)}</span>`).join("")}
      </div>` : ""}
    ${skillsInfo.missing && skillsInfo.missing.length ? `
      <div class="field">
        <label>Missing skills</label>
        ${skillsInfo.missing.map(s => `<span class="skills-tag" style="background:var(--warn-tint); color:var(--warn);">${escapeHtml(s)}</span>`).join("")}
      </div>` : ""}`;
}
