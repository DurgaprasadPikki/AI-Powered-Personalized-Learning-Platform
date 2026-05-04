const API_BASE = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    getHeaders(isFormData = false) {
        const headers = {};
        if (!isFormData) {
            headers['Content-Type'] = 'application/json';
        }
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, method = 'GET', data = null) {
        const url = `${API_BASE}${endpoint}`;
        const options = {
            method,
            headers: this.getHeaders()
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `HTTP ${response.status}`);
            }

            return result;
        } catch (error) {
            console.error(`API Error: ${error.message}`);
            throw error;
        }
    }

    // ======================== AUTH ========================
    async register(email, username, password) {
        return this.request('/auth/register', 'POST', { email, username, password });
    }

    async login(email, password) {
        const response = await this.request('/auth/login', 'POST', { email, password });
        if (response.token) {
            this.setToken(response.token);
        }
        return response;
    }

    async getProfile() {
        return this.request('/auth/profile', 'GET');
    }

    // ======================== TOPICS ========================
    async getTopics() {
        return this.request('/topics', 'GET');
    }

    async getTopicDetails(topicId) {
        return this.request(`/topics/${topicId}`, 'GET');
    }

    async getQuizQuestions(topicId, difficulty = null, limit = 5) {
        let url = `/quiz/questions/${topicId}?limit=${limit}`;
        if (difficulty) {
            url += `&difficulty=${difficulty}`;
        }
        return this.request(url, 'GET');
    }

    // ======================== QUIZ ========================
    async submitAnswer(questionId, selectedAnswer, timeSpent) {
        return this.request('/quiz/submit', 'POST', {
            question_id: questionId,
            selected_answer: selectedAnswer,
            time_spent: timeSpent
        });
    }

    async getNextQuestion(topicId) {
        return this.request(`/quiz/next/${topicId}`, 'GET');
    }

    async getQuizStatistics(topicId) {
        return this.request(`/quiz/statistics/${topicId}`, 'GET');
    }

    // ======================== PROGRESS ========================
    async getDashboard() {
        return this.request('/progress/dashboard', 'GET');
    }

    // ======================== RECOMMENDATIONS ========================
    async getRecommendations() {
        return this.request('/recommendations', 'GET');
    }

    // ======================== HEALTH CHECK ========================
    async healthCheck() {
        return this.request('/health', 'GET');
    }
}

const apiClient = new APIClient();
