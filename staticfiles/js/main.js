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
            const data = await API.getChartData('monthly');

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
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Доходы и расходы по месяцам'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
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
            console.error('Error creating monthly chart:', error);
        }
    },

    // Создать круговую диаграмму категорий
    async createCategoryChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        try {
            const data = await API.getChartData('category');

            if (currentCharts[canvasId]) {
                currentCharts[canvasId].destroy();
            }

            const ctx = canvas.getContext('2d');
            currentCharts[canvasId] = new Chart(ctx, {
                type: 'doughnut',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
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

// AI рекомендации
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

Charts.createCategoryChart = async function (canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    try {
        const data = await API.getChartData('category');

        if (currentCharts[canvasId]) {
            currentCharts[canvasId].destroy();
        }

        Chart.register(roundedDoughnut);

        const ctx = canvas.getContext('2d');
        currentCharts[canvasId] = new Chart(ctx, {
            type: "doughnut",
            plugins: [roundedDoughnut],

            data: {
                labels: data.labels,
                datasets: [
                    {
                        data: data.datasets[0].data,
                        backgroundColor: data.datasets[0].backgroundColor,
                        borderWidth: 0,
                        spacing: 14,
                        hoverOffset: 0
                    }
                ]
            },

            options: {
                cutout: "70%",
                responsive: true,
                maintainAspectRatio: false,

                animation: {
                    animateRotate: true,
                    duration: 1400
                },

                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            usePointStyle: true,
                            pointStyle: "circle",
                            padding: 18,
                            font: { size: 15 }
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("Ошибка диаграммы категорий:", error);
    }
};


document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById('categoryChart')) {
        Charts.createCategoryChart('categoryChart');
    }
});


// Экспорт для использования в других скриптах
window.VTBTracker = {
    API,
    Charts,
    Statistics,
    AI,
    Utils
};