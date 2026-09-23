/* js/pages/candidate-profile.js */
document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "candidate", activePage: "profile", title: "My profile" });
  await loadProfile();
  document.getElementById("profile-form").addEventListener("submit", saveProfile);
});

async function loadProfile() {
  try {
    // GET auto-creates the profile on first call, per the API spec.
    const c = await apiFetch("/api/candidates/me/");
    document.getElementById("f-phone").value = c.phone || "";
    document.getElementById("f-dob").value = c.date_of_birth || "";
    document.getElementById("f-address").value = c.address || "";
    document.getElementById("f-summary").value = c.summary || "";
    document.getElementById("f-linkedin").value = c.linkedin_url || "";
    document.getElementById("f-portfolio").value = c.portfolio_url || "";

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
    ` : `<p>Upload a resume and run department recommendation from the Resume page to see this.</p>`;
  } catch (err) {
    toastError(err);
  }
}

async function saveProfile(e) {
  e.preventDefault();
  hideFormError("form-error");
  const body = {
    phone: document.getElementById("f-phone").value.trim(),
    date_of_birth: document.getElementById("f-dob").value || null,
    address: document.getElementById("f-address").value.trim(),
    summary: document.getElementById("f-summary").value.trim(),
    linkedin_url: document.getElementById("f-linkedin").value.trim(),
    portfolio_url: document.getElementById("f-portfolio").value.trim(),
  };
  const btn = document.getElementById("save-btn");
  btn.disabled = true;
  try {
    await apiFetch("/api/candidates/me/", { method: "PATCH", body });
    toast("Profile updated", "success");
  } catch (err) {
    showFormError("form-error", err);
  } finally {
    btn.disabled = false;
  }
}
