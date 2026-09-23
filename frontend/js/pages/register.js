/* js/pages/register.js */
if (isLoggedIn()) goToOwnDashboard();

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideFormError("form-error");
  const btn = document.getElementById("submit-btn");
  btn.disabled = true;
  btn.textContent = "Creating…";

  const body = {
    username: document.getElementById("username").value.trim(),
    email: document.getElementById("email").value.trim(),
    password: document.getElementById("password").value,
  };

  try {
    await apiFetch("/api/auth/register/", { method: "POST", body });
    // Registration always creates a candidate; auto-login for a smooth flow.
    const data = await apiFetch("/api/auth/login/", { method: "POST", body: { username: body.username, password: body.password } });
    saveSession(data);
    toast("Account created — welcome!", "success");
    goToOwnDashboard();
  } catch (err) {
    showFormError("form-error", err);
  } finally {
    btn.disabled = false;
    btn.textContent = "Create account";
  }
});
