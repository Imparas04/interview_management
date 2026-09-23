/* js/auth.js — token storage + current user helpers */

function saveSession({ access, refresh, user }) {
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
  localStorage.setItem("user", JSON.stringify(user));
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem("user"));
  } catch (e) {
    return null;
  }
}

function isLoggedIn() {
  return !!localStorage.getItem("access") && !!getUser();
}

function clearAuth() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  localStorage.removeItem("user");
}

function logout() {
  clearAuth();
  window.location.href = resolvePath("login.html");
}

/** Each role's default landing page. */
function dashboardPathFor(role) {
  const map = {
    admin: "admin/dashboard.html",
    hr: "hr/dashboard.html",
    interviewer: "interviewer/dashboard.html",
    candidate: "candidate/dashboard.html",
  };
  return map[role] || "login.html";
}

function goToOwnDashboard() {
  const user = getUser();
  window.location.href = resolvePath(dashboardPathFor(user ? user.role : null));
}
