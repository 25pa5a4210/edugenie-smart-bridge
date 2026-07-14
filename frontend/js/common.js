/**
 * Shared UI helpers used across every page: toast notifications, navbar/sidebar
 * auth-aware behavior, mobile menu toggling, and small formatting utilities.
 */
const EduGenieUI = (() => {
  function ensureToastContainer() {
    let el = document.getElementById("toast-container");
    if (!el) {
      el = document.createElement("div");
      el.id = "toast-container";
      document.body.appendChild(el);
    }
    return el;
  }

  function toast(message, type = "default", duration = 4000) {
    const container = ensureToastContainer();
    const el = document.createElement("div");
    el.className = `toast ${type === "success" ? "toast-success" : type === "error" ? "toast-error" : ""}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => {
      el.classList.add("toast-out");
      setTimeout(() => el.remove(), 220);
    }, duration);
  }

  function requireAuth() {
    if (!EduGenieAPI.getToken()) {
      window.location.href = "login.html";
      return false;
    }
    return true;
  }

  function redirectIfAuthed() {
    if (EduGenieAPI.getToken()) {
      window.location.href = "pages/dashboard.html";
    }
  }

  function logout() {
    EduGenieAPI.clearToken();
    EduGenieAPI.clearUser();
    window.location.href = "../index.html";
  }

  function initials(name) {
    if (!name) return "?";
    const parts = name.trim().split(/\s+/);
    return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
  }

  function formatDate(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    } catch {
      return iso;
    }
  }

  function formatDateTime(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch {
      return iso;
    }
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function initMobileNav() {
    const toggle = document.querySelector(".mobile-toggle");
    const links = document.querySelector(".nav-links");
    if (toggle && links) {
      toggle.addEventListener("click", () => links.classList.toggle("open"));
    }
  }

  function initSidebar() {
    const toggle = document.querySelector(".mobile-sidebar-toggle");
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.querySelector(".sidebar-overlay");
    if (toggle && sidebar) {
      toggle.addEventListener("click", () => {
        sidebar.classList.toggle("open");
        if (overlay) overlay.classList.toggle("open");
      });
    }
    if (overlay && sidebar) {
      overlay.addEventListener("click", () => {
        sidebar.classList.remove("open");
        overlay.classList.remove("open");
      });
    }
    // Highlight current page
    const current = window.location.pathname.split("/").pop();
    document.querySelectorAll(".sidebar-link").forEach((link) => {
      if (link.getAttribute("href") === current) link.classList.add("active");
    });
  }

  function populateUserChrome() {
    const user = EduGenieAPI.getUser();
    if (!user) return;
    document.querySelectorAll("[data-user-name]").forEach((el) => (el.textContent = user.full_name));
    document.querySelectorAll("[data-user-initials]").forEach((el) => (el.textContent = initials(user.full_name)));
    document.querySelectorAll("[data-user-email]").forEach((el) => (el.textContent = user.email));
    document.querySelectorAll("[data-user-level]").forEach((el) => (el.textContent = user.academic_level));
  }

  function bindLogoutButtons() {
    document.querySelectorAll("[data-logout]").forEach((el) => {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        logout();
      });
    });
  }

  return {
    toast,
    requireAuth,
    redirectIfAuthed,
    logout,
    initials,
    formatDate,
    formatDateTime,
    escapeHtml,
    initMobileNav,
    initSidebar,
    populateUserChrome,
    bindLogoutButtons,
  };
})();
