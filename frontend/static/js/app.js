class LearningApp {
    constructor() {
        this.currentUser = null;
        this.currentTopic = null;
        this.currentQuiz = {
            topicId: null,
            questions: [],
            currentQuestionIndex: 0,
            answers: [],
            startTime: null,
            questionStartTime: null,
            correctCount: 0
        };
        this.charts = {};
        this.init();
    }

    async init() {
        // Check if user is logged in
        const token = localStorage.getItem('auth_token');
        if (token) {
            try {
                await this.loadUserProfile();
                this.showPage('dashboard-page');
                await this.loadDashboard();
            } catch (error) {
                console.error('Auth error:', error);
                this.logout();
            }
        } else {
            this.showPage('auth-page');
        }
    }

    // ======================== NAVIGATION ========================
    showPage(pageId) {
        document.querySelectorAll('.page').forEach(page => {
            page.classList.add('hidden');
        });
        document.getElementById(pageId).classList.remove('hidden');

        // Hide navbar on auth page
        const navbar = document.querySelector('.navbar');
        if (pageId === 'auth-page') {
            navbar.style.display = 'none';
        } else {
            navbar.style.display = '';
        }
    }

    navigateTo(section) {
        switch (section) {
            case 'dashboard':
                this.showPage('dashboard-page');
                this.loadDashboard();
                break;
            case 'topics':
                this.showPage('topics-page');
                this.loadTopics();
                break;
            case 'progress':
                this.showPage('progress-page');
                this.loadProgress();
                break;
        }
    }

    // ======================== AUTH HANDLERS ========================
    toggleAuthForm(event) {
        event.preventDefault();
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        loginForm.classList.toggle('active');
        registerForm.classList.toggle('active');
        document.getElementById('auth-message').innerHTML = '';
    }

    async handleLogin(event) {
        event.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            this.showLoader();
            const response = await apiClient.login(email, password);
            this.currentUser = response.user;
            this.showToast('Login successful!', 'success');
            this.showPage('dashboard-page');
            await this.loadDashboard();
        } catch (error) {
            this.showMessage('auth-message', error.message, 'error');
        } finally {
            this.hideLoader();
        }
    }

    async handleRegister(event) {
        event.preventDefault();
        const email = document.getElementById('registerEmail').value;
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;

        try {
            this.showLoader();
            const response = await apiClient.register(email, username, password);
            this.showMessage('auth-message', 'Registration successful! You can now log in.', 'success');
            
            setTimeout(() => {
                document.getElementById('register-form').classList.remove('active');
                document.getElementById('login-form').classList.add('active');
                document.getElementById('loginEmail').value = email;
            }, 1500);
        } catch (error) {
            this.showMessage('auth-message', error.message, 'error');
        } finally {
            this.hideLoader();
        }
    }

    async logout() {
        apiClient.clearToken();
        this.currentUser = null;
        this.showToast('Logged out successfully', 'success');
        this.showPage('auth-page');
        document.getElementById('login-form').classList.add('active');
        document.getElementById('register-form').classList.remove('active');
    }

    async loadUserProfile() {
        try {
            this.currentUser = await apiClient.getProfile();
        } catch (error) {
            throw error;
        }
    }

    // ======================== DASHBOARD ========================
    async loadDashboard() {
        try {
            this.showLoader();
            const dashboardData = await apiClient.getDashboard();

            // Update header
            document.getElementById('username').textContent = dashboardData.user.username;
            document.getElementById('userLevel').textContent = dashboardData.user.current_level;
            document.getElementById('totalPoints').textContent = dashboardData.user.total_points;
            document.getElementById('avgAccuracy').textContent = 
                dashboardData.statistics.average_accuracy.toFixed(1) + '%';
            document.getElementById('topicsStudied').textContent = dashboardData.statistics.topics_studied;

            // Render performance chart
            this.renderPerformanceChart(dashboardData.statistics);

            // Render recommendations
            await this.renderRecommendations();

            // Render insights
            this.renderInsights(dashboardData.insights);

            // Render progress
            this.renderProgressByTopic(dashboardData.progress_by_topic);
        } catch (error) {
            console.error('Dashboard load error:', error);
            this.showToast('Error loading dashboard', 'error');
        } finally {
            this.hideLoader();
        }
    }

    renderPerformanceChart(stats) {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        if (this.charts.performance) {
            this.charts.performance.destroy();
        }

        this.charts.performance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Accuracy', 'Remaining'],
                datasets: [{
                    data: [stats.average_accuracy, 100 - stats.average_accuracy],
                    backgroundColor: ['#10b981', '#e2e8f0'],
                    borderColor: ['#10b981', '#e2e8f0']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    async renderRecommendations() {
        try {
            const response = await apiClient.getRecommendations();
            const container = document.getElementById('recommendations-list');

            if (!response.recommendations || response.recommendations.length === 0) {
                container.innerHTML = '<p class="loading">No recommendations yet. Complete more quizzes!</p>';
                return;
            }

            container.innerHTML = response.recommendations.map((rec, idx) => `
                <div class="recommendation-item">
                    <h4>${idx + 1}. ${rec.topic_name}</h4>
                    <div>
                        <span class="score">${(rec.score * 100).toFixed(0)}% match</span>
                        <span class="reason">${rec.reason}</span>
                    </div>
                    <small>Difficulty: ${rec.difficulty}</small>
                </div>
            `).join('');
        } catch (error) {
            console.error('Recommendations error:', error);
        }
    }

    renderInsights(insights) {
        const container = document.getElementById('insights-container');
        let html = '';

        if (insights.overall_accuracy > 0) {
            html += `<div class="insight-item">
                <strong>Overall Accuracy:</strong> ${insights.overall_accuracy}%
            </div>`;
        }

        if (insights.improvement_trend) {
            html += `<div class="insight-item">
                <strong>Trend:</strong> ${insights.improvement_trend} 📈
            </div>`;
        }

        if (insights.recommended_focus) {
            html += `<div class="insight-item">
                <strong>Recommendation:</strong> ${insights.recommended_focus}
            </div>`;
        }

        if (!html) {
            html = '<p class="loading">Complete more quizzes to get insights</p>';
        }

        container.innerHTML = html;
    }

    renderProgressByTopic(progressData) {
        const container = document.getElementById('progress-list');

        if (!progressData || progressData.length === 0) {
            container.innerHTML = '<p class="loading">No progress data yet</p>';
            return;
        }

        container.innerHTML = progressData.map(p => `
            <div class="progress-item">
                <span class="progress-item-name">Topic ID: ${p.topic_id.substring(0, 8)}</span>
                <div class="progress-item-bar">
                    <div class="progress-item-fill" style="width: ${p.accuracy}%"></div>
                </div>
                <span class="progress-item-stats">${p.accuracy.toFixed(1)}% (${p.questions_answered} Q)</span>
            </div>
        `).join('');
    }

    // ======================== TOPICS ========================
    async loadTopics() {
    try {
        this.showLoader();
        const response = await apiClient.getTopics();

        console.log("Topics API Response:", response.topics); // ✅ ADD HERE

        this.cachedTopics = response.topics;  // ✅ ALSO ADD THIS
        this.renderTopics(this.cachedTopics);

        } catch (error) {
            console.error('Topics load error:', error);
            this.showToast('Error loading topics', 'error');
        } finally {
            this.hideLoader();
        }
    }

    renderTopics(topics, filter = 'all') {
        const grid = document.getElementById('topicsGrid');
        const filtered = filter === 'all' ? topics : topics.filter(t => t.difficulty === filter);

        grid.innerHTML = filtered.map(topic => `
            <div class="topic-card" onclick="app.viewTopic('${topic.topic_id}')">
                <h3>${topic.name}</h3>
                <p>${topic.description}</p>
                <div class="meta">
                    <span class="difficulty ${topic.difficulty}">${topic.difficulty}</span>
                    <span class="category">${topic.category}</span>
                </div>
            </div>
        `).join('');
    }

    filterTopics(difficulty) {
        // Update filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');

        // Get topics from cache and filter
        const topics = this.cachedTopics || [];
        this.renderTopics(topics, difficulty);
    }

    async viewTopic(topicId) {
        try {
            this.showLoader();
            const topic = await apiClient.getTopicDetails(topicId);
            this.currentTopic = topic;

            document.getElementById('topicTitle').textContent = topic.name;
            document.getElementById('topicDescription').textContent = topic.description;
            document.getElementById('topicDifficulty').textContent = topic.difficulty;
            document.getElementById('topicDifficulty').className = `difficulty ${topic.difficulty}`;
            document.getElementById('topicCategory').textContent = topic.category;
            document.getElementById('topicContent').innerHTML = this.formatContent(topic.content);

            this.showPage('topic-detail-page');
        } catch (error) {
            console.error('Topic detail error:', error);
            this.showToast('Error loading topic', 'error');
        } finally {
            this.hideLoader();
        }
    }

    formatContent(content) {
        // Simple markdown-like formatting
        return content
            .split('\n')
            .map(line => {
                if (line.startsWith('# ')) return `<h3>${line.substring(2)}</h3>`;
                if (line.startsWith('- ')) return `<li>${line.substring(2)}</li>`;
                if (line.trim()) return `<p>${line}</p>`;
                return '';
            })
            .join('');
    }

    // ======================== QUIZ ========================
    async startQuiz() {
        try {
            this.showLoader();
            this.currentQuiz.topicId = this.currentTopic.topic_id;
            this.currentQuiz.questions = [];
            this.currentQuiz.currentQuestionIndex = 0;
            this.currentQuiz.answers = [];
            this.currentQuiz.correctCount = 0;
            this.currentQuiz.startTime = Date.now();

            // Load 5 questions
            const response = await apiClient.getQuizQuestions(this.currentTopic.topic_id, null, 5);
            this.currentQuiz.questions = response.questions;

            this.showPage('quiz-page');
            this.showNextQuestion();
        } catch (error) {
            console.error('Quiz start error:', error);
            this.showToast('Error starting quiz', 'error');
        } finally {
            this.hideLoader();
        }
    }

    showNextQuestion() {
        const quiz = this.currentQuiz;
        if (quiz.currentQuestionIndex >= quiz.questions.length) {
            this.endQuiz();
            return;
        }

        const question = quiz.questions[quiz.currentQuestionIndex];
        quiz.questionStartTime = Date.now();

        // Update progress
        const progress = quiz.currentQuestionIndex + 1;
        document.getElementById('questionNumber').textContent = 
            `Question ${progress} of ${quiz.questions.length}`;
        document.getElementById('progressFill').style.width = 
            `${(progress / quiz.questions.length) * 100}%`;

        // Display question
        document.getElementById('questionText').textContent = question.text;
        const optionsContainer = document.getElementById('optionsContainer');
        optionsContainer.innerHTML = question.options.map((option, idx) => `
            <div class="option" onclick="app.selectOption(${idx})">
                ${String.fromCharCode(65 + idx)}. ${option}
            </div>
        `).join('');

        // Reset feedback
        document.getElementById('feedbackContainer').classList.add('hidden');
        document.getElementById('submitBtn').style.display = 'block';
        document.getElementById('submitBtn').disabled = false;

        this.startTimer();
    }

    selectedOptionIndex = null;

    selectOption(index) {
        // Deselect previous
        document.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
        // Select new
        document.querySelectorAll('.option')[index].classList.add('selected');
        this.selectedOptionIndex = index;
    }

    async submitAnswer() {
        if (this.selectedOptionIndex === null) {
            this.showToast('Please select an answer', 'error');
            return;
        }

        try {
            const quiz = this.currentQuiz;
            const question = quiz.questions[quiz.currentQuestionIndex];
            const selectedAnswer = question.options[this.selectedOptionIndex];
            const timeSpent = Math.floor((Date.now() - quiz.questionStartTime) / 1000);

            // Submit to API
            const response = await apiClient.submitAnswer(
                question.question_id,
                selectedAnswer,
                timeSpent
            );

            // Update UI
            const feedbackContainer = document.getElementById('feedbackContainer');
            const feedbackText = document.getElementById('feedbackText');

            if (response.correct) {
                quiz.correctCount++;
                document.getElementById('correctCount').textContent = quiz.correctCount;
                feedbackContainer.className = 'feedback correct';
                feedbackText.textContent = `✓ Correct! ${response.explanation}`;
            } else {
                feedbackContainer.className = 'feedback incorrect';
                feedbackText.textContent = `✗ Incorrect. ${response.explanation}`;
            }

            feedbackContainer.classList.remove('hidden');
            document.getElementById('submitBtn').style.display = 'none';

            // Store answer
            quiz.answers.push({
                questionId: question.question_id,
                answer: selectedAnswer,
                correct: response.correct,
                timeSpent
            });

            this.selectedOptionIndex = null;
        } catch (error) {
            console.error('Submit error:', error);
            this.showToast('Error submitting answer', 'error');
        }
    }

    nextQuestion() {
        this.currentQuiz.currentQuestionIndex++;
        if (this.currentQuiz.currentQuestionIndex < this.currentQuiz.questions.length) {
            this.showNextQuestion();
        } else {
            this.showQuizComplete();
        }
    }

    showQuizComplete() {
        const quiz = this.currentQuiz;
        const accuracy = (quiz.correctCount / quiz.questions.length) * 100;

        const feedbackContainer = document.getElementById('feedbackContainer');
        feedbackContainer.className = 'feedback';
        feedbackContainer.innerHTML = `
            <div class="feedback-text">
                <h3>Quiz Complete! 🎉</h3>
                <p>You got <strong>${quiz.correctCount}</strong> out of <strong>${quiz.questions.length}</strong> correct.</p>
                <p>Accuracy: <strong>${accuracy.toFixed(1)}%</strong></p>
            </div>
            <button class="btn btn-primary" onclick="app.endQuiz()">Back to Topics</button>
        `;
        feedbackContainer.classList.remove('hidden');
        document.getElementById('submitBtn').style.display = 'none';
    }

    endQuiz() {
        this.showPage('topics-page');
        this.loadTopics();
    }

    startTimer() {
        const startTime = this.currentQuiz.startTime;
        const timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            document.getElementById('timeSpent').textContent = elapsed;

            if (!this.currentQuiz.topicId) {
                clearInterval(timerInterval);
            }
        }, 1000);
    }

    // ======================== PROGRESS ========================
    async loadProgress() {
        try {
            this.showLoader();
            const dashboardData = await apiClient.getDashboard();
            const stats = dashboardData.statistics;

            document.getElementById('totalTime').textContent = stats.total_time_spent + ' min';
            document.getElementById('accuracyRate').textContent = stats.average_accuracy.toFixed(1) + '%';
            document.getElementById('questionsAnswered').textContent = stats.total_questions_answered;

            this.renderDetailedProgress(dashboardData.progress_by_topic);
            this.renderTrendChart(dashboardData.progress_by_topic);
        } catch (error) {
            console.error('Progress load error:', error);
            this.showToast('Error loading progress', 'error');
        } finally {
            this.hideLoader();
        }
    }

    renderDetailedProgress(progressData) {
        const container = document.getElementById('detailedProgress');

        if (!progressData || progressData.length === 0) {
            container.innerHTML = '<p class="loading">No progress data yet</p>';
            return;
        }

        container.innerHTML = progressData.map(p => `
            <div class="progress-item">
                <span class="progress-item-name">Topic ${p.topic_id.substring(0, 8)}</span>
                <div class="progress-item-bar">
                    <div class="progress-item-fill" style="width: ${p.accuracy}%"></div>
                </div>
                <span class="progress-item-stats">${p.accuracy.toFixed(1)}%</span>
            </div>
        `).join('');
    }

    renderTrendChart(progressData) {
        const ctx = document.getElementById('trendChart');
        if (!ctx || !progressData || progressData.length === 0) return;

        if (this.charts.trend) {
            this.charts.trend.destroy();
        }

        const labels = progressData.slice(0, 10).map((_, i) => `Topic ${i + 1}`);
        const data = progressData.slice(0, 10).map(p => p.accuracy);

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Accuracy %',
                    data: data,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // ======================== UI UTILITIES ========================
    showLoader() {
        document.getElementById('loader').classList.remove('hidden');
    }

    hideLoader() {
        document.getElementById('loader').classList.add('hidden');
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type === 'error' ? 'error' : ''}`;
        toast.classList.remove('hidden');

        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    showMessage(elementId, message, type) {
        const element = document.getElementById(elementId);
        element.textContent = message;
        element.className = type;
        element.style.display = 'block';
    }
}

// Initialize app
const app = new LearningApp();
