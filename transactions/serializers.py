from rest_framework import serializers
from .models import Transaction, Category, Budget
from django.db.models import Sum
from datetime import datetime, timedelta
from decimal import Decimal


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon', 'color', 'description', 'is_active']
        read_only_fields = ['id']


class TransactionSerializer(serializers.ModelSerializer):
    """Сериализатор транзакций"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'amount', 'description', 'date',
            'category', 'category_name', 'category_icon', 'category_color',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BudgetSerializer(serializers.ModelSerializer):
    """Сериализатор бюджетов"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'amount', 'month',
            'spent', 'remaining', 'percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_spent(self, obj):
        return float(obj.get_spent())

    def get_remaining(self, obj):
        return float(obj.get_remaining())

    def get_percentage(self, obj):
        return round(obj.get_percentage(), 2)


class StatisticsSerializer(serializers.Serializer):
    """Сериализатор статистики"""
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    transactions_count = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    avg_transaction = serializers.DecimalField(max_digits=12, decimal_places=2)


class ChartDataSerializer(serializers.Serializer):
    """Сериализатор данных для графиков"""
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField()


class AIRecommendationSerializer(serializers.Serializer):
    """Сериализатор AI рекомендаций"""
    type = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    priority = serializers.CharField()
    category = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)