(function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("history.html", "History");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  const TYPE_LABELS = {
    question: "Question", concept: "Concept", quiz: "Quiz", summary: "Summary", learning_path: "Learning Path",
  };

  document.querySelectorAll("#historyFilters .option-pill").forEach((p) => {
    p.addEventListener("click", () => {
      document.querySelectorAll("#historyFilters .option-pill").forEach((x) => x.classList.remove("active"));
      p.classList.add("active");
      loadHistory(p.dataset.type);
    });
  });

  async function loadHistory(activityType) {
    const listEl = document.getElementById("historyList");
    listEl.innerHTML = `<div class="skeleton" style="height:20px;margin-bottom:10px;"></div><div class="skeleton" style="height:20px;margin-bottom:10px;"></div><div class="skeleton" style="height:20px;"></div>`;

    try {
      const items = await EduGenieAPI.getHistory(activityType || undefined);
      if (!items.length) {
        listEl.innerHTML = `<div class="state-block">
          <div class="state-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 8v4l3 3M21 12a9 9 0 11-9-9 9 9 0 019 9z"/></svg></div>
          <h4>No history yet</h4>
          <p>Your learning activity will show up here as you use EduGenie.</p>
        </div>`;
        return;
      }
      listEl.innerHTML = items
        .map(
          (item) => `
        <div class="history-table-row" data-id="${item.id}">
          <span class="badge badge-info">${TYPE_LABELS[item.activity_type] || item.activity_type}</span>
          <span class="text-faint" style="font-size:var(--fs-xs);">${EduGenieUI.formatDateTime(item.created_at)}</span>
          <span>${EduGenieUI.escapeHtml(item.topic || "—")}</span>
          <button class="btn btn-ghost btn-sm" data-delete="${item.id}">Delete</button>
        </div>`
        )
        .join("");

      listEl.querySelectorAll("[data-delete]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          try {
            await EduGenieAPI.deleteHistoryItem(btn.dataset.delete);
            btn.closest(".history-table-row").remove();
            EduGenieUI.toast("Record deleted", "success", 2000);
          } catch (err) {
            EduGenieUI.toast(err.message, "error");
          }
        });
      });
    } catch (err) {
      listEl.innerHTML = `<div class="state-block"><h4>Couldn't load history</h4><p>${EduGenieUI.escapeHtml(err.message)}</p></div>`;
    }
  }

  loadHistory("");
})();
