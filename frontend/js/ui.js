/* js/ui.js — shared shell, toast, modal, and small render helpers used across pages */

const NAV_ITEMS = {
  admin: [
    { page: "dashboard", label: "Dashboard", href: "dashboard.html" },
    { page: "departments", label: "Departments", href: "departments.html" },
    { page: "jobs", label: "Jobs", href: "jobs.html" },
    { page: "candidates", label: "Candidates", href: "candidates.html" },
    { page: "analytics", label: "Analytics", href: "analytics.html" },
  ],
  hr: [
    { page: "dashboard", label: "Dashboard", href: "dashboard.html" },
    { page: "candidates", label: "Candidates", href: "candidates.html" },
    { page: "jobs", label: "Jobs", href: "jobs.html" },
    { page: "applications", label: "Applications", href: "applications.html" },
    { page: "interviews", label: "Interviews", href: "interviews.html" },
    { page: "notifications", label: "Notifications", href: "notifications.html" },
  ],
  interviewer: [
    { page: "dashboard", label: "My Interviews", href: "dashboard.html" },
    { page: "notifications", label: "Notifications", href: "notifications.html" },
  ],
  candidate: [
    { page: "dashboard", label: "Dashboard", href: "dashboard.html" },
    { page: "profile", label: "My Profile", href: "profile.html" },
    { page: "resume-upload", label: "Resume", href: "resume-upload.html" },
    { page: "jobs", label: "Browse Jobs", href: "jobs.html" },
    { page: "applications", label: "My Applications", href: "applications.html" },
    { page: "interviews", label: "Interviews", href: "interviews.html" },
    { page: "notifications", label: "Notifications", href: "notifications.html" },
  ],
};

/** Builds sidebar + topbar. Call once on DOMContentLoaded from every dashboard page. */
function renderShell({ role, activePage, title }) {
  const user = getUser();
  const items = NAV_ITEMS[role] || [];
  const sidebar = document.getElementById("sidebar");
  sidebar.innerHTML = `
    <div class="sb-brand">RecruitOS<span>${role.toUpperCase()} PORTAL</span></div>
    <nav class="sb-nav">
      ${items.map(i => `
        <a class="sb-link ${i.page === activePage ? "active" : ""}" href="${i.href}">
          <span class="dot"></span>${i.label}
        </a>`).join("")}
    </nav>
    <div class="sb-foot">
      <div class="sb-user">${escapeHtml(user.username)}</div>
      <div class="sb-role">${role}</div>
      <button class="btn btn-outline btn-sm btn-block" id="logout-btn">Log out</button>
    </div>`;
  document.getElementById("logout-btn").addEventListener("click", logout);

  const topbar = document.getElementById("topbar");
  topbar.innerHTML = `
    <div class="tb-title">${title}</div>
    <div class="tb-right">
      <div class="notif-bell" id="notif-bell" title="Notifications">
        &#128276;
        <span class="dot" id="notif-count" style="display:none;">0</span>
      </div>
    </div>`;
  document.getElementById("notif-bell").addEventListener("click", () => {
    window.location.href = role === "admin" ? "#" : "notifications.html";
  });
  loadNotifCount();
}

async function loadNotifCount() {
  const el = document.getElementById("notif-count");
  if (!el) return;
  try {
    const data = await apiFetch("/api/notifications/");
    const unread = (Array.isArray(data) ? data : data.results || []).filter(n => !n.is_read).length;
    if (unread > 0) {
      el.textContent = unread > 9 ? "9+" : unread;
      el.style.display = "flex";
    }
  } catch (e) { /* silent — bell badge isn't critical */ }
}

/* ===== Toast ===== */
function ensureToastStack() {
  let stack = document.getElementById("toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.id = "toast-stack";
    document.body.appendChild(stack);
  }
  return stack;
}
function toast(message, type = "default") {
  const stack = ensureToastStack();
  const el = document.createElement("div");
  el.className = `toast ${type === "success" ? "toast-success" : type === "error" ? "toast-error" : ""}`;
  el.textContent = message;
  stack.appendChild(el);
  setTimeout(() => el.remove(), 4200);
}
function toastError(err) {
  toast(err instanceof ApiError ? err.message : "Something went wrong. Please try again.", "error");
}

/* ===== Modal ===== */
function openModal(id) { document.getElementById(id).classList.add("open"); }
function closeModal(id) { document.getElementById(id).classList.remove("open"); }

/* ===== Form error banner ===== */
function showFormError(bannerId, err) {
  const el = document.getElementById(bannerId);
  if (!el) return;
  el.textContent = err instanceof ApiError ? err.message : "Something went wrong.";
  el.classList.add("show");
}
function hideFormError(bannerId) {
  const el = document.getElementById(bannerId);
  if (el) el.classList.remove("show");
}

/* ===== Small formatting helpers ===== */
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function fmtDate(d) {
  if (!d) return "—";
  return new Date(d).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}
function fmtDateTime(d) {
  if (!d) return "—";
  return new Date(d).toLocaleString(undefined, { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}
function statusBadgeClass(status) {
  const s = (status || "").toLowerCase();
  if (["selected", "shortlisted", "confirmed", "completed", "success", "open"].includes(s)) return "badge-success";
  if (["rejected", "cancelled", "failed", "closed"].includes(s)) return "badge-warn";
  if (["pending", "applied", "scheduled", "draft"].includes(s)) return "badge-neutral";
  return "badge-info";
}
function loadingRow(colspan, text = "Loading…") {
  return `<tr class="empty-row"><td colspan="${colspan}"><div class="loading-row" style="justify-content:center;"><span class="spinner"></span>${text}</div></td></tr>`;
}
function emptyRow(colspan, text = "Nothing here yet.") {
  return `<tr class="empty-row"><td colspan="${colspan}">${text}</td></tr>`;
}
