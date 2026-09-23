/* js/pages/hr-schedule-interview.js */
document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "hr", activePage: "interviews", title: "Schedule interview" });
  await Promise.all([loadApplications(), loadRounds()]);
  document.getElementById("schedule-form").addEventListener("submit", submitSchedule);
});

async function loadApplications() {
  try {
    const data = await apiFetch("/api/applications/");
    const list = Array.isArray(data) ? data : data.results || [];
    const active = list.filter(a => !["selected", "rejected"].includes(a.status));
    document.getElementById("f-application").innerHTML = active.map(a =>
      `<option value="${a.id}">${escapeHtml(a.candidate_username)} — ${escapeHtml(a.job_title)} (${escapeHtml(a.status.replace("_", " "))})</option>`
    ).join("") || `<option value="">No active applications</option>`;
  } catch (err) { toastError(err); }
}

async function loadRounds() {
  try {
    const data = await apiFetch("/api/interviews/rounds/");
    const list = Array.isArray(data) ? data : data.results || [];
    document.getElementById("f-round").innerHTML = list.map(r => `<option value="${r.id}">${escapeHtml(r.name)}</option>`).join("");
  } catch (err) { toastError(err); }
}

async function submitSchedule(e) {
  e.preventDefault();
  hideFormError("form-error");
  const body = {
    application: Number(document.getElementById("f-application").value),
    round: Number(document.getElementById("f-round").value),
    interviewer: Number(document.getElementById("f-interviewer").value),
    scheduled_date: document.getElementById("f-date").value,
    scheduled_time: document.getElementById("f-time").value + ":00",
    duration_minutes: Number(document.getElementById("f-duration").value) || 45,
    location_or_link: document.getElementById("f-location").value.trim(),
    status: document.getElementById("f-status").value,
  };
  const btn = document.getElementById("submit-btn");
  btn.disabled = true;
  btn.textContent = "Scheduling…";
  try {
    await apiFetch("/api/interviews/", { method: "POST", body });
    toast("Interview scheduled", "success");
    window.location.href = "interviews.html";
  } catch (err) {
    // Conflict errors (double-booked interviewer) come back as 400 naming the clash — surface it clearly.
    showFormError("form-error", err);
  } finally {
    btn.disabled = false;
    btn.textContent = "Schedule interview";
  }
}
