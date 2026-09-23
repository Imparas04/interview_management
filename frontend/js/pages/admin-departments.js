/* js/pages/admin-departments.js */
document.addEventListener("DOMContentLoaded", () => {
  renderShell({ role: "admin", activePage: "departments", title: "Departments" });
  loadDepartments();

  document.getElementById("add-btn").addEventListener("click", () => openDeptModal(null));
  document.getElementById("dept-modal-close").addEventListener("click", () => closeModal("dept-modal"));
  document.getElementById("dept-cancel-btn").addEventListener("click", () => closeModal("dept-modal"));
  document.getElementById("dept-form").addEventListener("submit", saveDept);
});

let departmentsCache = [];

async function loadDepartments() {
  const tbody = document.getElementById("dept-tbody");
  tbody.innerHTML = loadingRow(4);
  try {
    const data = await apiFetch("/api/departments/");
    departmentsCache = Array.isArray(data) ? data : data.results || [];
    if (departmentsCache.length === 0) {
      tbody.innerHTML = emptyRow(4, "No departments yet — add the first one.");
      return;
    }
    tbody.innerHTML = departmentsCache.map(d => `
      <tr>
        <td><strong>${escapeHtml(d.name)}</strong></td>
        <td>${escapeHtml(d.description || "—")}</td>
        <td><span class="badge ${d.is_active ? "badge-success" : "badge-neutral"}">${d.is_active ? "Active" : "Inactive"}</span></td>
        <td class="table-actions">
          <button class="btn btn-ghost btn-sm" onclick="openDeptModal(${d.id})">Edit</button>
          <button class="btn btn-ghost btn-sm" style="color:var(--warn);" onclick="deleteDept(${d.id})">Delete</button>
        </td>
      </tr>`).join("");
  } catch (err) {
    tbody.innerHTML = emptyRow(4, "Couldn't load departments.");
    toastError(err);
  }
}

function openDeptModal(id) {
  hideFormError("dept-form-error");
  const form = document.getElementById("dept-form");
  form.reset();
  document.getElementById("dept-active").checked = true;
  if (id) {
    const d = departmentsCache.find(x => x.id === id);
    document.getElementById("dept-modal-title").textContent = "Edit department";
    document.getElementById("dept-id").value = d.id;
    document.getElementById("dept-name").value = d.name;
    document.getElementById("dept-desc").value = d.description || "";
    document.getElementById("dept-active").checked = d.is_active;
  } else {
    document.getElementById("dept-modal-title").textContent = "Add department";
    document.getElementById("dept-id").value = "";
  }
  openModal("dept-modal");
}

async function saveDept(e) {
  e.preventDefault();
  hideFormError("dept-form-error");
  const id = document.getElementById("dept-id").value;
  const body = {
    name: document.getElementById("dept-name").value.trim(),
    description: document.getElementById("dept-desc").value.trim(),
    is_active: document.getElementById("dept-active").checked,
  };
  const btn = document.getElementById("dept-save-btn");
  btn.disabled = true;
  try {
    if (id) {
      await apiFetch(`/api/departments/${id}/`, { method: "PATCH", body });
      toast("Department updated", "success");
    } else {
      await apiFetch("/api/departments/", { method: "POST", body });
      toast("Department created", "success");
    }
    closeModal("dept-modal");
    loadDepartments();
  } catch (err) {
    showFormError("dept-form-error", err);
  } finally {
    btn.disabled = false;
  }
}

async function deleteDept(id) {
  if (!confirm("Delete this department? This cannot be undone.")) return;
  try {
    await apiFetch(`/api/departments/${id}/`, { method: "DELETE" });
    toast("Department deleted", "success");
    loadDepartments();
  } catch (err) {
    toastError(err);
  }
}
