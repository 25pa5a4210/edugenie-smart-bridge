/**
 * Theme (light/dark) toggle. Persists preference in localStorage and applies
 * it before paint via the inline script in each page's <head> to avoid FOUC.
 */
const EduGenieTheme = (() => {
  const STORAGE_KEY = "edugenie_theme";

  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
  }

  function get() {
    return localStorage.getItem(STORAGE_KEY) || "dark";
  }

  function set(theme) {
    localStorage.setItem(STORAGE_KEY, theme);
    apply(theme);
  }

  function toggle() {
    const next = get() === "dark" ? "light" : "dark";
    set(next);
    return next;
  }

  function initToggleButton(buttonEl) {
    if (!buttonEl) return;
    updateIcon(buttonEl);
    buttonEl.addEventListener("click", () => {
      toggle();
      updateIcon(buttonEl);
    });
  }

  function updateIcon(buttonEl) {
    const isDark = get() === "dark";
    buttonEl.innerHTML = isDark
      ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1111.2 3 7 7 0 0021 12.8z"/></svg>';
  }

  // Apply immediately on load
  apply(get());

  return { get, set, toggle, initToggleButton };
})();
