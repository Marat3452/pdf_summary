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


def send_to_ollama(text):
    """Отправка текста на Ollama и получение ответа."""
    url = "http://localhost:11434/api/generate"  # Адрес Ollama API с вашим портом
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama3",  # Замените на нужную модель, поддерживаемую Ollama
        "prompt": f"{text}"  # Просто отправляем текст без специального промта для проверки
    }

    response = requests.post(url, json=data, headers=headers)

    try:
        # Попытка распарсить текст ответа, который может быть разбит на несколько JSON-объектов
        response_text = response.text.strip()
        json_lines = response_text.splitlines()

        # Собираем текст из всех частей ответа
        full_response = ""
        for line in json_lines:
            try:
                json_obj = json.loads(line)
                if "response" in json_obj:
                    full_response += json_obj["response"]
            except json.JSONDecodeError:
                continue

        return full_response if full_response else "No summary returned"

    except ValueError:
        # Если декодирование JSON не удалось, возвращаем текст ошибки
        return "Failed to decode response from Ollama."


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

        # Сохранение полного распознанного текста и таблиц в DOCX
        docx_filename = f"{os.path.splitext(filename)[0]}.docx"
        docx_file_path = os.path.join(fs.location, docx_filename)
        save_text_to_docx(extracted_text, extracted_tables, docx_file_path)

        # Получение summary от модели Hugging Face с добавлением промта
        summary_text = send_to_ollama(extracted_text)

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