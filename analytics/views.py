from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from transactions.models import Transaction
from .forms import BudgetForm
from .models import Budget, AIRecommendation


# ============================================================
# AI LOGIC — вынесено отдельно
# ============================================================

class RecommendationService:
    """Логика генерации рекомендаций"""

    @staticmethod
    def generate(user, transactions, budgets):
        recommendations = []

        # ----- 1. Проверка перерасхода бюджета -----
        for budget in budgets:
            spent = transactions.filter(
                category=budget.category,
                type="expense"
            ).aggregate(total=Sum("amount"))["total"] or Decimal(0)

            if spent > budget.amount:
                recommendations.append(
                    f"Вы превысили бюджет категории «{budget.category.name}» на {spent - budget.amount} ₽."
                )

            elif spent > budget.amount * Decimal("0.8"):
                recommendations.append(
                    f"Категория «{budget.category.name}» почти достигла лимита. Осталось {budget.amount - spent} ₽."
                )

        # ----- 2. Категория лидера по расходам -----
        top_category = (
            transactions.filter(type="expense")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
            .first()
        )

        if top_category:
            recommendations.append(
                f"Максимальные траты в категории «{top_category['category__name']}». Рекомендуется проанализировать расходы."
            )

        # ----- 3. Большие расходы за последнюю неделю -----
        week_expense = transactions.filter(
            date__gte=timezone.now().date() - timedelta(days=7),
            type="expense"
        ).aggregate(total=Sum("amount"))["total"] or Decimal(0)

        if week_expense > Decimal("5000"):
            recommendations.append(
                "Расходы за последние 7 дней выше нормы. Проверьте необязательные траты."
            )

        # ----- 4. Если нет рекомендаций -----
        if not recommendations:
            recommendations.append("Отлично! Ваши траты выглядят стабильно.")

        # ----- 5. Сохранение в БД (но без дублей в один день) -----
        today = timezone.now().date()

        for rec in recommendations:
            exists = AIRecommendation.objects.filter(user=user, text=rec, created_at__date=today).exists()
            if not exists:
                AIRecommendation.objects.create(user=user, text=rec)

        return recommendations


# ============================================================
# ОСНОВНАЯ СТРАНИЦА АНАЛИТИКИ
# ============================================================

class AnalyticsView(LoginRequiredMixin, View):
    template_name = 'analytics/analytics.html'

    def generate_ai_recommendations(self, user, transactions, budgets):
        recommendations = []

        # Перерасход бюджета
        for b in budgets:
            spent = transactions.filter(
                category=b.category,
                type="expense"
            ).aggregate(total=Sum("amount"))["total"] or 0

            if spent > b.amount:
                recommendations.append(
                    f"Вы превысили бюджет категории «{b.category.name}» на {spent - b.amount} ₽."
                )

            elif spent > b.amount * Decimal("0.8"):
                recommendations.append(
                    f"Категория «{b.category.name}» близка к лимиту. Осталось {b.amount - spent} ₽."
                )

        # Максимальные траты
        top_category = (
            transactions.filter(type="expense")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
            .first()
        )
        if top_category:
            recommendations.append(
                f"Больше всего расходов в категории «{top_category['category__name']}». Рекомендуем проверить траты."
            )

        # Динамика за неделю
        last_week = timezone.now() - timedelta(days=7)
        week_expense = transactions.filter(
            type="expense",
            date__gte=last_week
        ).aggregate(total=Sum("amount"))["total"] or 0

        if week_expense > 5000:
            recommendations.append(
                "Расходы за последнюю неделю выше нормы. Подумайте о сокращении необязательных покупок."
            )

        if not recommendations:
            recommendations.append("Ваши финансы стабильны. Продолжайте в том же духе!")

        # Сохраняем в БД
        AIRecommendation.objects.filter(user=user).delete()
        for text in recommendations:
            AIRecommendation.objects.create(user=user, text=text)

        return recommendations

    def get(self, request):
        user = request.user

        # анализ последних 30 дней
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        transactions = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).select_related("category")

        budgets = Budget.objects.filter(user=user)

        recommendations = self.generate_ai_recommendations(user, transactions, budgets)

        return render(request, self.template_name, {
            "recommendations": recommendations
        })


# ============================================================
# ИСТОРИЯ РЕКОМЕНДАЦИЙ
# ============================================================

class RecommendationListView(LoginRequiredMixin, ListView):
    template_name = "analytics/recommendations.html"
    context_object_name = "recommendations"

    def get_queryset(self):
        return AIRecommendation.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


# ============================================================
# БЮДЖЕТЫ
# ============================================================

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    context_object_name = "budgets"
    template_name = "analytics/budget_list.html"

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = "analytics/budget_form.html"
    success_url = reverse_lazy("analytics:budget_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Бюджет успешно создан!")
        return super().form_valid(form)
