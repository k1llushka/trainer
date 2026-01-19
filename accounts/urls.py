from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    LoginView,
    RegisterView,
    ProfileView,
    ProfileEditView,
    ProfileSettingsUpdateView,   # ← обязательно
)

app_name = 'accounts'

urlpatterns = [
    # Аутентификация
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Профиль
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),

    # Дополнительные страницы
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('documents/', views.DocumentsView.as_view(), name='documents'),

    # Изменение пароля
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/password_change.html',
             success_url='/accounts/profile/'
         ),
         name='password_change'),

    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ),
         name='password_change_done'),
    path("profile/settings/", ProfileSettingsUpdateView.as_view(), name="profile_settings"),

]