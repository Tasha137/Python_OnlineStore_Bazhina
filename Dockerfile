FROM python:3.13
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ✅ МИГРАЦИИ + СУПЕРПОЛЬЗОВАТЕЛЬ АВТОМАТИЧЕСКИ!
RUN python manage.py makemigrations --noinput
RUN python manage.py migrate --noinput
RUN python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None
"

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
