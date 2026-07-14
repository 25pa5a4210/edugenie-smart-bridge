(async function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("profile.html", "Profile");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  try {
    const me = await EduGenieAPI.me();
    EduGenieAPI.setUser(me);
    EduGenieUI.populateUserChrome();
    document.getElementById("full_name").value = me.full_name;
    document.getElementById("academic_level").value = me.academic_level;
    document.getElementById("createdAt").textContent = EduGenieUI.formatDate(me.created_at);
  } catch (err) {
    EduGenieUI.toast(err.message, "error");
  }

  document.getElementById("profileForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("saveBtn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Saving...`;

    try {
      const updated = await EduGenieAPI.updateProfile({
        full_name: document.getElementById("full_name").value.trim(),
        academic_level: document.getElementById("academic_level").value,
      });
      EduGenieAPI.setUser(updated);
      EduGenieUI.populateUserChrome();
      EduGenieUI.toast("Profile updated", "success");
    } catch (err) {
      EduGenieUI.toast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Save Changes";
    }
  });

  try {
    const stats = await EduGenieAPI.getProfileStats();
    document.getElementById("statGrid").innerHTML = `
      <div class="stat-card"><div class="stat-value">${stats.total_questions_asked}</div><div class="stat-label">Questions Asked</div></div>
      <div class="stat-card"><div class="stat-value">${stats.quizzes_completed}</div><div class="stat-label">Quizzes Completed</div></div>
      <div class="stat-card"><div class="stat-value">${stats.average_quiz_score}%</div><div class="stat-label">Average Score</div></div>
      <div class="stat-card"><div class="stat-value">${stats.learning_paths_created}</div><div class="stat-label">Learning Paths</div></div>
    `;
  } catch (err) {
    EduGenieUI.toast(err.message, "error");
  }
})();
