import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facebook.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@telirma.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Telirma@2024')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} créé avec succès')
else:
    print(f'Superuser {username} existe déjà')
