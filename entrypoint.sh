#!/bin/bash

# Aplicar migraciones
echo "→ Running migrations..."
python manage.py migrate

# Crear superusuario si no existe
echo "→ Creating superuser (if needed)..."
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if username and email and password and not User.objects.filter(username=username).exists():
    print("Creating superuser:", username)
    User.objects.create_superuser(username, email, password)
else:
    print("Superuser already exists or env vars not set.")
EOF

# Levantar servidor
echo "→ Starting Gunicorn server..."
gunicorn EchoesOfValue.wsgi
