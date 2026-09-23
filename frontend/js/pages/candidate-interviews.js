/* js/pages/candidate-interviews.js */
document.addEventListener("DOMContentLoaded", () => {
  renderShell({ role: "candidate", activePage: "interviews", title: "My interviews" });
  loadInterviews();
});

async function loadInterviews() {
  const tbody = document.getElementById("iv-tbody");
  tbody.innerHTML = loadingRow(5);
  try {
    const data = await apiFetch("/api/interviews/");
    const list = Array.isArray(data) ? data : data.results || [];
    if (list.length === 0) {
      tbody.innerHTML = emptyRow(5, "No interviews scheduled yet.");
      return;
    }
    list.sort((a, b) => `${a.scheduled_date}${a.scheduled_time}`.localeCompare(`${b.scheduled_date}${b.scheduled_time}`));
    tbody.innerHTML = list.map(iv => `
      <tr>
        <td><strong>${escapeHtml(iv.job_title)}</strong></td>
        <td>${escapeHtml(iv.round_name)}</td>
        <td>${fmtDate(iv.scheduled_date)} · ${iv.scheduled_time}</td>
        <td>${escapeHtml(iv.location_or_link || "—")}</td>
        <td><span class="badge ${statusBadgeClass(iv.status)}">${escapeHtml(iv.status)}</span></td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(5, "Couldn't load your interviews.");
    toastError(err);
  }
}
