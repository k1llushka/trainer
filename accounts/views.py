from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.contrib.auth.views import LoginView as AuthLoginView
from .models import User, UserProfile
from .forms import RegisterForm, UserUpdateForm, UserProfileForm


class LoginView(AuthLoginView):
    """Вход в систему"""
    template_name = 'accounts/login.html'

    def get_success_url(self):
        # Перенаправляем на профиль вместо dashboard
        return '/accounts/profile/'


class RegisterView(View):
    """Регистрация"""
    template_name = 'accounts/register.html'

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('accounts:login')
        return render(request, self.template_name, {'form': form})


class ProfileView(View):
    """Профиль пользователя"""
    template_name = 'accounts/profile.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        return render(request, self.template_name, {
            'user': request.user,
            'profile': profile
        })


class ProfileEditView(View):
    """Редактирование профиля"""
    template_name = 'accounts/profile_edit.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        profile, created = UserProfile.objects.get_or_create(user=request.user)

        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        user_valid = user_form.is_valid()
        profile_valid = profile_form.is_valid()

        # Сохраняем независимо
        if user_valid:
            user_form.save()

        if profile_valid:
            profile_form.save()

        # Если обе валидны — показываем сообщение
        if user_valid and profile_valid:
            messages.success(request, "Профиль обновлен!")
            return redirect('accounts:profile')

        # Иначе показываем ошибки
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })


class ContactsView(View):
    """Контакты"""
    template_name = 'accounts/contacts.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return render(request, self.template_name)


class DocumentsView(View):
    """Документы"""
    template_name = 'accounts/documents.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return render(request, self.template_name)

class ProfileSettingsUpdateView(View):
    """Отдельное сохранение настроек профиля (правая колонка)"""

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Настройки профиля сохранены!")
        else:
            messages.error(request, "Ошибка при сохранении настроек.")

        return redirect("accounts:profile_edit")
