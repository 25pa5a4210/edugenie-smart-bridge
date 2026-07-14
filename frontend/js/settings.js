(async function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("settings.html", "Settings");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  function selectThemePill(theme) {
    document.querySelectorAll("#themePills .option-pill").forEach((p) => p.classList.toggle("active", p.dataset.val === theme));
  }
  selectThemePill(EduGenieTheme.get());

  document.querySelectorAll("#themePills .option-pill").forEach((p) => {
    p.addEventListener("click", () => {
      EduGenieTheme.set(p.dataset.val);
      selectThemePill(p.dataset.val);
      document.getElementById("themeToggle") && EduGenieTheme.initToggleButton(document.getElementById("themeToggle"));
    });
  });

  try {
    const prefs = await EduGenieAPI.getPreferences();
    document.getElementById("explanationStyle").value = prefs.preferred_explanation_style;
    document.getElementById("quizDifficulty").value = prefs.quiz_difficulty_preference;
  } catch (err) {
    EduGenieUI.toast(err.message, "error");
  }

  document.getElementById("saveSettingsBtn").addEventListener("click", async () => {
    const btn = document.getElementById("saveSettingsBtn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Saving...`;
    try {
      await EduGenieAPI.updatePreferences({
        theme: EduGenieTheme.get(),
        preferred_explanation_style: document.getElementById("explanationStyle").value,
        quiz_difficulty_preference: document.getElementById("quizDifficulty").value,
      });
      EduGenieUI.toast("Settings saved", "success");
    } catch (err) {
      EduGenieUI.toast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Save Settings";
    }
  });
})();
