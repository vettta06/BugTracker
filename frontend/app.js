const API_URL = "http://localhost:8000";

const bugsList = document.getElementById("bugsList");
const modal = document.getElementById("modal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.querySelector(".close");
const bugForm = document.getElementById("bugForm");

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
    bugsList.innerHTML = `<p style="color: red;">Ошибка: ${error.message}</p>`;
  }
}

async function loadProjects() {
  const select = document.getElementById("projectSelect");
  try {
    const response = await fetch(`${API_URL}/projects/`);
    const projects = await response.json();
    select.innerHTML = projects
      .map((p) => `<option value="${p.id}">${p.name}</option>`)
      .join("");
  } catch (error) {
    select.innerHTML = '<option value="">Ошибка загрузки</option>';
  }
}

async function loadUsers() {
  const select = document.getElementById("userSelect");
  try {
    const response = await fetch(`${API_URL}/users/`);
    const users = await response.json();
    select.innerHTML = users
      .map((u) => `<option value="${u.id}">${u.name}</option>`)
      .join("");
  } catch (error) {
    select.innerHTML = '<option value="">Ошибка загрузки</option>';
  }
}

function renderBugs(bugs) {
  if (bugs.length === 0) {
    bugsList.innerHTML = "<p>Баги не найдены.</p>";
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
            <p>${bug.description || "Нет описания"}</p>
            <div class="bug-meta">
                Приоритет: <strong>${bug.priority}</strong> | 
                Обновлено: ${new Date(bug.updated_at).toLocaleDateString()}
            </div>
        </div>
    `,
    )
    .join("");
}

bugForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(bugForm);
  const newBug = {
    title: formData.get("title"),
    description: formData.get("description"),
    priority: formData.get("priority"),
    status: "open",
    project_id: parseInt(formData.get("project_id")),
    assignee_id: parseInt(formData.get("assignee_id")),
  };

  try {
    const response = await fetch(`${API_URL}/bugs/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newBug),
    });

    if (response.ok) {
      modal.classList.remove("active");
      bugForm.reset();
      loadBugs();
    } else {
      const err = await response.json();
      alert(`Ошибка: ${err.detail}`);
    }
  } catch (error) {
    alert("Не удалось создать баг.");
  }
});

openModalBtn.addEventListener("click", () => modal.classList.add("active"));
closeModalBtn.addEventListener("click", () => modal.classList.remove("active"));
window.addEventListener("click", (e) => {
  if (e.target === modal) modal.classList.remove("active");
});
