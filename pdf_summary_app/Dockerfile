# Используем официальный образ Python в качестве базового
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы проекта в контейнер
COPY . .

# Открываем порт для доступа к приложению
EXPOSE 8000

# Выполняем команду для запуска сервера Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
