/* Shamix Prep SAT - API Client & Authentication Layer */

const API_BASE = "/api";
const TOKEN_KEY = "shamix_token";

const ShamixApi = {
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token) {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  },

  clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  },

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith("/") ? `${API_BASE}${endpoint}` : `${API_BASE}/${endpoint}`;
    const token = this.getToken();

    const headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(options.headers || {})
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutMs = options.timeout || 10000;
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (response.status === 401) {
        this.clearToken();
        if (typeof window.onUnauthorized === "function") {
          window.onUnauthorized();
        }
        let detail = "Session expired. Please log in again.";
        try {
          const errData = await response.json();
          if (errData && errData.detail) detail = errData.detail;
        } catch (e) {}
        throw new Error(detail);
      }

      if (!response.ok) {
        let errorMessage = `Server error (${response.status})`;
        try {
          const errData = await response.json();
          if (errData && errData.detail) {
            if (Array.isArray(errData.detail)) {
              errorMessage = errData.detail.map(d => d.msg || d).join(", ");
            } else {
              errorMessage = errData.detail;
            }
          }
        } catch (e) {}
        throw new Error(errorMessage);
      }

      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === "AbortError") {
        throw new Error("Network request timed out. Please check your connection and try again.");
      }
      if (error.message && (error.message.includes("Failed to fetch") || error.message.includes("NetworkError"))) {
        throw new Error("Unable to connect to Shamix Prep server. Please verify your internet connection.");
      }
      throw error;
    }
  },

  // Auth endpoints
  async login(username, password) {
    const res = await this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
    if (res && res.access_token) {
      this.setToken(res.access_token);
    }
    return res;
  },

  async register(username, email, password, display_name) {
    const res = await this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password, display_name })
    });
    if (res && res.access_token) {
      this.setToken(res.access_token);
    }
    return res;
  },

  async getMe() {
    return await this.request("/auth/me");
  },

  async updateMe(data) {
    return await this.request("/auth/me", {
      method: "PATCH",
      body: JSON.stringify(data)
    });
  },

  // Dashboard
  async getDashboard() {
    return await this.request("/dashboard");
  },

  // Lessons
  async getLessons() {
    return await this.request("/lessons");
  },

  async getLesson(id) {
    return await this.request(`/lessons/${id}`);
  },

  async updateLessonProgress(id, watched_seconds, completed = false) {
    return await this.request(`/lessons/${id}/progress`, {
      method: "POST",
      body: JSON.stringify({ watched_seconds, completed })
    });
  },

  // Homework
  async getHomework(status = null) {
    const query = status && status !== "all" ? `?status=${encodeURIComponent(status)}` : "";
    return await this.request(`/homework${query}`);
  },

  async getHomeworkDetail(id) {
    return await this.request(`/homework/${id}`);
  },

  async startHomework(id) {
    return await this.request(`/homework/${id}/start`, { method: "POST" });
  },

  async submitAnswer(homeworkId, questionId, selectedIndex) {
    return await this.request(`/homework/${homeworkId}/answer?question_id=${questionId}`, {
      method: "POST",
      body: JSON.stringify({ selected_index: selectedIndex })
    });
  },

  async submitHomework(homeworkId) {
    return await this.request(`/homework/${homeworkId}/submit`, { method: "POST" });
  },

  // Leaderboard
  async getLeaderboard(period = "week") {
    return await this.request(`/leaderboard?period=${encodeURIComponent(period)}`);
  },

  // Attendance
  async getAttendance(month = null) {
    const query = month ? `?month=${encodeURIComponent(month)}` : "";
    return await this.request(`/attendance${query}`);
  },

  async checkIn() {
    return await this.request("/attendance/check-in", { method: "POST" });
  },

  // Flashcards
  async getFlashcards() {
    return await this.request("/flashcards");
  },

  // Badges
  async getBadges() {
    return await this.request("/badges");
  }
};

window.ShamixApi = ShamixApi;
