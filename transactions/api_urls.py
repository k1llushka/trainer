from rest_framework.routers import DefaultRouter
from . import api_views

app_name = "api"

router = DefaultRouter()
router.register(r'transactions', api_views.TransactionViewSet, basename='transactions')
router.register(r'categories', api_views.CategoryViewSet, basename='categories')
router.register(r'budgets', api_views.BudgetViewSet, basename='budgets')
router.register(r'ai_chat', api_views.AIAnalyticsViewSet, basename='ai_chat')

urlpatterns = router.urls
