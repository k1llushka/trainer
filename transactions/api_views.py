from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from .models import Transaction, Category, Budget
from .serializers import (
    TransactionSerializer, CategorySerializer, BudgetSerializer,
    StatisticsSerializer, ChartDataSerializer, AIRecommendationSerializer
)


class TransactionViewSet(viewsets.ModelViewSet):
    """API для транзакций"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по транзакциям"""
        queryset = self.get_queryset()

        # Фильтр по периоду
        period = request.query_params.get('period', 'month')
        today = timezone.now().date()

        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today.replace(day=1)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
        else:
            start_date = None

        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        # Подсчет статистики
        income = queryset.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

        expense = queryset.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

        balance = income - expense

        transactions_count = queryset.count()
        categories_count = queryset.values('category').distinct().count()

        avg_transaction = queryset.aggregate(
            avg=Avg('amount')
        )['avg'] or Decimal('0')

        data = {
            'total_income': income,
            'total_expense': expense,
            'balance': balance,
            'transactions_count': transactions_count,
            'categories_count': categories_count,
            'avg_transaction': avg_transaction,
        }

        serializer = StatisticsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """Получить данные для графиков"""
        chart_type = request.query_params.get('type', 'monthly')

        if chart_type == 'monthly':
            return self._get_monthly_chart_data(request)
        elif chart_type == 'category':
            return self._get_category_chart_data(request)
        elif chart_type == 'trend':
            return self._get_trend_chart_data(request)

        return Response({'error': 'Invalid chart type'}, status=400)

    def _get_monthly_chart_data(self, request):
        """Данные по месяцам"""
        today = timezone.now().date()
        months = []
        income_data = []
        expense_data = []

        for i in range(6, -1, -1):
            date = today - timedelta(days=30 * i)
            month_start = date.replace(day=1)

            if i > 0:
                next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
                month_end = next_month - timedelta(days=1)
            else:
                month_end = today

            months.append(month_start.strftime('%B'))

            income = Transaction.objects.filter(
                user=request.user,
                type='income',
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0

            expense = Transaction.objects.filter(
                user=request.user,
                type='expense',
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0

            income_data.append(float(income))
            expense_data.append(float(expense))

        data = {
            'labels': months,
            'datasets': [
                {
                    'label': 'Доходы',
                    'data': income_data,
                    'backgroundColor': 'rgba(40, 167, 69, 0.2)',
                    'borderColor': 'rgba(40, 167, 69, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Расходы',
                    'data': expense_data,
                    'backgroundColor': 'rgba(220, 53, 69, 0.2)',
                    'borderColor': 'rgba(220, 53, 69, 1)',
                    'borderWidth': 2
                }
            ]
        }

        serializer = ChartDataSerializer(data)
        return Response(serializer.data)

    def _get_category_chart_data(self, request):
        """Данные по категориям"""
        today = timezone.now().date()
        month_start = today.replace(day=1)

        categories = Transaction.objects.filter(
            user=request.user,
            type='expense',
            date__gte=month_start
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount')
        ).order_by('-total')[:10]

        labels = [cat['category__name'] or 'Без категории' for cat in categories]
        data_values = [float(cat['total']) for cat in categories]
        colors = [cat['category__color'] or '#6c757d' for cat in categories]

        data = {
            'labels': labels,
            'datasets': [{
                'label': 'Расходы по категориям',
                'data': data_values,
                'backgroundColor': colors,
                'borderWidth': 1
            }]
        }

        serializer = ChartDataSerializer(data)
        return Response(serializer.data)

    def _get_trend_chart_data(self, request):
        """Тренд за последние 30 дней"""
        today = timezone.now().date()
        dates = []
        balance_data = []

        for i in range(29, -1, -1):
            date = today - timedelta(days=i)
            dates.append(date.strftime('%d.%m'))

            income = Transaction.objects.filter(
                user=request.user,
                type='income',
                date__lte=date
            ).aggregate(total=Sum('amount'))['total'] or 0

            expense = Transaction.objects.filter(
                user=request.user,
                type='expense',
                date__lte=date
            ).aggregate(total=Sum('amount'))['total'] or 0

            balance_data.append(float(income - expense))

        data = {
            'labels': dates,
            'datasets': [{
                'label': 'Баланс',
                'data': balance_data,
                'fill': True,
                'backgroundColor': 'rgba(13, 110, 253, 0.1)',
                'borderColor': 'rgba(13, 110, 253, 1)',
                'borderWidth': 2,
                'tension': 0.4
            }]
        }

        serializer = ChartDataSerializer(data)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """API для категорий"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    """API для бюджетов"""
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AIAnalyticsViewSet(viewsets.ViewSet):
    """API для AI аналитики"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Получить AI рекомендации"""
        recommendations = self._generate_recommendations(request.user)
        serializer = AIRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Прогноз расходов на следующий месяц"""
        forecast_data = self._generate_forecast(request.user)
        return Response(forecast_data)

    @action(detail=False, methods=['get'])
    def insights(self, request):
        """Финансовые инсайты"""
        insights = self._generate_insights(request.user)
        return Response(insights)

    def _generate_recommendations(self, user):
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        today = timezone.now().date()
        month_start = today.replace(day=1)

        # Анализ расходов по категориям
        categories = Transaction.objects.filter(
            user=user,
            type='expense',
            date__gte=month_start
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')

        if categories:
            top_category = categories[0]
            if top_category['total'] > 10000:
                recommendations.append({
                    'type': 'warning',
                    'title': 'Высокие расходы',
                    'message': f"Вы потратили {top_category['total']} ₽ на {top_category['category__name']}. Рассмотрите возможность оптимизации.",
                    'priority': 'high',
                    'category': top_category['category__name'],
                    'amount': top_category['total']
                })

        # Проверка бюджетов
        budgets = Budget.objects.filter(user=user, month=month_start)
        for budget in budgets:
            percentage = budget.get_percentage()
            if percentage > 90:
                recommendations.append({
                    'type': 'alert',
                    'title': 'Превышение бюджета',
                    'message': f"Бюджет на {budget.category.name} использован на {percentage:.0f}%",
                    'priority': 'high',
                    'category': budget.category.name,
                    'amount': budget.get_spent()
                })
            elif percentage > 70:
                recommendations.append({
                    'type': 'warning',
                    'title': 'Приближение к лимиту',
                    'message': f"Бюджет на {budget.category.name} использован на {percentage:.0f}%",
                    'priority': 'medium',
                    'category': budget.category.name,
                    'amount': budget.get_spent()
                })

        # Анализ трендов
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        last_month_end = month_start - timedelta(days=1)

        current_expense = Transaction.objects.filter(
            user=user,
            type='expense',
            date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        last_month_expense = Transaction.objects.filter(
            user=user,
            type='expense',
            date__gte=last_month_start,
            date__lte=last_month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        if last_month_expense > 0:
            change = ((current_expense - last_month_expense) / last_month_expense) * 100
            if change > 20:
                recommendations.append({
                    'type': 'info',
                    'title': 'Рост расходов',
                    'message': f"Ваши расходы выросли на {change:.1f}% по сравнению с прошлым месяцем",
                    'priority': 'medium',
                    'amount': current_expense
                })
            elif change < -20:
                recommendations.append({
                    'type': 'success',
                    'title': 'Снижение расходов',
                    'message': f"Отличная работа! Расходы снизились на {abs(change):.1f}%",
                    'priority': 'low',
                    'amount': current_expense
                })

        # Рекомендации по накоплениям
        income = Transaction.objects.filter(
            user=user,
            type='income',
            date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        if income > 0:
            savings_rate = ((income - current_expense) / income) * 100
            if savings_rate < 10:
                recommendations.append({
                    'type': 'warning',
                    'title': 'Низкий уровень накоплений',
                    'message': f"Вы откладываете только {savings_rate:.1f}% дохода. Рекомендуется откладывать минимум 20%",
                    'priority': 'high',
                    'amount': income - current_expense
                })
            elif savings_rate > 30:
                recommendations.append({
                    'type': 'success',
                    'title': 'Отличный уровень накоплений',
                    'message': f"Вы откладываете {savings_rate:.1f}% дохода. Продолжайте в том же духе!",
                    'priority': 'low',
                    'amount': income - current_expense
                })

        return recommendations

    def _generate_forecast(self, user):
        """Прогноз на следующий месяц"""
        today = timezone.now().date()

        # Анализ последних 3 месяцев
        forecasts = []
        for i in range(3):
            month_start = (today.replace(day=1) - timedelta(days=30 * i))
            month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

            expense = Transaction.objects.filter(
                user=user,
                type='expense',
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            forecasts.append(float(expense))

        # Простой прогноз (среднее значение)
        avg_expense = sum(forecasts) / len(forecasts) if forecasts else 0

        # Прогноз по категориям
        category_forecasts = []
        categories = Category.objects.filter(user=user, type='expense', is_active=True)

        for category in categories:
            cat_expenses = []
            for i in range(3):
                month_start = (today.replace(day=1) - timedelta(days=30 * i))
                month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

                expense = Transaction.objects.filter(
                    user=user,
                    type='expense',
                    category=category,
                    date__gte=month_start,
                    date__lte=month_end
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

                cat_expenses.append(float(expense))

            avg_cat_expense = sum(cat_expenses) / len(cat_expenses) if cat_expenses else 0

            if avg_cat_expense > 0:
                category_forecasts.append({
                    'category': category.name,
                    'forecast': round(avg_cat_expense, 2),
                    'icon': category.icon,
                    'color': category.color
                })

        return {
            'total_forecast': round(avg_expense, 2),
            'category_forecasts': sorted(category_forecasts, key=lambda x: x['forecast'], reverse=True),
            'confidence': 'medium',
            'based_on_months': 3
        }

    def _generate_insights(self, user):
        """Генерация финансовых инсайтов"""
        today = timezone.now().date()
        month_start = today.replace(day=1)

        insights = []

        # Самая дорогая транзакция
        max_transaction = Transaction.objects.filter(
            user=user,
            type='expense',
            date__gte=month_start
        ).order_by('-amount').first()

        if max_transaction:
            insights.append({
                'title': 'Самая крупная покупка',
                'value': f"{max_transaction.amount} ₽",
                'description': f"{max_transaction.category.name if max_transaction.category else 'Без категории'} - {max_transaction.date.strftime('%d.%m.%Y')}",
                'icon': 'bi-cash-stack'
            })

        # Средний чек
        avg_transaction = Transaction.objects.filter(
            user=user,
            type='expense',
            date__gte=month_start
        ).aggregate(avg=Avg('amount'))['avg'] or 0

        insights.append({
            'title': 'Средний чек',
            'value': f"{avg_transaction:.2f} ₽",
            'description': 'Среднее значение ваших покупок',
            'icon': 'bi-receipt'
        })

        # Количество транзакций
        transaction_count = Transaction.objects.filter(
            user=user,
            date__gte=month_start
        ).count()

        insights.append({
            'title': 'Транзакций в месяце',
            'value': str(transaction_count),
            'description': 'Общее количество операций',
            'icon': 'bi-list-check'
        })

        # Самая популярная категория
        top_category = Transaction.objects.filter(
            user=user,
            type='expense',
            date__gte=month_start
        ).values('category__name').annotate(
            count=Count('id')
        ).order_by('-count').first()

        if top_category:
            insights.append({
                'title': 'Популярная категория',
                'value': top_category['category__name'] or 'Без категории',
                'description': f"{top_category['count']} транзакций",
                'icon': 'bi-star'
            })

        return insights