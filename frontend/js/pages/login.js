/* js/pages/login.js */
if (isLoggedIn()) goToOwnDashboard();

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideFormError("form-error");
  const btn = document.getElementById("submit-btn");
  btn.disabled = true;
  btn.textContent = "Logging in…";

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  try {
    // login is a public endpoint -> call it directly (apiFetch would also work, no token needed)
    const data = await apiFetch("/api/auth/login/", { method: "POST", body: { username, password } });
    saveSession(data);
    goToOwnDashboard();
  } catch (err) {
    showFormError("form-error", err);
  } finally {
    btn.disabled = false;
    btn.textContent = "Log in";
  }
});
