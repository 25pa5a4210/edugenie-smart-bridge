(function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("summarizer.html", "Summarizer");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  const MAX_CHARS = 20000;
  let summaryType = "Short Summary";
  let detailLevel = "Standard";

  const textarea = document.getElementById("sourceText");
  const charCount = document.getElementById("charCount");

  textarea.addEventListener("input", () => {
    charCount.textContent = `${textarea.value.length.toLocaleString()} / ${MAX_CHARS.toLocaleString()} characters`;
    charCount.style.color = textarea.value.length > MAX_CHARS ? "var(--color-coral)" : "";
  });

  document.querySelectorAll("#typePills .option-pill").forEach((p) =>
    p.addEventListener("click", () => {
      document.querySelectorAll("#typePills .option-pill").forEach((x) => x.classList.remove("active"));
      p.classList.add("active");
      summaryType = p.dataset.val;
    })
  );
  document.querySelectorAll("#levelPills .option-pill").forEach((p) =>
    p.addEventListener("click", () => {
      document.querySelectorAll("#levelPills .option-pill").forEach((x) => x.classList.remove("active"));
      p.classList.add("active");
      detailLevel = p.dataset.val;
    })
  );

  document.getElementById("clearBtn").addEventListener("click", () => {
    textarea.value = "";
    charCount.textContent = `0 / ${MAX_CHARS.toLocaleString()} characters`;
    document.getElementById("resultContainer").innerHTML = "";
  });

  document.getElementById("summaryForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = textarea.value.trim();
    if (!text) {
      EduGenieUI.toast("Please paste some text to summarize.", "error");
      return;
    }
    if (text.length > MAX_CHARS) {
      EduGenieUI.toast(`Text exceeds the maximum of ${MAX_CHARS.toLocaleString()} characters.`, "error");
      return;
    }

    const btn = document.getElementById("submitBtn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Summarizing...`;
    const resultContainer = document.getElementById("resultContainer");
    resultContainer.innerHTML = `<div class="card"><div class="skeleton" style="height:80px;"></div></div>`;

    try {
      const data = await EduGenieAPI.generateSummary({ text, summary_type: summaryType, detail_level: detailLevel });
      renderResult(data);
    } catch (err) {
      resultContainer.innerHTML = `<div class="card state-block"><h4>Couldn't generate a summary</h4><p>${EduGenieUI.escapeHtml(err.message)}</p></div>`;
      EduGenieUI.toast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Summarize";
    }
  });

  function renderResult(data) {
    const r = data.result;
    const fullText = `${r.main_summary}\n\nKey Concepts:\n${r.key_concepts.join("\n")}\n\nImportant Points:\n${r.important_points.join("\n")}\n\nImportant Terms:\n${r.important_terms.join("\n")}\n\nQuick Revision:\n${r.quick_revision}`;

    document.getElementById("resultContainer").innerHTML = `
      <div class="card">
        <div class="flex justify-between items-center" style="margin-bottom:var(--space-sm);">
          <div class="eyebrow">${EduGenieUI.escapeHtml(data.summary_type)} · ${EduGenieUI.escapeHtml(data.detail_level)}</div>
          <div class="flex gap-xs">
            <button class="btn btn-secondary btn-sm" id="copyBtn">Copy Summary</button>
            <button class="btn btn-secondary btn-sm" id="downloadBtn">Download .txt</button>
          </div>
        </div>
        <h4>Main Summary</h4>
        <p>${EduGenieUI.escapeHtml(r.main_summary)}</p>
        <div class="concept-result-grid">
          <div class="concept-block"><h4>Key Concepts</h4><ul>${r.key_concepts.map((k) => `<li>${EduGenieUI.escapeHtml(k)}</li>`).join("")}</ul></div>
          <div class="concept-block"><h4>Important Points</h4><ul>${r.important_points.map((k) => `<li>${EduGenieUI.escapeHtml(k)}</li>`).join("")}</ul></div>
          <div class="concept-block full"><h4>Important Terms</h4><ul>${r.important_terms.map((k) => `<li>${EduGenieUI.escapeHtml(k)}</li>`).join("")}</ul></div>
          <div class="concept-block full"><h4>Quick Revision</h4><p>${EduGenieUI.escapeHtml(r.quick_revision)}</p></div>
        </div>
      </div>`;

    document.getElementById("copyBtn").addEventListener("click", () => {
      navigator.clipboard.writeText(fullText);
      EduGenieUI.toast("Summary copied to clipboard", "success", 2000);
    });
    document.getElementById("downloadBtn").addEventListener("click", () => {
      const blob = new Blob([fullText], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "edugenie-summary.txt";
      a.click();
      URL.revokeObjectURL(url);
    });
  }
})();
