/* js/pages/notifications.js — shared across hr, interviewer, candidate */
const NOTIF_ROLE = document.body.dataset.role;

document.addEventListener("DOMContentLoaded", () => {
  renderShell({ role: NOTIF_ROLE, activePage: "notifications", title: "Notifications" });
  loadNotifications();
  document.getElementById("mark-all-btn").addEventListener("click", markAllRead);
});

const NOTIF_ICON = { application: "\u{1F4C4}", interview: "\u{1F4C5}", feedback: "\u{1F4DD}", general: "\u{1F514}" };

async function loadNotifications() {
  const list = document.getElementById("notif-list");
  list.innerHTML = `<div class="loading-row"><span class="spinner"></span>Loading…</div>`;
  try {
    const data = await apiFetch("/api/notifications/");
    const items = Array.isArray(data) ? data : data.results || [];
    if (items.length === 0) {
      list.innerHTML = `<div class="card">No notifications yet.</div>`;
      return;
    }
    list.innerHTML = items.map(n => `
      <div class="card" style="margin-bottom:10px; display:flex; gap:14px; align-items:flex-start; ${n.is_read ? "opacity:.6;" : ""}">
        <div style="font-size:20px;">${NOTIF_ICON[n.notif_type] || "\u{1F514}"}</div>
        <div style="flex:1;">
          <div>${escapeHtml(n.message)}</div>
          <div class="hint" style="margin-top:4px;">${fmtDateTime(n.created_at)}</div>
        </div>
        ${!n.is_read ? `<button class="btn btn-ghost btn-sm" onclick="markOneRead(${n.id})">Mark read</button>` : `<span class="badge badge-neutral">Read</span>`}
      </div>`).join("");
  } catch (err) {
    list.innerHTML = `<div class="card">Couldn't load notifications.</div>`;
    toastError(err);
  }
}

async function markOneRead(id) {
  try {
    await apiFetch(`/api/notifications/${id}/read/`, { method: "PATCH" });
    loadNotifications();
  } catch (err) { toastError(err); }
}

async function markAllRead() {
  try {
    const res = await apiFetch("/api/notifications/mark-all-read/", { method: "POST" });
    toast(`Marked ${res.marked_read} as read`, "success");
    loadNotifications();
  } catch (err) { toastError(err); }
}
