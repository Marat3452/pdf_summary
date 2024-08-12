from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from docx import Document
import pytesseract
import os
from PyPDF2 import PdfReader
import camelot
import requests
import json
import requests
import uuid
import base64

CLIENT_ID = "e2a698cf-de31-4ff4-94b6-1b09ebbeb002"  # Замените на ваш Client ID
CLIENT_SECRET = "664b5049-7c2d-419f-bdc5-20900531159f"  # Замените на ваш Client Secret


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


def save_text_to_docx(text, tables, docx_filename):
    doc = Document()
    doc.add_paragraph(text)

    # Добавление таблиц в документ
    for table in tables:
        df = table.df  # Таблица в формате DataFrame
        # Добавление таблицы в DOCX
        doc_table = doc.add_table(rows=df.shape[0], cols=df.shape[1])
        for i, row in enumerate(df.itertuples()):
            for j, cell in enumerate(row[1:]):  # Пропускаем индекс строки
                doc_table.cell(i, j).text = str(cell)

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

    payload = json.dumps({
        "model": "GigaChat",
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "max_tokens": 512,
        "repetition_penalty": 1,
        "update_interval": 0
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


# Включаем функции для авторизации и работы с GigaChat
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

        # Сохранение полного распознанного текста и таблиц в DOCX
        docx_filename = f"{os.path.splitext(filename)[0]}.docx"
        docx_file_path = os.path.join(fs.location, docx_filename)
        save_text_to_docx(extracted_text, extracted_tables, docx_file_path)

        # Сохранение summary в DOCX
        summary_docx_filename = f"{os.path.splitext(filename)[0]}_summary.docx"
        summary_docx_file_path = os.path.join(fs.location, summary_docx_filename)
        save_text_to_docx(summary_text, [], summary_docx_file_path)

        # Возврат пути к файлам
        response_data = {
            'summary': summary_text,
            'docx_url': fs.url(docx_filename),
            'summary_docx_url': fs.url(summary_docx_file_path),
            'progress': 100
        }
        return JsonResponse(response_data)

    return render(request, 'pdfprocessor/upload.html')