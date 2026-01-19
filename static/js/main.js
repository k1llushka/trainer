/**
 * VTB Finance Tracker - Main JavaScript
 */

// Глобальные переменные
const API_BASE = '/transactions/api';
let currentCharts = {};

// Утилиты
const Utils = {
    // Форматирование чисел
    formatMoney(amount) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 2
        }).format(amount);
    },

    // Форматирование даты
    formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('ru-RU').format(date);
    },

    // Получение CSRF токена
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    // Показать уведомление
    showNotification(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    },

    // Показать загрузку
    showLoading(element) {
        element.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        `;
    }
};

// API клиент
const API = {
    async request(endpoint, options = {}) {
        const csrftoken = Utils.getCookie('csrftoken');

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin'
        };

        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    },

    // Транзакции
    async getTransactions(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/transactions/?${queryString}`);
    },

    async createTransaction(data) {
        return await this.request('/transactions/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateTransaction(id, data) {
        return await this.request(`/transactions/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async deleteTransaction(id) {
        return await this.request(`/transactions/${id}/`, {
            method: 'DELETE'
        });
    },

    // Статистика
    async getStatistics(period = 'month') {
        return await this.request(`/transactions/statistics/?period=${period}`);
    },

    // Данные для графиков
    async getChartData(type = 'monthly') {
        return await this.request(`/transactions/chart_data/?type=${type}`);
    },

    // AI рекомендации
    async getRecommendations() {
        return await this.request('/ai/recommendations/');
    },

    async getForecast() {
        return await this.request('/ai/forecast/');
    },

    async getInsights() {
        return await this.request('/ai/insights/');
    }
};

// Управление графиками
const Charts = {
    // Создать график расходов/доходов
    async createMonthlyChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    try {
        const chartData = await API.getChartData("monthly");

        if (currentCharts[canvasId]) {
            currentCharts[canvasId].destroy();
        }

        const ctx = canvas.getContext("2d");

        // === ГРАДИЕНТЫ ===
        const incomeGradient = ctx.createLinearGradient(0, 0, 0, 300);
        incomeGradient.addColorStop(0, "rgba(0, 178, 255, 0.8)");
        incomeGradient.addColorStop(1, "rgba(0, 178, 255, 0.2)");

        const expenseGradient = ctx.createLinearGradient(0, 0, 0, 300);
        expenseGradient.addColorStop(0, "rgba(255, 82, 82, 0.8)");
        expenseGradient.addColorStop(1, "rgba(255, 82, 82, 0.2)");

        // === СВЕТЯЩАЯСЯ ТЕНЬ ===
        const shadowPlugin = {
            id: "glowShadow",
            afterDatasetsDraw(chart) {
                const { ctx } = chart;
                chart.data.datasets.forEach((dataset, i) => {
                    const meta = chart.getDatasetMeta(i);
                    if (!meta.hidden) {
                        ctx.save();
                        ctx.shadowColor = dataset.borderColor;
                        ctx.shadowBlur = 18;
                        ctx.lineJoin = "round";
                        ctx.lineCap = "round";
                        ctx.strokeStyle = dataset.borderColor;
                        ctx.lineWidth = 3;

                        ctx.beginPath();
                        meta.data.forEach((point, index) => {
                            if (index === 0) ctx.moveTo(point.x, point.y);
                            else ctx.lineTo(point.x, point.y);
                        });
                        ctx.stroke();
                        ctx.restore();
                    }
                });
            }
        };

        Chart.register(shadowPlugin);

        currentCharts[canvasId] = new Chart(ctx, {
            type: "line",
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: "Доходы",
                        data: chartData.datasets[0].data,
                        borderColor: "rgba(0, 140, 255, 1)",
                        backgroundColor: incomeGradient,
                        fill: true,
                        tension: 0.35,        // плавная линия
                        borderWidth: 3,
                        pointBackgroundColor: "white",
                        pointBorderColor: "rgba(0,140,255,1)",
                        pointBorderWidth: 3,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                    },
                    {
                        label: "Расходы",
                        data: chartData.datasets[1].data,
                        borderColor: "rgba(255, 60, 60, 1)",
                        backgroundColor: expenseGradient,
                        fill: true,
                        tension: 0.35,
                        borderWidth: 3,
                        pointBackgroundColor: "white",
                        pointBorderColor: "rgba(255,60,60,1)",
                        pointBorderWidth: 3,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            font: { size: 14 }
                        }
                    },
                    tooltip: {
                        backgroundColor: "rgba(0,0,0,0.7)",
                        titleFont: { weight: "bold" },
                        callbacks: {
                            label: function(ctx) {
                                return `${ctx.dataset.label}: ${Utils.formatMoney(ctx.raw)}`;
                            }
                        }
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: "rgba(200,200,200,0.3)"
                        },
                        ticks: {
                            callback: value => Utils.formatMoney(value)
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                },

                // Красивая анимация
                animation: {
                    duration: 2000,
                    easing: "easeOutQuart"
                }
            }
        });

    } catch (error) {
        console.error("Ошибка построения графика доходов/расходов:", error);
    }
},

    // Создать круговую диаграмму категорий
    async createCategoryChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        try {
            const chartData = await API.getChartData('category');

            if (currentCharts[canvasId]) {
                currentCharts[canvasId].destroy();
            }

            const preparedData = {
                labels: chartData.labels,
                datasets: chartData.datasets.map(dataset => ({
                    ...dataset,
                    backgroundColor: dataset.backgroundColor?.length
                        ? dataset.backgroundColor
                        : dataset.data.map(() => '#6c757d'),
                    borderColor: 'transparent',
                    borderWidth: 0,
                    borderRadius: 18,
                    spacing: 6,
                    hoverOffset: 10,
                }))
            };

            const ctx = canvas.getContext('2d');
            currentCharts[canvasId] = new Chart(ctx, {
                type: 'doughnut',
                  data: preparedData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '55%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                usePointStyle: true,
                                pointStyle: 'circle',
                                boxWidth: 12,
                                boxHeight: 12,
                                padding: 12,
                            }
                        },
                        title: {
                            display: true,
                            text: 'Расходы по категориям'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = Utils.formatMoney(context.parsed);
                                    return `${label}: ${value}`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error creating category chart:', error);
        }
    },

    // Создать график тренда
    async createTrendChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        try {
            const data = await API.getChartData('trend');

            if (currentCharts[canvasId]) {
                currentCharts[canvasId].destroy();
            }

            const ctx = canvas.getContext('2d');
            currentCharts[canvasId] = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Тренд баланса (30 дней)'
                        }
                    },
                    scales: {
                        y: {
                            ticks: {
                                callback: function(value) {
                                    return Utils.formatMoney(value);
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error creating trend chart:', error);
        }
    }
};

// Управление статистикой
const Statistics = {
    async loadStatistics(period = 'month') {
        const container = document.getElementById('statistics-container');
        if (!container) return;

        try {
            Utils.showLoading(container);
            const stats = await API.getStatistics(period);

            container.innerHTML = `
                <div class="row g-3">
                    <div class="col-md-3">
                        <div class="card bg-success text-white">
                            <div class="card-body">
                                <h6 class="card-title">
                                    <i class="bi bi-arrow-up-circle me-2"></i>
                                    Доходы
                                </h6>
                                <h3 class="mb-0">${Utils.formatMoney(stats.total_income)}</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-danger text-white">
                            <div class="card-body">
                                <h6 class="card-title">
                                    <i class="bi bi-arrow-down-circle me-2"></i>
                                    Расходы
                                </h6>
                                <h3 class="mb-0">${Utils.formatMoney(stats.total_expense)}</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card ${stats.balance >= 0 ? 'bg-primary' : 'bg-warning'} text-white">
                            <div class="card-body">
                                <h6 class="card-title">
                                    <i class="bi bi-wallet2 me-2"></i>
                                    Баланс
                                </h6>
                                <h3 class="mb-0">${Utils.formatMoney(stats.balance)}</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-info text-white">
                            <div class="card-body">
                                <h6 class="card-title">
                                    <i class="bi bi-graph-up me-2"></i>
                                    Средний чек
                                </h6>
                                <h3 class="mb-0">${Utils.formatMoney(stats.avg_transaction)}</h3>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading statistics:', error);
            Utils.showNotification('Ошибка загрузки статистики', 'danger');
        }
    }
};

// рекомендации
const AI = {
    async loadRecommendations() {
        const container = document.getElementById('recommendations-container');
        if (!container) return;

        try {
            Utils.showLoading(container);
            const recommendations = await API.getRecommendations();

            if (recommendations.length === 0) {
                container.innerHTML = `
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        Пока нет рекомендаций. Добавьте больше транзакций для анализа.
                    </div>
                `;
                return;
            }

            const priorityColors = {
                'high': 'danger',
                'medium': 'warning',
                'low': 'info'
            };

            const typeIcons = {
                'warning': 'bi-exclamation-triangle',
                'alert': 'bi-exclamation-circle',
                'info': 'bi-info-circle',
                'success': 'bi-check-circle'
            };

            container.innerHTML = recommendations.map(rec => `
                <div class="alert alert-${priorityColors[rec.priority] || 'info'} d-flex align-items-start">
                    <i class="${typeIcons[rec.type] || 'bi-info-circle'} fs-4 me-3"></i>
                    <div class="flex-grow-1">
                        <h6 class="alert-heading mb-1">${rec.title}</h6>
                        <p class="mb-0">${rec.message}</p>
                        ${rec.amount ? `<small class="text-muted">Сумма: ${Utils.formatMoney(rec.amount)}</small>` : ''}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading recommendations:', error);
            Utils.showNotification('Ошибка загрузки рекомендаций', 'danger');
        }
    },

    async loadForecast() {
        const container = document.getElementById('forecast-container');
        if (!container) return;

        try {
            Utils.showLoading(container);
            const forecast = await API.getForecast();

            container.innerHTML = `
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="bi bi-graph-up-arrow me-2"></i>
                            Прогноз на следующий месяц
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <h4 class="mb-3">Ожидаемые расходы: ${Utils.formatMoney(forecast.total_forecast)}</h4>
                            <small class="text-muted">На основе анализа последних ${forecast.based_on_months} месяцев</small>
                        </div>

                        <h6 class="mt-4 mb-3">Прогноз по категориям:</h6>
                        <div class="list-group">
                            ${forecast.category_forecasts.map(cat => `
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <div>
                                        <i class="${cat.icon} me-2" style="color: ${cat.color}"></i>
                                        ${cat.category}
                                    </div>
                                    <span class="badge bg-primary rounded-pill">
                                        ${Utils.formatMoney(cat.forecast)}
                                    </span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading forecast:', error);
            Utils.showNotification('Ошибка загрузки прогноза', 'danger');
        }
    },

    async loadInsights() {
        const container = document.getElementById('insights-container');
        if (!container) return;

        try {
            Utils.showLoading(container);
            const insights = await API.getInsights();

            container.innerHTML = `
                <div class="row g-3">
                    ${insights.map(insight => `
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-body">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="${insight.icon} fs-3 text-primary me-3"></i>
                                        <div>
                                            <h6 class="mb-0">${insight.title}</h6>
                                            <h4 class="mb-0 text-primary">${insight.value}</h4>
                                        </div>
                                    </div>
                                    <p class="text-muted mb-0 small">${insight.description}</p>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            console.error('Error loading insights:', error);
            Utils.showNotification('Ошибка загрузки инсайтов', 'danger');
        }
    }
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('VTB Finance Tracker initialized');

    // Загрузка статистики
    if (document.getElementById('statistics-container')) {
        Statistics.loadStatistics();

        // Обработчик смены периода
        const periodSelect = document.getElementById('period-select');
        if (periodSelect) {
            periodSelect.addEventListener('change', (e) => {
                Statistics.loadStatistics(e.target.value);
            });
        }
    }

    // Загрузка графиков
    if (document.getElementById('monthlyChart')) {
        Charts.createMonthlyChart('monthlyChart');
    }
    if (document.getElementById('categoryChart')) {
        Charts.createCategoryChart('categoryChart');
    }
    if (document.getElementById('trendChart')) {
        Charts.createTrendChart('trendChart');
    }

    // Загрузка AI функций
    if (document.getElementById('recommendations-container')) {
        AI.loadRecommendations();
    }
    if (document.getElementById('forecast-container')) {
        AI.loadForecast();
    }
    if (document.getElementById('insights-container')) {
        AI.loadInsights();
    }

    // Обработчик формы добавления транзакции
    const transactionForm = document.getElementById('transaction-form');
    if (transactionForm) {
        transactionForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(transactionForm);
            const data = Object.fromEntries(formData);

            try {
                await API.createTransaction(data);
                Utils.showNotification('Транзакция успешно добавлена!', 'success');
                transactionForm.reset();

                // Обновить статистику и графики
                if (document.getElementById('statistics-container')) {
                    Statistics.loadStatistics();
                }
                if (document.getElementById('monthlyChart')) {
                    Charts.createMonthlyChart('monthlyChart');
                }
            } catch (error) {
                console.error('Error creating transaction:', error);
                Utils.showNotification('Ошибка при добавлении транзакции', 'danger');
            }
        });
    }

    // Обработчики удаления транзакций
    document.querySelectorAll('.delete-transaction').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();

            if (!confirm('Вы уверены, что хотите удалить эту транзакцию?')) {
                return;
            }

            const transactionId = button.dataset.id;

            try {
                await API.deleteTransaction(transactionId);
                Utils.showNotification('Транзакция удалена', 'success');
                button.closest('tr').remove();
            } catch (error) {
                console.error('Error deleting transaction:', error);
                Utils.showNotification('Ошибка при удалении транзакции', 'danger');
            }
        });
    });
});

//Красивая круговая диаграмма
const roundedDoughnut = {
    id: "roundedDoughnut",
    afterDraw(chart) {
        const ctx = chart.ctx;
        chart.data.datasets.forEach((dataset, i) => {
            const arc = chart.getDatasetMeta(i).data;
            arc.forEach((segment, index) => {
                const props = segment.getProps(['startAngle', 'endAngle', 'outerRadius', 'innerRadius', 'x', 'y'], true);

                const radius = props.outerRadius;
                const thickness = props.outerRadius - props.innerRadius;
                const angle = props.endAngle - props.startAngle;

                const startAngle = props.startAngle;
                const endAngle = props.endAngle;

                // Цвет
                ctx.fillStyle = dataset.backgroundColor[index];

                // Рисуем
                ctx.beginPath();
                ctx.arc(props.x, props.y, props.outerRadius, startAngle, endAngle);
                ctx.arc(props.x, props.y, props.innerRadius, endAngle, startAngle, true);
                ctx.closePath();
                ctx.fill();
            });
        });
    }
};



document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById('categoryChart')) {
        Charts.createCategoryChart('categoryChart');
    }
});

window.VTBTracker.AI.renderRecommendations = function (data) {
    const container = document.getElementById("ai-recommendations");
    container.innerHTML = "";

    data.forEach(rec => {
        container.innerHTML += `
            <div class="ai-card">
                <h4>${rec.title}</h4>
                <p>${rec.text}</p>
            </div>
        `;
    });
};

// ===================== AI CHAT =====================

const chatButton = document.getElementById("ai-chat-button");
const chatWindow = document.getElementById("ai-chat-window");
const chatClose = document.getElementById("ai-chat-close");
const chatInput = document.getElementById("ai-message-input");
const chatSend = document.getElementById("ai-send-btn");
const chatMessages = document.getElementById("ai-chat-messages");

function addMessage(text, sender = "user") {
    const msg = document.createElement("div");
    msg.className = sender === "user" ? "msg-user" : "msg-ai";
    msg.innerText = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatButton.onclick = () => {
    chatWindow.style.display = "flex";
};
chatClose.onclick = () => {
    chatWindow.style.display = "none";
};

chatSend.onclick = sendMessage;
chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
});

function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    chatInput.value = "";

    // ---- Эмуляция ответа AI ----
    setTimeout(() => {
        addMessage("Это пример ответа AI. \n(Скоро подключим настоящий интеллект)", "ai");
    }, 600);
}

async function sendAIMessage() {
    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if (!text) return;

    const chatWindow = document.getElementById("chat-window");

    // показываем сообщение пользователя
    chatWindow.innerHTML += `
        <div class="text-end mb-2">
            <span class="badge bg-primary p-2">${text}</span>
        </div>
    `;

    input.value = "";
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // отправляем на сервер
    const response = await fetch("/ai-chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": Utils.getCookie("csrftoken")
        },
        body: JSON.stringify({ message: text })
    });

    const data = await response.json();

    // показываем ответ ИИ
    chatWindow.innerHTML += `
        <div class="text-start mb-2">
            <span class="badge bg-light text-dark p-2 border">
                ${data.response}
            </span>
        </div>
    `;

    chatWindow.scrollTop = chatWindow.scrollHeight;
}


// Экспорт для использования в других скриптах
window.VTBTracker = {
    API,
    Charts,
    Statistics,
    AI,
    Utils
};