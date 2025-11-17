# Dockerfile — for backend located at repo root (adjust path if Docker build context is the subfolder)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (small)
RUN apt-get update && apt-get install -y build-essential libpq-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Run migrations, create superuser (if env vars set), collect static
#  — migrate first, then create superuser, then collectstatic
RUN python manage.py migrate --noinput

# Create superuser if env vars supplied (idempotent)
RUN if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then \
    python - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dojo_backend.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
u = os.environ.get('DJANGO_SUPERUSER_USERNAME')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=p)
print('superuser ensured')
PY
fi

RUN python manage.py collectstatic --noinput

# Gunicorn binds to the PORT env var if provided by platform
CMD ["gunicorn", "dojo_backend.wsgi:application", "--bind", "0.0.0.0:${PORT:-8080}", "--workers", "3"]