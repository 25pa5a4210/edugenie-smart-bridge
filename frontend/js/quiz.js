(function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("quiz.html", "Quiz Generator");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  const quizArea = document.getElementById("quizArea");
  let currentQuiz = null;
  let currentIndex = 0;
  let userAnswers = {}; // question_id -> selected_answer
  let lastConfig = null;

  function showForm() {
    quizArea.innerHTML = document.getElementById("tpl-quiz-form").innerHTML;
    bindFormEvents();
  }

  function bindFormEvents() {
    let difficulty = "Easy";
    let count = "5";
    let quizType = "Multiple Choice Questions";

    document.querySelectorAll("#difficultyPills .option-pill").forEach((p) =>
      p.addEventListener("click", () => selectPill(p, "#difficultyPills", (v) => (difficulty = v)))
    );
    document.querySelectorAll("#countPills .option-pill").forEach((p) =>
      p.addEventListener("click", () => selectPill(p, "#countPills", (v) => (count = v)))
    );
    document.querySelectorAll("#typePills .option-pill").forEach((p) =>
      p.addEventListener("click", () => selectPill(p, "#typePills", (v) => (quizType = v)))
    );

    function selectPill(pill, scopeSelector, setter) {
      document.querySelectorAll(`${scopeSelector} .option-pill`).forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      setter(pill.dataset.val);
    }

    document.getElementById("quizForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const topic = document.getElementById("topic").value.trim();
      if (!topic) return;

      lastConfig = {
        topic,
        subject: document.getElementById("subject").value.trim(),
        difficulty,
        num_questions: parseInt(count, 10),
        quiz_type: quizType,
      };

      const btn = document.getElementById("generateBtn");
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner"></span> Generating quiz...`;

      try {
        const quiz = await EduGenieAPI.generateQuiz(lastConfig);
        currentQuiz = quiz;
        currentIndex = 0;
        userAnswers = {};
        renderQuestion();
      } catch (err) {
        EduGenieUI.toast(err.message, "error");
        btn.disabled = false;
        btn.textContent = "Generate Quiz";
      }
    });
  }

  function renderQuestion() {
    const q = currentQuiz.questions[currentIndex];
    const total = currentQuiz.questions.length;
    const pct = Math.round((currentIndex / total) * 100);
    const difficultyClass = { Easy: "badge-easy", Medium: "badge-medium", Hard: "badge-hard" }[currentQuiz.difficulty] || "badge-medium";

    quizArea.innerHTML = `
      <div class="card">
        <div class="flex justify-between items-center" style="margin-bottom:var(--space-md);">
          <span class="badge ${difficultyClass}">${EduGenieUI.escapeHtml(currentQuiz.difficulty)}</span>
          <span class="text-faint" style="font-size:var(--fs-xs);">${EduGenieUI.escapeHtml(currentQuiz.topic)}</span>
        </div>
        <div class="quiz-progress-row">
          <div class="progress-track"><div class="progress-fill" style="width:${pct}%;"></div></div>
          <span class="text-muted" style="font-size:var(--fs-xs);white-space:nowrap;">Question ${currentIndex + 1} of ${total}</span>
        </div>
        <h3>${EduGenieUI.escapeHtml(q.question_text)}</h3>
        <div id="optionsList">
          ${q.options
            .map(
              (opt, i) => `
            <div class="quiz-option ${userAnswers[q.id] === opt ? "selected" : ""}" data-opt="${EduGenieUI.escapeHtml(opt)}">
              <span class="quiz-option-letter">${String.fromCharCode(65 + i)}</span>
              <span>${EduGenieUI.escapeHtml(opt)}</span>
            </div>`
            )
            .join("")}
        </div>
        <div class="quiz-nav-row">
          <button class="btn btn-secondary" id="prevBtn" ${currentIndex === 0 ? "disabled" : ""}>Previous</button>
          <button class="btn btn-primary" id="nextBtn">${currentIndex === total - 1 ? "Submit Quiz" : "Next Question"}</button>
        </div>
      </div>`;

    document.querySelectorAll("#optionsList .quiz-option").forEach((el) => {
      el.addEventListener("click", () => {
        userAnswers[q.id] = el.dataset.opt;
        document.querySelectorAll("#optionsList .quiz-option").forEach((o) => o.classList.remove("selected"));
        el.classList.add("selected");
      });
    });

    document.getElementById("prevBtn").addEventListener("click", () => {
      currentIndex = Math.max(0, currentIndex - 1);
      renderQuestion();
    });
    document.getElementById("nextBtn").addEventListener("click", () => {
      if (currentIndex < total - 1) {
        currentIndex++;
        renderQuestion();
      } else {
        submitQuiz();
      }
    });
  }

  async function submitQuiz() {
    const answers = Object.entries(userAnswers).map(([question_id, selected_answer]) => ({
      question_id: parseInt(question_id, 10),
      selected_answer,
    }));

    quizArea.innerHTML = `<div class="card"><div class="skeleton" style="height:120px;"></div></div>`;

    try {
      const result = await EduGenieAPI.submitQuiz({ quiz_id: currentQuiz.id, answers });
      renderResults(result);
    } catch (err) {
      EduGenieUI.toast(err.message, "error");
    }
  }

  function renderResults(result) {
    const scoreColor = result.percentage >= 70 ? "var(--color-success)" : result.percentage >= 40 ? "var(--color-accent)" : "var(--color-coral)";

    quizArea.innerHTML = `
      <div class="card">
        <div class="score-ring-wrap">
          <h2 style="color:${scoreColor};font-size:var(--fs-4xl);">${result.percentage}%</h2>
          <p>You scored ${result.score} out of ${result.total_questions}</p>
          <div class="flex gap-sm" style="justify-content:center;margin-top:var(--space-md);">
            <button class="btn btn-secondary" id="retakeBtn">Retake Quiz</button>
            <button class="btn btn-primary" id="newQuizBtn">Generate Another Quiz</button>
          </div>
        </div>
      </div>
      <h3 style="margin-top:var(--space-lg);">Review answers</h3>
      <div id="reviewList"></div>
    `;

    const reviewList = document.getElementById("reviewList");
    reviewList.innerHTML = result.results
      .map(
        (r, i) => `
      <div class="card" style="margin-bottom:var(--space-sm);">
        <div class="flex justify-between items-center">
          <strong>Q${i + 1}. ${EduGenieUI.escapeHtml(r.question_text)}</strong>
          <span class="badge ${r.is_correct ? "badge-success" : "badge-danger"}">${r.is_correct ? "Correct" : "Incorrect"}</span>
        </div>
        <p style="margin-top:var(--space-xs);">Your answer: <strong>${EduGenieUI.escapeHtml(r.selected_answer || "No answer")}</strong></p>
        ${!r.is_correct ? `<p>Correct answer: <strong style="color:var(--color-success);">${EduGenieUI.escapeHtml(r.correct_answer)}</strong></p>` : ""}
        <p class="text-muted" style="font-size:var(--fs-sm);">${EduGenieUI.escapeHtml(r.explanation)}</p>
      </div>`
      )
      .join("");

    document.getElementById("retakeBtn").addEventListener("click", () => {
      currentIndex = 0;
      userAnswers = {};
      renderQuestion();
    });
    document.getElementById("newQuizBtn").addEventListener("click", showForm);
  }

  showForm();
})();
