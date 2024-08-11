import requests
import PyPDF2
from pdf2image import convert_from_path
import pytesseract


def extract_text_from_pdf(pdf_path):
    """Извлечение текста из текстового PDF."""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text


def extract_text_from_images(pdf_path):
    """Извлечение текста из PDF, содержащего изображения."""
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text


import json

import requests
import json


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


from docx import Document
from io import BytesIO


def create_summary_docx(summary):
    """Создание документа .docx с текстом summary."""
    document = Document()
    document.add_heading('Ответ от Ollama', 0)
    document.add_paragraph(summary)

    # Сохраняем документ в поток
    file_stream = BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream
