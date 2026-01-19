import os
import shutil

print("🔄 Сброс базы данных...")

# Удаляем базу данных
if os.path.exists('db.sqlite3'):
    os.remove('db.sqlite3')
    print("✅ База данных удалена")

# Удаляем миграции
migrations_dir = 'accounts/migrations'
if os.path.exists(migrations_dir):
    for file in os.listdir(migrations_dir):
        if file.endswith('.py') and file != '__init__.py':
            os.remove(os.path.join(migrations_dir, file))
            print(f"✅ Удалена миграция: {file}")

print("\n✨ Готово! Теперь выполните:")
print("   python manage.py makemigrations")
print("   python manage.py migrate")
print("   python manage.py createsuperuser")