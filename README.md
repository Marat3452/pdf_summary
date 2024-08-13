# PDF Summary Project

## Описание проекта

Проект предназначен для обработки PDF-файлов и изображений, извлечения текста и таблиц, а также генерации краткого содержания документа в табличной форме. Полученное краткое содержание сохраняется в формате Excel и DOCX для удобного использования.

## Структура проекта

- **pdf_summary_app/** - Основное приложение Django.
  - `settings.py` - Настройки Django.
  - `urls.py` - Конфигурация маршрутизации.
  - `wsgi.py` - Точка входа для WSGI-сервера.
  - `asgi.py` - Точка входа для ASGI-сервера.
  
- **pdfprocessor/** - Приложение для обработки файлов.
  - `views.py` - Основная логика обработки PDF и изображений, взаимодействие с API GigaChat.
  - `templates/upload.html` - HTML-шаблон для загрузки файлов и отображения результата.

- **Dockerfile** - Файл для создания Docker-образа приложения.
- **docker-compose.yml** - Конфигурация Docker Compose для запуска приложения.
- **requirements.txt** - Список зависимостей Python, необходимых для работы приложения.

## Требования

- Python 3.8+
- Django 3.2+
- Docker и Docker Compose (для контейнеризации)

## Установка и настройка

### Клонирование репозитория:

```bash
git clone https://github.com/Marat3452/pdf_summary.git
cd pdf_summary_app
```

## Создание и запуск Docker контейнера:

```bash
docker-compose up --build
```

# Использование


## Запуск и загрузка файла:

1. Перейдите на главную страницу приложения `http://localhost:8000/`
2. Выберите __PDF-файл__ для обработки.
3. Нажмите __Загрузить__.

## Отображение и скачивание результатов:
- После обработки в окне __summary__ вы увидите краткое содержание в табличном виде.
- После обработки вы можете скачать результат распознанного текста в формате `DOCX` или `Excel` файл в котором будет содержаться содержимое окна __Summary__.

# Примечание автора:
 - Сервис работает не совсем корректно так как требуется llm способная вместить в себя весь текст по которому требуется суммаризация в виде таблицы.
 - Стандартная(стартовая бесплатная) подписка на GigaChat API не дает полный доступ к полному окну языковой модели.
 - Количество подаваемых токенов сильно ограничена и в соответствии с этим в будущем можно будет посмотреть в сторону более больших моделей способных вмещать в себя весь распознанный текст.
 - Подобрать хорошие мощности и в рамках безопастности развернуть большую модель локально в интрасети.
 - Так же требуется более тонкая работа с промтами которые будут подаваться в llm совместно с текстом.
 - Есть еще вариант в будущем развернуть еще один микросервис с OCR для более точного распознавания текста и таблиц с изображений.
 - В данный момент сервис с изображениями работает очень плохо так как плохо распознает текс на изображениях.
 - Это мой первый опыт в работе с фреймворком Django, делал все не без помощи GPT.
 - В коде так же есть описание каждой функции.
 - В коде используются токены с моего акаунта на котором я тестировал сервис.

# Автор:
Ибраев Марат

Email:int93@mail.ru

# Лицензия
Этот проект распространяется под лицензией MIT.
