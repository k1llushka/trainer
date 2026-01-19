from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Transaction, Category, Budget
from .forms import TransactionForm, CategoryForm, BudgetForm, TransactionFilterForm
from analytics.models import AIRecommendation
from cards.models import Card
from django.http import JsonResponse


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        today = datetime.now().date()

        # ===== ПЕРИОД =====
        period = self.request.GET.get("period", "month")

        if period == "week":
            start_date = today - timedelta(days=today.weekday())
            title = "Статистика за текущую неделю"
        elif period == "year":
            start_date = today.replace(month=1, day=1)
            title = "Статистика за текущий год"
        else:
            start_date = today.replace(day=1)
            title = "Статистика за текущий месяц"

        context["period"] = period
        context["period_title"] = title

        # ===== КАРТЫ =====
        cards = Card.objects.filter(user=user)
        context["cards"] = cards

        card_id = self.request.GET.get("card")
        selected_card = None

        if card_id and card_id.isdigit():
            selected_card = cards.filter(id=card_id).first()

        context["selected_card"] = selected_card

        # ===== ТРАНЗАКЦИИ (УЧЁТ КАРТЫ) =====
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=today
        )

        if selected_card:
            transactions = transactions.filter(card=selected_card)

        # ===== ДОХОДЫ / РАСХОДЫ =====
        income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # ===== БАЛАНС =====
        if selected_card:
            balance = selected_card.balance
        else:
            balance = cards.aggregate(total=Sum("balance"))["total"] or Decimal("0")

        # ===== ПОСЛЕДНИЕ ТРАНЗАКЦИИ =====
        recent_transactions = transactions.order_by('-date')[:10]

        context.update({
            "income": income,
            "expense": expense,
            "balance": balance,
            "recent_transactions": recent_transactions,
        })

        # ===== ГРАФИК КАТЕГОРИЙ =====
        category_data = (
            transactions.filter(type="expense")
            .values("category__name", "category__color")
            .annotate(total=Sum("amount"))
        )

        context["chart_labels"] = [c["category__name"] for c in category_data]
        context["chart_values"] = [float(c["total"]) for c in category_data]
        context["chart_colors"] = [c["category__color"] or "#cccccc" for c in category_data]

        # ===== AI РЕКОМЕНДАЦИИ =====
        context["ai_recommendations"] = self.generate_ai_recommendations(
            user=user,
            transactions=transactions,
            income=income,
            expense=expense
        )

        return context



    def generate_ai_recommendations(self, user, transactions, income, expense):
        recommendations = []

        # 1. Превышение расходов над доходами
        if expense > income:
            recommendations.append(
                f"Ваши расходы превышают доходы на {float(expense - income):.0f} ₽. Попробуйте пересмотреть траты."
            )

        # 2. Категория с максимальными расходами
        top_cat = (
            transactions.filter(type="expense")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
            .first()
        )
        if top_cat:
            recommendations.append(
                f"Больше всего вы тратите на «{top_cat['category__name']}» — {float(top_cat['total']):.0f} ₽."
            )

        # 3. Быстрый рост расходов за неделю
        week_ago = datetime.now().date() - timedelta(days=7)
        week_expense = (
                transactions.filter(type="expense", date__gte=week_ago)
                .aggregate(total=Sum("amount"))["total"]
                or 0
        )

        if week_expense > 0 and week_expense > (expense * Decimal("0.5")):
            recommendations.append(
                "Более 50% ваших расходов за период пришлись на последние 7 дней — расходы растут слишком быстро."
            )

        # 4. Средний чек
        expenses_list = [
            float(t.amount) for t in transactions.filter(type="expense")
        ]
        if expenses_list:
            avg = sum(expenses_list) / len(expenses_list)
            if avg > 3000:
                recommendations.append(
                    f"Средняя трата составляет {avg:.0f} ₽ — это довольно высоко. Попробуйте снизить количество крупных покупок."
                )

        # 5. Низкая диверсификация категорий
        categories_count = (
            transactions.filter(type="expense")
            .values("category")
            .distinct()
            .count()
        )
        if categories_count == 1:
            recommendations.append(
                "Все ваши расходы сосредоточены в одной категории — это риск несбалансированности бюджета."
            )

        # 6. Если нет рекомендаций
        if not recommendations:
            recommendations.append("Отлично! Ваши траты выглядят сбалансировано 😊")

        return recommendations


class TransactionListView(LoginRequiredMixin, ListView):
    """Список всех транзакций"""
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        form = TransactionFilterForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            if form.cleaned_data.get('type'):
                queryset = queryset.filter(type=form.cleaned_data['type'])
            if form.cleaned_data.get('category'):
                queryset = queryset.filter(category=form.cleaned_data['category'])
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(date__lte=form.cleaned_data['date_to'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        income = queryset.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        expense = queryset.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')

        context['filter_form'] = TransactionFilterForm(self.request.GET, user=self.request.user)
        context['total_income'] = income
        context['total_expense'] = expense
        context['balance'] = income - expense

        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "transactions/transaction_form.html"
    success_url = reverse_lazy("transactions:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        card = form.instance.card
        if card:
            if form.instance.type == 'income':
                card.balance += form.instance.amount
            else:
                card.balance -= form.instance.amount
            card.save()

        return response

    def get_initial(self):
        initial = super().get_initial()

        card_id = self.request.GET.get("card")
        if card_id:
            initial["card"] = card_id

        return initial


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        old_transaction = self.get_object()
        old_card = old_transaction.card

        # Откат старой транзакции
        if old_card:
            if old_transaction.type == 'income':
                old_card.balance -= old_transaction.amount
            else:
                old_card.balance += old_transaction.amount
            old_card.save()

        response = super().form_valid(form)

        new_card = form.instance.card
        if new_card:
            if form.instance.type == 'income':
                new_card.balance += form.instance.amount
            else:
                new_card.balance -= form.instance.amount
            new_card.save()

        return response


class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:list')

    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        card = transaction.card

        if card:
            if transaction.type == "income":
                card.balance -= transaction.amount
            else:
                card.balance += transaction.amount
            card.save()

        return super().delete(request, *args, **kwargs)



class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'transactions/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'transactions/category_form.html'
    success_url = reverse_lazy('transactions:category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Категория успешно создана!')
        return super().form_valid(form)

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "transactions/category_confirm_delete.html"
    success_url = reverse_lazy("transactions:category_list")

    def get_queryset(self):
        # Чтобы пользователь видел только свои категории
        return Category.objects.filter(user=self.request.user)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "transactions/category_form.html"
    success_url = reverse_lazy("transactions:category_list")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
