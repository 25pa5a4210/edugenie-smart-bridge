/**
 * Injects the shared sidebar + topbar markup used by every authenticated
 * page, so nav structure lives in one place instead of being copy-pasted
 * across 10 HTML files. Call EduGenieLayout.render(activePage, pageTitle)
 * near the top of each page's script.
 */
const EduGenieLayout = (() => {
  const NAV_ITEMS = [
    { page: "dashboard.html", label: "Dashboard", icon: '<path d="M3 12l9-9 9 9M5 10v10h14V10"/>' },
    { page: "assistant.html", label: "AI Assistant", icon: '<path d="M12 18h.01M9.5 9a2.5 2.5 0 015 0c0 1.5-2 2-2.5 3.5M12 3a9 9 0 100 18 9 9 0 000-18z"/>' },
    { page: "concept-explainer.html", label: "Concept Explainer", icon: '<path d="M12 3l8 4-8 4-8-4 8-4zM4 11l8 4 8-4M4 15l8 4 8-4"/>' },
    { page: "quiz.html", label: "Quiz Generator", icon: '<path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>' },
    { page: "summarizer.html", label: "Summarizer", icon: '<path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z"/>' },
    { page: "learning-path.html", label: "Learning Paths", icon: '<path d="M13 2L3 14h7l-1 8 10-12h-7l1-8z"/>' },
    { page: "history.html", label: "History", icon: '<path d="M12 8v4l3 3M21 12a9 9 0 11-9-9 9 9 0 019 9z"/>' },
    { page: "profile.html", label: "Profile", icon: '<path d="M12 12a5 5 0 100-10 5 5 0 000 10zM3 22a9 9 0 0118 0"/>' },
    { page: "settings.html", label: "Settings", icon: '<path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06A1.65 1.65 0 004.6 15a1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06A1.65 1.65 0 009 4.6a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1z"/>' },
  ];

  function render(activePage, pageTitle) {
    const user = EduGenieAPI.getUser();
    const shellRoot = document.getElementById("app-shell-root");
    if (!shellRoot) return;

    const navHtml = NAV_ITEMS.map(
      (item) => `
      <a href="${item.page}" class="sidebar-link ${item.page === activePage ? "active" : ""}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${item.icon}</svg>
        ${item.label}
      </a>`
    ).join("");

    shellRoot.innerHTML = `
      <div class="sidebar-overlay"></div>
      <aside class="sidebar">
        <a href="../index.html" class="logo"><span class="logo-mark">Eg</span>EduGenie</a>
        <nav class="sidebar-nav">${navHtml}</nav>
        <div class="sidebar-footer">
          <a href="#" class="sidebar-link" data-logout>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/></svg>
            Logout
          </a>
        </div>
      </aside>
      <div class="main-content">
        <div class="topbar">
          <div class="flex items-center gap-sm">
            <button class="mobile-sidebar-toggle" aria-label="Toggle menu">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
            </button>
            <h4 style="margin:0;">${pageTitle}</h4>
          </div>
          <div class="flex items-center gap-sm">
            <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme"></button>
            <div class="avatar" data-user-initials>${user ? EduGenieUI.initials(user.full_name) : "?"}</div>
          </div>
        </div>
        <div class="page-body" id="page-content"></div>
      </div>
    `;

    EduGenieUI.initSidebar();
    EduGenieUI.bindLogoutButtons();
    EduGenieUI.populateUserChrome();
    EduGenieTheme.initToggleButton(document.getElementById("themeToggle"));
  }

  return { render };
})();
