/* js/pages/interviewer-dashboard.js */
document.addEventListener("DOMContentLoaded", () => {
  renderShell({ role: "interviewer", activePage: "dashboard", title: "My interviews" });
  loadMyInterviews();
  document.getElementById("filter-btn").addEventListener("click", loadMyInterviews);
});

async function loadMyInterviews() {
  const tbody = document.getElementById("iv-tbody");
  tbody.innerHTML = loadingRow(6);
  const status = document.getElementById("f-status").value;
  const params = status ? `?status=${status}` : "";
  try {
    const data = await apiFetch(`/api/interviews/${params}`);
    const list = Array.isArray(data) ? data : data.results || [];
    if (list.length === 0) {
      tbody.innerHTML = emptyRow(6, "No interviews assigned to you yet.");
      return;
    }
    // upcoming first
    list.sort((a, b) => `${a.scheduled_date}${a.scheduled_time}`.localeCompare(`${b.scheduled_date}${b.scheduled_time}`));
    tbody.innerHTML = list.map(iv => `
      <tr>
        <td><strong>${escapeHtml(iv.candidate_username)}</strong></td>
        <td>${escapeHtml(iv.job_title)}</td>
        <td>${escapeHtml(iv.round_name)}</td>
        <td>${fmtDate(iv.scheduled_date)} · ${iv.scheduled_time}</td>
        <td><span class="badge ${statusBadgeClass(iv.status)}">${escapeHtml(iv.status)}</span></td>
        <td>${iv.status === "completed"
          ? `<span class="hint">Feedback submitted</span>`
          : `<a class="btn btn-outline btn-sm" href="feedback-form.html?interview=${iv.id}">Submit feedback</a>`}
        </td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(6, "Couldn't load your interviews.");
    toastError(err);
  }
}
