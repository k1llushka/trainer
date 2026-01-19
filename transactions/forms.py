from django import forms
from datetime import date
from .models import Transaction, Category, Budget
from cards.models import Card



class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["type", "amount", "category", "card", "date", "description"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")  # <-- правильно забираем user ДО super()
        super().__init__(*args, **kwargs)

        # Фильтр карт пользователя
        self.fields["card"].queryset = Card.objects.filter(user=user)

        self.fields["card"].empty_label = "Наличными / Без карты"

        # Фильтр категорий
        categories = Category.objects.filter(user=user, is_active=True)

        tx_type = None

        # Получаем выбранный тип транзакции
        if 'type' in self.data:
            tx_type = self.data.get('type')
        elif self.instance and self.instance.pk:
            tx_type = self.instance.type

        # Фильтруем категории по типу (доход/расход)
        if tx_type in ('income', 'expense'):
            categories = categories.filter(type=tx_type)

        self.fields["category"].queryset = categories.order_by("name")

        # Стилизация
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

        self.fields["type"].widget.attrs["class"] = "form-select"
        self.fields["category"].widget.attrs["class"] = "form-select"
        self.fields["card"].widget.attrs["class"] = "form-select"

        # Дата по умолчанию
        if not self.instance.pk:
            self.fields["date"].initial = date.today()



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'icon', 'color', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class BudgetForm(forms.ModelForm):
    """Форма для создания/редактирования бюджета"""

    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month']   # ← БЕЗ ЗАПЯТОЙ
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'month': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'month',
                'required': True
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # только категории расходов текущего пользователя
            self.fields['category'].queryset = Category.objects.filter(
                user=user,
                type='expense',
                is_active=True
            )

class TransactionFilterForm(forms.Form):
    type = forms.ChoiceField(
        label='Тип',
        choices=[('', 'Все')] + list(Transaction.TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    category = forms.ModelChoiceField(
        label='Категория',
        queryset=Category.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user, is_active=True
            )

