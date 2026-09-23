/* js/router-guard.js
   Include this AFTER api.js and auth.js on every dashboard page.
   It reads the required role from <body data-role="hr">, and:
   - bounces to login if there's no token
   - bounces a wrong-role user back to their own dashboard
*/
(function guard() {
  if (!isLoggedIn()) {
    window.location.href = resolvePath("login.html");
    return;
  }
  const requiredRole = document.body.dataset.role;
  const user = getUser();
  if (requiredRole && user.role !== requiredRole) {
    goToOwnDashboard();
  }
})();
