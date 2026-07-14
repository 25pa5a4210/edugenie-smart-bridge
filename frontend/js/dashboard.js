(async function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("dashboard.html", "Dashboard");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  const ACTIVITY_ICONS = {
    question: '<path d="M12 18h.01M9.5 9a2.5 2.5 0 015 0c0 1.5-2 2-2.5 3.5M12 3a9 9 0 100 18 9 9 0 000-18z"/>',
    concept: '<path d="M12 3l8 4-8 4-8-4 8-4zM4 11l8 4 8-4M4 15l8 4 8-4"/>',
    quiz: '<path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>',
    summary: '<path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z"/>',
    learning_path: '<path d="M13 2L3 14h7l-1 8 10-12h-7l1-8z"/>',
  };
  const ACTIVITY_LABELS = {
    question: "Asked a question",
    concept: "Explained a concept",
    quiz: "Generated a quiz",
    summary: "Summarized text",
    learning_path: "Created a learning path",
  };

  try {
    const data = await EduGenieAPI.getDashboard();

    document.getElementById("statGrid").innerHTML = `
      <div class="card stat-card"><div class="stat-value">${data.stats.questions_asked}</div><div class="stat-label">Questions Asked</div></div>
      <div class="card stat-card"><div class="stat-value">${data.stats.quizzes_taken}</div><div class="stat-label">Quizzes Taken</div></div>
      <div class="card stat-card"><div class="stat-value">${data.stats.average_quiz_score}%</div><div class="stat-label">Average Quiz Score</div></div>
      <div class="card stat-card"><div class="stat-value">${data.stats.active_learning_paths}</div><div class="stat-label">Learning Paths</div></div>
    `;

    const activityEl = document.getElementById("recentActivity");
    if (!data.recent_activity.length) {
      activityEl.innerHTML = `<div class="state-block" style="padding:var(--space-md) 0;">
        <p>No activity yet. Try asking EduGenie a question to get started!</p>
      </div>`;
    } else {
      activityEl.innerHTML = data.recent_activity
        .map(
          (a) => `
        <div class="activity-item">
          <div class="activity-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${ACTIVITY_ICONS[a.activity_type] || ""}</svg></div>
          <div style="flex:1;">
            <div>${ACTIVITY_LABELS[a.activity_type] || a.activity_type}${a.topic ? `: <strong>${EduGenieUI.escapeHtml(a.topic)}</strong>` : ""}</div>
            <div class="activity-meta">${EduGenieUI.formatDateTime(a.created_at)}</div>
          </div>
        </div>`
        )
        .join("");
    }

    const recEl = document.getElementById("recommendations");
    const rec = data.recommendations;
    const hasRec =
      (rec.topics_to_learn_next && rec.topics_to_learn_next.length) ||
      (rec.topics_to_revise && rec.topics_to_revise.length);

    if (!hasRec) {
      recEl.innerHTML = `<div class="state-block" style="padding:var(--space-md) 0;">
        <p>${EduGenieUI.escapeHtml(rec.disclaimer || "Keep learning to unlock personalized recommendations.")}</p>
      </div>`;
    } else {
      recEl.innerHTML = `
        ${rec.topics_to_learn_next?.length ? `<h4 style="font-size:var(--fs-xs);color:var(--color-accent);text-transform:uppercase;">Learn next</h4><ul>${rec.topics_to_learn_next.map((t) => `<li>${EduGenieUI.escapeHtml(t)}</li>`).join("")}</ul>` : ""}
        ${rec.topics_to_revise?.length ? `<h4 style="font-size:var(--fs-xs);color:var(--color-accent);text-transform:uppercase;margin-top:var(--space-sm);">Revise</h4><ul>${rec.topics_to_revise.map((t) => `<li>${EduGenieUI.escapeHtml(t)}</li>`).join("")}</ul>` : ""}
        <p class="field-hint" style="margin-top:var(--space-sm);">${EduGenieUI.escapeHtml(rec.disclaimer || "")}</p>
      `;
    }
  } catch (err) {
    EduGenieUI.toast(err.message, "error");
  }
})();
