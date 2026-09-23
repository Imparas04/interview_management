/* js/pages/interviewer-feedback.js */
const interviewId = new URLSearchParams(window.location.search).get("interview");

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "interviewer", activePage: "dashboard", title: "Submit feedback" });
  if (!interviewId) {
    document.getElementById("iv-context").textContent = "No interview specified.";
    return;
  }
  document.getElementById("interview-id").value = interviewId;
  await loadContext();
  document.getElementById("feedback-form").addEventListener("submit", submitFeedback);
});

async function loadContext() {
  try {
    const iv = await apiFetch(`/api/interviews/${interviewId}/`);
    document.getElementById("iv-context").textContent =
      `${iv.candidate_username} — ${iv.job_title} — ${iv.round_name} (${iv.scheduled_date})`;
    if (iv.status === "completed") {
      document.getElementById("form-error").textContent = "Feedback has already been submitted for this interview.";
      document.getElementById("form-error").classList.add("show");
      document.getElementById("submit-btn").disabled = true;
    }
  } catch (err) {
    document.getElementById("iv-context").textContent = "Couldn't load this interview.";
    toastError(err);
  }
}

async function submitFeedback(e) {
  e.preventDefault();
  hideFormError("form-error");
  const body = {
    interview: Number(interviewId),
    technical_knowledge: Number(document.getElementById("f-technical").value),
    communication: Number(document.getElementById("f-communication").value),
    problem_solving: Number(document.getElementById("f-problem").value),
    coding: Number(document.getElementById("f-coding").value),
    confidence: Number(document.getElementById("f-confidence").value),
    recommendation: document.getElementById("f-recommendation").value,
  };
  const btn = document.getElementById("submit-btn");
  btn.disabled = true;
  btn.textContent = "Submitting…";
  try {
    await apiFetch("/api/interviews/feedback/", { method: "POST", body });
    toast("Feedback submitted", "success");
    window.location.href = "dashboard.html";
  } catch (err) {
    showFormError("form-error", err);
  } finally {
    btn.disabled = false;
    btn.textContent = "Submit feedback";
  }
}
