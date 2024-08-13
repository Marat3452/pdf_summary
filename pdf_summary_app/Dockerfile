# Используем официальный Python образ в качестве базового
FROM python:3.11-slim

# Устанавливаем переменные среды
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем содержимое вашего приложения в рабочую директорию
COPY . /app/

# Открываем порт 8000 для взаимодействия с сервером
EXPOSE 8000

# Запускаем Django сервер разработки
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
