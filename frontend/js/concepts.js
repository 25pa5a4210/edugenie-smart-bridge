(function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("concept-explainer.html", "Concept Explainer");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  let selectedStyle = "Simple";
  document.querySelectorAll("#stylePills .option-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      document.querySelectorAll("#stylePills .option-pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      selectedStyle = pill.dataset.style;
    });
  });

  const resultContainer = document.getElementById("resultContainer");

  document.getElementById("conceptForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const topic = document.getElementById("topic").value.trim();
    if (!topic) return;

    const btn = document.getElementById("submitBtn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Thinking...`;
    resultContainer.innerHTML = renderSkeleton();

    try {
      const data = await EduGenieAPI.explainConcept({
        topic,
        subject: document.getElementById("subject").value.trim(),
        academic_level: document.getElementById("academic_level").value,
        style: selectedStyle,
      });
      renderResult(data);
    } catch (err) {
      resultContainer.innerHTML = `<div class="card state-block"><h4>Couldn't generate an explanation</h4><p>${EduGenieUI.escapeHtml(err.message)}</p></div>`;
      EduGenieUI.toast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Explain This Concept";
    }
  });

  function renderSkeleton() {
    return `<div class="card"><div class="skeleton" style="height:20px;width:40%;margin-bottom:16px;"></div>
      <div class="skeleton" style="height:60px;margin-bottom:16px;"></div>
      <div class="skeleton" style="height:60px;"></div></div>`;
  }

  function renderResult(data) {
    const r = data.result;
    resultContainer.innerHTML = `
      <div class="card">
        <div class="eyebrow">${EduGenieUI.escapeHtml(data.style)} explanation</div>
        <h3>${EduGenieUI.escapeHtml(data.topic)}</h3>
        <div class="concept-result-grid">
          <div class="concept-block full"><h4>Definition</h4><p>${EduGenieUI.escapeHtml(r.definition)}</p></div>
          <div class="concept-block full"><h4>Explanation</h4><p>${EduGenieUI.escapeHtml(r.explanation)}</p></div>
          <div class="concept-block"><h4>Real-Life Analogy</h4><p>${EduGenieUI.escapeHtml(r.real_life_analogy)}</p></div>
          <div class="concept-block"><h4>Example</h4><p>${EduGenieUI.escapeHtml(r.example)}</p></div>
          <div class="concept-block full"><h4>Important Points</h4><ul>${r.important_points.map((p) => `<li>${EduGenieUI.escapeHtml(p)}</li>`).join("")}</ul></div>
          <div class="concept-block full"><h4>Quick Recap</h4><p>${EduGenieUI.escapeHtml(r.quick_recap)}</p></div>
        </div>
      </div>`;
  }
})();
