from django.core.management.base import BaseCommand
from transactions.models import Category

class Command(BaseCommand):
    help = 'Создает начальные категории'

    def handle(self, *args, **kwargs):
        # Категории доходов
        income_categories = [
            {'name': 'Зарплата', 'type': 'income', 'icon': 'bi-wallet2', 'color': '#27AE60'},
            {'name': 'Подарок', 'type': 'income', 'icon': 'bi-gift', 'color': '#9B51E0'},
            {'name': 'Перевод', 'type': 'income', 'icon': 'bi-arrow-left-right', 'color': '#0066CC'},
            {'name': 'Инвестиции', 'type': 'income', 'icon': 'bi-graph-up', 'color': '#F2994A'},
            {'name': 'Пенсия', 'type': 'income', 'icon': 'bi-piggy-bank', 'color': '#56CCF2'},
        ]

        # Категории расходов
        expense_categories = [
            {'name': 'Еда', 'type': 'expense', 'icon': 'bi-cart', 'color': '#EB5757'},
            {'name': 'Транспорт', 'type': 'expense', 'icon': 'bi-bus-front', 'color': '#F2994A'},
            {'name': 'Дом: Коммунальные услуги', 'type': 'expense', 'icon': 'bi-house', 'color': '#2F80ED'},
            {'name': 'Покупки', 'type': 'expense', 'icon': 'bi-bag', 'color': '#BB6BD9'},
            {'name': 'Кредит', 'type': 'expense', 'icon': 'bi-credit-card', 'color': '#EB5757'},
            {'name': 'Развлечения', 'type': 'expense', 'icon': 'bi-controller', 'color': '#F2C94C'},
            {'name': 'Здоровье', 'type': 'expense', 'icon': 'bi-heart-pulse', 'color': '#27AE60'},
            {'name': 'Образование', 'type': 'expense', 'icon': 'bi-book', 'color': '#2D9CDB'},
        ]

        all_categories = income_categories + expense_categories

        for cat_data in all_categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                type=cat_data['type'],
                is_default=True,
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создана категория: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Категория уже существует: {category.name}')
                )

        self.stdout.write(self.style.SUCCESS('Начальные данные успешно созданы!'))