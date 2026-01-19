from django.urls import path, include
from . import views
from .views import (
    CategoryListView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryUpdateView
)

app_name = 'transactions'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Transactions
    path('list/', views.TransactionListView.as_view(), name='list'),
    path('add/', views.TransactionCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='delete'),

    # Categories
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name="category_edit"),

    # API (DRF router)
    path('api/', include(('transactions.api_urls', 'api'), namespace='api')),
]
