/* js/pages/hr-interviews.js */
let interviewsCache = [];

document.addEventListener("DOMContentLoaded", async () => {
  renderShell({ role: "hr", activePage: "interviews", title: "Interview calendar" });

  const calendarEl = document.getElementById("calendar");
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    headerToolbar: { left: "prev,next today", center: "title", right: "dayGridMonth,timeGridWeek,listMonth" },
    height: "auto",
    events: [],
    eventClick: (info) => showInterviewModal(Number(info.event.id)),
  });
  calendar.render();

  try {
    const data = await apiFetch("/api/interviews/");
    interviewsCache = Array.isArray(data) ? data : data.results || [];
    const events = interviewsCache.map(iv => ({
      id: iv.id,
      title: `${iv.round_name} — ${iv.candidate_username}`,
      start: `${iv.scheduled_date}T${iv.scheduled_time}`,
      color: eventColor(iv.status),
    }));
    calendar.addEventSource(events);
  } catch (err) {
    toastError(err);
  }
});

function eventColor(status) {
  return { scheduled: "#2E6FBB", confirmed: "#1F8A70", completed: "#8993A6", rescheduled: "#B8860B", cancelled: "#C1121F" }[status] || "#2E4374";
}

function showInterviewModal(id) {
  const iv = interviewsCache.find(x => x.id === id);
  if (!iv) return;
  document.getElementById("iv-modal-body").innerHTML = `
    <p><strong>Candidate:</strong> ${escapeHtml(iv.candidate_username)}</p>
    <p><strong>Job:</strong> ${escapeHtml(iv.job_title)}</p>
    <p><strong>Round:</strong> ${escapeHtml(iv.round_name)}</p>
    <p><strong>Interviewer:</strong> ${escapeHtml(iv.interviewer_username)}</p>
    <p><strong>When:</strong> ${fmtDate(iv.scheduled_date)} at ${iv.scheduled_time} (${iv.duration_minutes} min)</p>
    <p><strong>Location / link:</strong> ${escapeHtml(iv.location_or_link || "—")}</p>
    <p><strong>Status:</strong> <span class="badge ${statusBadgeClass(iv.status)}">${escapeHtml(iv.status)}</span></p>
    ${iv.status === "completed" ? `<div id="fb-box"><button class="btn btn-outline btn-sm" onclick="loadFeedback(${iv.id})">View feedback</button></div>` : ""}
  `;
  openModal("iv-modal");
}

async function loadFeedback(interviewId) {
  const box = document.getElementById("fb-box");
  box.innerHTML = `<div class="loading-row"><span class="spinner"></span>Loading feedback…</div>`;
  try {
    const data = await apiFetch(`/api/interviews/feedback/list/?interview=${interviewId}`);
    const list = Array.isArray(data) ? data : data.results || [];
    if (list.length === 0) { box.innerHTML = `<p class="hint">No feedback recorded.</p>`; return; }
    box.innerHTML = list.map(f => `
      <div style="border-top:1px solid var(--border); padding-top:10px; margin-top:10px;">
        <p><strong>Overall score:</strong> ${f.overall_score}</p>
        <p>Technical: ${f.technical_knowledge} · Communication: ${f.communication} · Problem solving: ${f.problem_solving} · Coding: ${f.coding} · Confidence: ${f.confidence}</p>
        <p><span class="badge ${statusBadgeClass(f.recommendation)}">${escapeHtml((f.recommendation || "").replace("_", " "))}</span></p>
      </div>`).join("");
  } catch (err) {
    box.innerHTML = `<p class="hint">Couldn't load feedback.</p>`;
  }
}
