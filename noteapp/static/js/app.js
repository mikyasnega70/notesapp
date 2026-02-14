document.addEventListener("DOMContentLoaded", () => {

    handleRegister();
    handleLogin();
    handleLogout();
    handleSearch();
    handleEditNote();   // ✅ FIXED (was handleEdit)
    handleDelete();
    handleRestore();

});


// ================= REGISTER =================
function handleRegister() {
    const form = document.getElementById("registerForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Convert form inputs to JS object
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const response = await fetch("/auth/create", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            window.location.href = "/auth/login-page";
        } else {
            document.getElementById("registerError").innerText =
                "Registration failed.";
        }
    });
}



// ================= LOGIN =================
function handleLogin() {
    const form = document.getElementById("loginForm");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(form);

        const payload = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            payload.append(key, value);
        }

        try {
            const response = await fetch("/auth/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: payload.toString()
            });

            if (response.ok) {
                const data = await response.json();

                document.cookie = `access_token=${data.access_token}; path=/`;

                window.location.href = "/notes/home-page/";
            } else {
                const errorData = await response.json();
                document.getElementById("loginError").innerText =
                    errorData.detail || "Invalid username or password.";
            }
        } catch (error) {
            console.error("Login error:", error);
            document.getElementById("loginError").innerText =
                "An error occurred. Please try again.";
        }
    });
}


// ================= LOGOUT =================
function handleLogout() {
    const logoutBtn = document.getElementById("logoutBtn");
    if (!logoutBtn) return;

    logoutBtn.addEventListener("click", () => {
        document.cookie = "access_token=; Max-Age=0; path=/";
        window.location.href = '/auth/login-page';  // ✅ fixed path
    });
}


// ================= SEARCH =================
function handleSearch() {
    const form = document.getElementById("searchForm");
    if (!form) return;

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const searchValue =
            form.querySelector("input[name='search']").value;

        if (searchValue.trim() === "") {
            window.location.href = "/notes/home-page/";
        } else {
            window.location.href =
                `/notes/home-page/?search=${encodeURIComponent(searchValue)}`;
        }
    });
}


// ================= EDIT NOTE =================
function handleEditNote() {
    const form = document.getElementById("editForm");
    if (!form) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const path = window.location.pathname;
        const noteId = path.substring(path.lastIndexOf("/") + 1);

        const payload = {
        title: data.title,
        content: data.content,
        tags: data.tags
            ? data.tags.split(",").map(tag => tag.trim())
            : []
        };


        try {
            const token = getCookie("access_token");
            if (!token) {
                alert("Authentication token not found.");
                return;
            }

            const response = await fetch(`/notes/update/${noteId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.status === 204) {
                window.location.href = "/notes/home-page/";
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Update failed.");
            }

        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred.");
        }
    });
}


// ================= DELETE =================
function handleDelete() {
    const form = document.getElementById("deleteForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!confirm("Are you sure you want to delete?")) return;

        // ✅ Get note ID from URL
        const path = window.location.pathname;
        const noteId = path.substring(path.lastIndexOf("/") + 1);

        const token = getCookie("access_token");
        if (!token) {
            alert("Not authenticated");
            return;
        }

        const response = await fetch(`/notes/delete/${noteId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 204) {
            window.location.href = "/notes/home-page/";
        } else {
            alert("Delete failed.");
        }
    });
}



// ================= RESTORE =================
function handleRestore() {
    const form = document.getElementById("restoreForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const noteId = form.querySelector("input[name='note_id']").value;

        if (!noteId || isNaN(noteId)) {
            alert("Please enter a valid note ID");
            return;
        }

        const token = getCookie("access_token");
        if (!token) {
            alert("Not authenticated");
            return;
        }

        const response = await fetch(`/notes/${noteId}/restore`, {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 204) {
            window.location.href = "/notes/home-page/";
        } else if (response.status === 404) {
            alert("Note not found or already restored.");
        } else {
            alert("Restore failed.");
        }
    });
}





// ================= HELPER =================
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}
