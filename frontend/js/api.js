/**
 * EduGenie centralized API client.
 * Every network call in the frontend goes through this module so base URL,
 * auth headers, JSON parsing, and error handling stay consistent.
 */
const EduGenieAPI = (() => {
  // Auto-detect: same-origin in production, localhost:8000 during local dev
  // when the frontend is opened as a separate static file server.
  const DEFAULT_LOCAL_API = "http://127.0.0.1:8000";
  const API_BASE =
    window.EDUGENIE_API_BASE_URL ||
    (window.location.port && window.location.port !== "8000" ? DEFAULT_LOCAL_API : "");

  function getToken() {
    return localStorage.getItem("edugenie_token");
  }

  function setToken(token) {
    localStorage.setItem("edugenie_token", token);
  }

  function clearToken() {
    localStorage.removeItem("edugenie_token");
  }

  function setUser(user) {
    localStorage.setItem("edugenie_user", JSON.stringify(user));
  }

  function getUser() {
    const raw = localStorage.getItem("edugenie_user");
    return raw ? JSON.parse(raw) : null;
  }

  function clearUser() {
    localStorage.removeItem("edugenie_user");
  }

  async function request(path, { method = "GET", body, auth = true } = {}) {
    const headers = { "Content-Type": "application/json" };
    if (auth) {
      const token = getToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
    } catch (networkErr) {
      throw new APIError(
        "Could not reach the EduGenie server. Check your connection and try again.",
        0
      );
    }

    let data = null;
    const text = await response.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = null;
      }
    }

    if (!response.ok) {
      if (response.status === 401) {
        clearToken();
        clearUser();
      }
      const detail =
        (data && (data.detail || data.message)) ||
        "Something went wrong. Please try again.";
      throw new APIError(
        typeof detail === "string" ? detail : "Something went wrong. Please try again.",
        response.status
      );
    }

    return data;
  }

  class APIError extends Error {
    constructor(message, status) {
      super(message);
      this.status = status;
    }
  }

  return {
    // auth
    register: (payload) => request("/api/auth/register", { method: "POST", body: payload, auth: false }),
    login: (payload) => request("/api/auth/login", { method: "POST", body: payload, auth: false }),
    me: () => request("/api/auth/me"),

    // users / profile
    updateProfile: (payload) => request("/api/users/me", { method: "PUT", body: payload }),
    getPreferences: () => request("/api/users/me/preferences"),
    updatePreferences: (payload) => request("/api/users/me/preferences", { method: "PUT", body: payload }),
    getProfileStats: () => request("/api/users/me/stats"),

    // assistant
    askQuestion: (payload) => request("/api/assistant/ask", { method: "POST", body: payload }),
    listConversations: () => request("/api/assistant/conversations"),
    getConversationMessages: (id) => request(`/api/assistant/conversations/${id}`),

    // concepts
    explainConcept: (payload) => request("/api/concepts/explain", { method: "POST", body: payload }),
    conceptHistory: () => request("/api/concepts/history"),

    // quizzes
    generateQuiz: (payload) => request("/api/quizzes/generate", { method: "POST", body: payload }),
    getQuiz: (id) => request(`/api/quizzes/${id}`),
    submitQuiz: (payload) => request("/api/quizzes/submit", { method: "POST", body: payload }),

    // summaries
    generateSummary: (payload) => request("/api/summaries/generate", { method: "POST", body: payload }),
    summaryHistory: () => request("/api/summaries/history"),

    // learning paths
    generateLearningPath: (payload) => request("/api/learning-paths/generate", { method: "POST", body: payload }),
    listLearningPaths: () => request("/api/learning-paths"),
    getLearningPath: (id) => request(`/api/learning-paths/${id}`),
    setTopicComplete: (topicId, completed) =>
      request(`/api/learning-paths/topics/${topicId}/complete`, { method: "PUT", body: { completed } }),

    // dashboard & history
    getDashboard: () => request("/api/dashboard"),
    getHistory: (activityType) =>
      request(`/api/history${activityType ? `?activity_type=${encodeURIComponent(activityType)}` : ""}`),
    deleteHistoryItem: (id) => request(`/api/history/${id}`, { method: "DELETE" }),

    // token/user helpers
    getToken,
    setToken,
    clearToken,
    getUser,
    setUser,
    clearUser,
    APIError,
  };
})();
