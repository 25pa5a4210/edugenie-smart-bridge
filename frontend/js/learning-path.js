(function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("learning-path.html", "Learning Paths");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  let knowledgeLevel = "Beginner";
  let learningGoal = "Academic Learning";
  let studyTime = "1 Week";

  document.querySelectorAll("#levelPills .option-pill").forEach((p) =>
    p.addEventListener("click", () => selectPill(p, "#levelPills", (v) => (knowledgeLevel = v)))
  );
  document.querySelectorAll("#goalPills .option-pill").forEach((p) =>
    p.addEventListener("click", () => selectPill(p, "#goalPills", (v) => (learningGoal = v)))
  );
  document.querySelectorAll("#timePills .option-pill").forEach((p) =>
    p.addEventListener("click", () => selectPill(p, "#timePills", (v) => (studyTime = v)))
  );

  function selectPill(pill, scope, setter) {
    document.querySelectorAll(`${scope} .option-pill`).forEach((p) => p.classList.remove("active"));
    pill.classList.add("active");
    setter(pill.dataset.val);
  }

  // ---------------- Tabs ----------------
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const isSaved = btn.dataset.tab === "saved";
      document.getElementById("newPathTab").classList.toggle("hidden", isSaved);
      document.getElementById("savedPathTab").classList.toggle("hidden", !isSaved);
      if (isSaved) loadSavedPaths();
    });
  });
  document.getElementById("newPathBtn").addEventListener("click", () => {
    document.querySelector('.tab-btn[data-tab="new"]').click();
  });

  // ---------------- Generate ----------------
  document.getElementById("pathForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const topic = document.getElementById("topic").value.trim();
    if (!topic) return;

    const btn = document.getElementById("generateBtn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Building your roadmap...`;
    const resultEl = document.getElementById("newPathResult");
    resultEl.innerHTML = `<div class="card" style="margin-top:var(--space-lg);"><div class="skeleton" style="height:160px;"></div></div>`;

    try {
      const path = await EduGenieAPI.generateLearningPath({
        topic,
        knowledge_level: knowledgeLevel,
        learning_goal: learningGoal,
        study_time: studyTime,
      });
      resultEl.innerHTML = `<div style="margin-top:var(--space-lg);">${renderPath(path)}</div>`;
      bindTopicCheckboxes(resultEl);
      EduGenieUI.toast("Your learning roadmap is ready!", "success");
    } catch (err) {
      resultEl.innerHTML = `<div class="card state-block"><h4>Couldn't generate a roadmap</h4><p>${EduGenieUI.escapeHtml(err.message)}</p></div>`;
      EduGenieUI.toast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Generate Roadmap";
    }
  });

  // ---------------- Saved list ----------------
  async function loadSavedPaths() {
    const listEl = document.getElementById("savedPathsList");
    listEl.innerHTML = `<div class="card"><div class="skeleton" style="height:80px;"></div></div>`;
    try {
      const paths = await EduGenieAPI.listLearningPaths();
      if (!paths.length) {
        listEl.innerHTML = `<div class="card state-block">
          <h4>No saved learning paths yet</h4>
          <p>Generate a roadmap and it'll appear here automatically.</p>
        </div>`;
        return;
      }
      listEl.innerHTML = paths.map((p) => renderPath(p)).join("");
      bindTopicCheckboxes(listEl);
    } catch (err) {
      EduGenieUI.toast(err.message, "error");
    }
  }

  function renderPath(path) {
    return `
      <div class="card" style="margin-bottom:var(--space-lg);" data-path-id="${path.id}">
        <div class="flex justify-between items-center" style="margin-bottom:var(--space-2xs);">
          <h3 style="margin-bottom:0;">${EduGenieUI.escapeHtml(path.topic)}</h3>
          <span class="badge badge-info">${path.progress_percentage}% complete</span>
        </div>
        <p class="text-muted" style="font-size:var(--fs-sm);">${EduGenieUI.escapeHtml(path.knowledge_level)} · ${EduGenieUI.escapeHtml(path.learning_goal)} · ${EduGenieUI.escapeHtml(path.study_time)}</p>
        <div class="progress-track" style="margin-bottom:var(--space-md);"><div class="progress-fill" style="width:${path.progress_percentage}%;"></div></div>
        ${path.phases
          .map(
            (phase, idx) => `
          <div class="card phase-card">
            <h4>${EduGenieUI.escapeHtml(phase.title)}</h4>
            ${phase.objectives ? `<p class="text-muted" style="font-size:var(--fs-sm);">${EduGenieUI.escapeHtml(phase.objectives)}</p>` : ""}
            ${phase.topics
              .map(
                (t) => `
              <div class="phase-topic-row ${t.completed ? "completed" : ""}">
                <input type="checkbox" data-topic-id="${t.id}" ${t.completed ? "checked" : ""}>
                <span>${EduGenieUI.escapeHtml(t.title)}</span>
              </div>`
              )
              .join("")}
            <div class="phase-meta-row">
              ${phase.estimated_duration ? `<span>⏱ ${EduGenieUI.escapeHtml(phase.estimated_duration)}</span>` : ""}
              ${phase.recommended_practice ? `<span>📝 ${EduGenieUI.escapeHtml(phase.recommended_practice)}</span>` : ""}
            </div>
            ${phase.mini_task ? `<p style="margin-top:var(--space-xs);"><strong>Mini task:</strong> ${EduGenieUI.escapeHtml(phase.mini_task)}</p>` : ""}
          </div>`
          )
          .join("")}
      </div>`;
  }

  function bindTopicCheckboxes(scopeEl) {
    scopeEl.querySelectorAll("input[type=checkbox][data-topic-id]").forEach((cb) => {
      cb.addEventListener("change", async () => {
        const row = cb.closest(".phase-topic-row");
        try {
          await EduGenieAPI.setTopicComplete(cb.dataset.topicId, cb.checked);
          row.classList.toggle("completed", cb.checked);
          updateProgressBar(scopeEl.querySelector(`[data-path-id]`) || scopeEl);
        } catch (err) {
          cb.checked = !cb.checked;
          EduGenieUI.toast(err.message, "error");
        }
      });
    });
  }

  function updateProgressBar(cardEl) {
    if (!cardEl) return;
    const boxes = cardEl.querySelectorAll("input[type=checkbox][data-topic-id]");
    const checked = cardEl.querySelectorAll("input[type=checkbox][data-topic-id]:checked");
    const pct = boxes.length ? Math.round((checked.length / boxes.length) * 100) : 0;
    const fill = cardEl.querySelector(".progress-fill");
    const badge = cardEl.querySelector(".badge-info");
    if (fill) fill.style.width = pct + "%";
    if (badge) badge.textContent = `${pct}% complete`;
  }
})();
