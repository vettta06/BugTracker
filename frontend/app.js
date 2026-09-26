const API_URL = "http://localhost:8000";

const bugsList = document.getElementById("bugsList");
const bugsCount = document.getElementById("bugsCount");
const modal = document.getElementById("modal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.querySelector(".close-btn");
const bugForm = document.getElementById("bugForm");
const modalTitle = document.getElementById("modalTitle");
const bugIdField = document.getElementById("bugId");
const submitBtn = document.getElementById("submitBtn");
const btnText = submitBtn.querySelector(".btn-text");
const btnLoader = submitBtn.querySelector(".btn-loader");

document.addEventListener("DOMContentLoaded", () => {
  loadBugs();
  loadProjects();
  loadUsers();
});

async function loadBugs() {
  try {
    const response = await fetch(`${API_URL}/bugs/`);
    if (!response.ok) throw new Error("Network error");
    const bugs = await response.json();
    renderBugs(bugs);
  } catch (error) {
    bugsList.innerHTML = `<p class="error-message">Error: ${error.message}</p>`;
    bugsCount.textContent = "";
  }
}

async function loadProjects() {
  const select = document.getElementById("projectSelect");
  try {
    const response = await fetch(`${API_URL}/projects/`);
    if (!response.ok) throw new Error("Network error");
    const projects = await response.json();
    select.innerHTML = projects
      .map((p) => `<option value="${p.id}">${p.name}</option>`)
      .join("");
  } catch (error) {
    select.innerHTML = '<option value="">Load error</option>';
  }
}

async function loadUsers() {
  const select = document.getElementById("userSelect");
  try {
    const response = await fetch(`${API_URL}/users/`);
    if (!response.ok) throw new Error("Network error");
    const users = await response.json();
    select.innerHTML = users
      .map((u) => `<option value="${u.id}">${u.name}</option>`)
      .join("");
  } catch (error) {
    select.innerHTML = '<option value="">Load error</option>';
  }
}

function renderBugs(bugs) {
  bugsCount.textContent = `${bugs.length} item(s)`;

  if (bugs.length === 0) {
    bugsList.innerHTML = "<p class='empty-state'>No bugs found.</p>";
    return;
  }

  bugsList.innerHTML = bugs
    .map(
      (bug) => `
    <div class="bug-card priority-${bug.priority}">
      <div class="bug-header">
        <h3 class="bug-title">#${bug.id} ${bug.title}</h3>
        <span class="badge badge-${bug.status}">${bug.status}</span>
      </div>
      <p class="bug-description">${bug.description || "No description"}</p>
      <div class="bug-meta">
        Priority: <strong>${bug.priority}</strong> | 
        Updated: ${new Date(bug.updated_at).toLocaleDateString()}
      </div>
      <div class="bug-actions">
        <button class="btn-action btn-edit" data-edit="${bug.id}">
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
          Edit
        </button>
        <button class="btn-action btn-delete" data-delete="${bug.id}">
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 6h18"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          Delete
        </button>
      </div>
    </div>
  `,
    )
    .join("");
}

bugsList.addEventListener("click", async (e) => {
  const editBtn = e.target.closest("[data-edit]");
  const deleteBtn = e.target.closest("[data-delete]");

  if (editBtn) {
    await editBug(editBtn.dataset.edit);
  } else if (deleteBtn) {
    await deleteBug(deleteBtn.dataset.delete);
  }
});

async function editBug(bugId) {
  try {
    const response = await fetch(`${API_URL}/bugs/${bugId}`);
    if (!response.ok) throw new Error("Bug not found");
    const bug = await response.json();

    modalTitle.textContent = "Edit Bug";
    bugIdField.value = bug.id;
    document.getElementById("bugTitle").value = bug.title;
    document.getElementById("bugDescription").value = bug.description || "";
    document.getElementById("bugStatus").value = bug.status;
    document.getElementById("bugPriority").value = bug.priority;
    document.getElementById("projectSelect").value = bug.project_id;
    document.getElementById("userSelect").value = bug.assignee_id;

    openModal();
  } catch (error) {
    showToast("Failed to load bug details", "error");
  }
}

async function deleteBug(bugId) {
  if (
    !confirm(
      "Are you sure you want to delete this bug? This action cannot be undone.",
    )
  )
    return;

  try {
    const response = await fetch(`${API_URL}/bugs/${bugId}`, {
      method: "DELETE",
    });

    if (response.ok) {
      showToast("Bug deleted successfully", "success");
      loadBugs();
    } else {
      showToast("Failed to delete bug", "error");
    }
  } catch (error) {
    showToast("Network error while deleting", "error");
  }
}

bugForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(bugForm);
  const bugId = formData.get("bug_id");

  const bugData = {
    title: formData.get("title"),
    description: formData.get("description"),
    status: formData.get("status"),
    priority: formData.get("priority"),
    project_id: parseInt(formData.get("project_id")),
    assignee_id: parseInt(formData.get("assignee_id")),
  };

  submitBtn.disabled = true;
  btnText.textContent = bugId ? "Updating..." : "Creating...";
  btnLoader.hidden = false;

  try {
    const url = bugId ? `${API_URL}/bugs/${bugId}` : `${API_URL}/bugs/`;
    const method = bugId ? "PUT" : "POST";

    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bugData),
    });

    if (response.ok) {
      closeModal();
      bugForm.reset();
      bugIdField.value = "";
      loadBugs();
      showToast(
        bugId ? "Bug updated successfully" : "Bug created successfully",
        "success",
      );
    } else {
      const err = await response.json();
      showToast(`Error: ${err.detail || "Unknown error"}`, "error");
    }
  } catch (error) {
    showToast("Failed to save bug", "error");
  } finally {
    submitBtn.disabled = false;
    btnText.textContent = "Save";
    btnLoader.hidden = true;
  }
});

function openModal() {
  modal.classList.add("active");
  document.body.style.overflow = "hidden";
}

function closeModal() {
  modal.classList.remove("active");
  document.body.style.overflow = "";
}

openModalBtn.addEventListener("click", () => {
  modalTitle.textContent = "Create New Bug";
  bugIdField.value = "";
  bugForm.reset();
  document.getElementById("bugStatus").value = "open";
  openModal();
});

closeModalBtn.addEventListener("click", closeModal);
modal.querySelector(".modal-overlay").addEventListener("click", closeModal);

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal.classList.contains("active")) {
    closeModal();
  }
});

function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("hide");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
