import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vtb_tracker.settings')
django.setup()

from accounts.models import User, UserProfile


def create_profiles():
    """Создает профили для всех пользователей без профиля"""
    users_without_profile = User.objects.filter(userprofile__isnull=True)

    created_count = 0
    for user in users_without_profile:
        UserProfile.objects.create(user=user)
        created_count += 1
        print(f"✅ Создан профиль для пользователя: {user.username}")

    if created_count == 0:
        print("ℹ️  Все пользователи уже имеют профили")
    else:
        print(f"\n✨ Создано профилей: {created_count}")


if __name__ == '__main__':
    create_profiles()
