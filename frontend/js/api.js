/* js/api.js
   Single place that knows how to talk to the Django backend.
   Every page calls apiFetch() instead of raw fetch() so that:
   - the Authorization header is always attached
   - a 401 triggers one silent token refresh + retry
   - errors come back as a consistent {status, data} shape you can catch
*/

const API_BASE = "http://127.0.0.1:8000";

/**
 * apiFetch(path, { method, body, isForm })
 * - path: e.g. "/api/jobs/" (relative to API_BASE)
 * - body: plain object (auto JSON.stringify'd) OR a FormData instance (set isForm: true)
 * Returns parsed JSON on success. Throws an ApiError on failure.
 */
async function apiFetch(path, { method = "GET", body = null, isForm = false } = {}) {
  const doRequest = async (accessToken) => {
    const headers = {};
    if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
    let payload = undefined;
    if (body !== null) {
      if (isForm) {
        payload = body; // browser sets multipart Content-Type + boundary itself
      } else {
        headers["Content-Type"] = "application/json";
        payload = JSON.stringify(body);
      }
    }
    const res = await fetch(`${API_BASE}${path}`, { method, headers, body: payload });
    return res;
  };

  let access = localStorage.getItem("access");
  let res = await doRequest(access);

  // Access token expired -> try a silent refresh, then retry the original call once.
  if (res.status === 401 && localStorage.getItem("refresh")) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      access = localStorage.getItem("access");
      res = await doRequest(access);
    }
  }

  if (res.status === 204) return null;

  let data = null;
  try { data = await res.json(); } catch (e) { /* empty body */ }

  if (!res.ok) {
    if (res.status === 401) {
      // refresh failed too / no refresh token at all -> force logout
      clearAuth();
      window.location.href = resolvePath("login.html");
    }
    throw new ApiError(res.status, data);
  }
  return data;
}

async function tryRefreshToken() {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_BASE}/api/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem("access", data.access);
    return true;
  } catch (e) {
    return false;
  }
}

class ApiError extends Error {
  constructor(status, data) {
    super(apiErrorMessage(data));
    this.status = status;
    this.data = data;
  }
}

/** Turns DRF's various error shapes into one readable string. */
function apiErrorMessage(data) {
  if (!data) return "Something went wrong. Please try again.";
  if (typeof data === "string") return data;
  if (data.detail) {
    return Array.isArray(data.detail) ? data.detail.join(" ") : data.detail;
  }
  // field validation errors: {field: ["msg"]}
  const parts = [];
  for (const key in data) {
    const val = Array.isArray(data[key]) ? data[key].join(" ") : data[key];
    parts.push(key === "non_field_errors" ? val : `${key}: ${val}`);
  }
  return parts.join(" | ") || "Something went wrong. Please try again.";
}

/** Resolves a path relative to the site root, no matter which folder depth a page is in. */
function resolvePath(target) {
  const depth = window.location.pathname.split("/").filter(Boolean);
  // if we're inside a role folder (admin/, hr/, interviewer/, candidate/), go up one level
  const inSubfolder = ["admin", "hr", "interviewer", "candidate"].some(f => window.location.pathname.includes(`/${f}/`));
  return inSubfolder ? `../${target}` : target;
}
