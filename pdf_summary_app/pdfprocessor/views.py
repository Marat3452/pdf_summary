from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from docx import Document
import pytesseract
import os
from PyPDF2 import PdfReader
import camelot
import json
import requests
import uuid
import base64


CLIENT_ID = "e2a698cf-de31-4ff4-94b6-1b09ebbeb002"
CLIENT_SECRET = "2b0e8ae9-b29e-413c-b2de-49d5a7a8d79e"


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_tables_from_pdf(pdf_path):
    tables = camelot.read_pdf(pdf_path, pages='all')
    return tables


def extract_text_from_image(image_path):
    return pytesseract.image_to_string(image_path)


def save_text_to_docx(text, docx_filename):
    """
    Сохранение текста в файл DOCX
    """
    doc = Document()
    doc.add_paragraph(text)
    doc.save(docx_filename)
    return docx_filename


def get_gigachat_token():
    """
    Выполняет POST-запрос к эндпоинту, который выдает токен.
    Возвращает токен доступа для использования с API GigaChat.
    """
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_header = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {auth_header}'
    }

    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"Ошибка получения токена: {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Ошибка: {str(e)}")
        return None


def send_to_ollama(auth_token, user_message):
    """
    Отправляет POST-запрос к API GigaChat для получения ответа от модели.
    """
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Добавляем промт перед исходным сообщением пользователя
    prompt = "Give me back a summary of the text in markdown form. Give your answer in Russian.\n\n"
    user_message_with_prompt = prompt + user_message

    payload = json.dumps({
        "model": "GigaChat-Plus",
        "messages": [{"role": "system", "content": user_message_with_prompt}],
        # "stream": False,
        # "update_interval": 0
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'.encode('utf-8').decode('latin-1')
    }

    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Ошибка получения ответа: {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Произошла ошибка: {str(e)}")
        return None


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        if filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file_path)
            extracted_tables = extract_tables_from_pdf(file_path)
        elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            extracted_text = extract_text_from_image(file_path)
            extracted_tables = []  # Таблицы из изображений не извлекаются
        else:
            return JsonResponse({'error': 'Unsupported file format'}, status=400)

        # Получение токена доступа от GigaChat
        access_token = get_gigachat_token()
        if not access_token:
            return JsonResponse({'error': 'Не удалось получить токен доступа'}, status=500)

        # Отправка текста в GigaChat для генерации ответа
        summary_text = send_to_ollama(access_token, extracted_text)

        # Сохранение summary в DOCX
        summary_docx_filename = f"{os.path.splitext(filename)[0]}_summary.docx"
        summary_docx_file_path = os.path.join(fs.location, summary_docx_filename)
        save_text_to_docx(summary_text, summary_docx_file_path)

        # Сохранение полного распознанного текста и таблиц в DOCX
        docx_filename = f"{os.path.splitext(filename)[0]}.docx"
        docx_file_path = os.path.join(fs.location, docx_filename)
        save_text_to_docx(extracted_text, docx_file_path)

        # Отображение текста summary в окне Summary
        summary_html = summary_text.replace('\n', '<br>')  # Форматирование для HTML

        # Возврат пути к файлам
        response_data = {
            'summary': summary_html,  # Отображаем ответ от GigaChat в HTML
            'docx_url': fs.url(docx_filename),
            'summary_docx_url': fs.url(summary_docx_file_path),  # URL для скачивания DOCX файла с summary
            'progress': 100
        }
        return JsonResponse(response_data)

    return render(request, 'pdfprocessor/upload.html')
