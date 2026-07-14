(function () {
  if (!EduGenieUI.requireAuth()) return;

  EduGenieLayout.render("assistant.html", "AI Assistant");
  document.getElementById("page-content").innerHTML = document.getElementById("tpl-content").innerHTML;
  EduGenieUI.populateUserChrome();

  let conversationId = null;
  const messagesEl = document.getElementById("chatMessages");
  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const suggestedEl = document.getElementById("suggestedQuestions");

  document.getElementById("newChatBtn").addEventListener("click", () => {
    conversationId = null;
    renderEmptyState();
    suggestedEl.classList.remove("hidden");
  });

  suggestedEl.querySelectorAll("[data-q]").forEach((btn) => {
    btn.addEventListener("click", () => {
      input.value = btn.getAttribute("data-q");
      form.dispatchEvent(new Event("submit"));
    });
  });

  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 140) + "px";
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event("submit"));
    }
  });

  function renderEmptyState() {
    messagesEl.innerHTML = `
      <div class="state-block">
        <div class="state-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 18h.01M9.5 9a2.5 2.5 0 015 0c0 1.5-2 2-2.5 3.5M12 3a9 9 0 100 18 9 9 0 000-18z"/></svg></div>
        <h4>Ask your first question</h4>
        <p>EduGenie is ready to help you understand any topic.</p>
      </div>`;
  }

  function addMessage(role, content, messageId) {
    const bubble = document.createElement("div");
    bubble.className = `chat-msg ${role}`;
    bubble.innerHTML = EduGenieUI.escapeHtml(content).replace(/\n/g, "<br>");
    if (role === "assistant") {
      const actions = document.createElement("div");
      actions.className = "chat-msg-actions";
      actions.innerHTML = `<button type="button" data-copy>Copy</button>`;
      actions.querySelector("[data-copy]").addEventListener("click", () => {
        navigator.clipboard.writeText(content);
        EduGenieUI.toast("Copied to clipboard", "success", 2000);
      });
      bubble.appendChild(actions);
    }
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addTypingIndicator() {
    const el = document.createElement("div");
    el.className = "chat-msg assistant";
    el.id = "typingIndicator";
    el.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeTypingIndicator() {
    document.getElementById("typingIndicator")?.remove();
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (!question) return;

    if (messagesEl.querySelector(".state-block")) messagesEl.innerHTML = "";
    suggestedEl.classList.add("hidden");

    addMessage("user", question);
    input.value = "";
    input.style.height = "auto";
    sendBtn.disabled = true;
    addTypingIndicator();

    try {
      const data = await EduGenieAPI.askQuestion({ question, conversation_id: conversationId });
      conversationId = data.conversation_id;
      removeTypingIndicator();
      addMessage("assistant", data.answer);
    } catch (err) {
      removeTypingIndicator();
      EduGenieUI.toast(err.message, "error");
    } finally {
      sendBtn.disabled = false;
    }
  });
})();
