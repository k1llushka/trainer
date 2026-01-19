from django.urls import path
from . import views
from .views import CardListView

app_name = 'cards'

urlpatterns = [
    path("", CardListView.as_view(), name="list"),
    path('', views.CardListView.as_view(), name='card_list'),
    path('create/', views.CardCreateView.as_view(), name='card_create'),
    path('<int:pk>/', views.CardDetailView.as_view(), name='card_detail'),
    path('<int:pk>/update/', views.CardUpdateView.as_view(), name='card_update'),
    path('<int:pk>/delete/', views.CardDeleteView.as_view(), name='card_delete'),
]