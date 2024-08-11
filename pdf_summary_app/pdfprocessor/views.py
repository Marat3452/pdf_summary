# from django.shortcuts import render
# from .utils import extract_text_from_pdf, extract_text_from_images, send_to_ollama, create_summary_docx
# from django.http import JsonResponse
# from django.core.files.storage import FileSystemStorage
#
#
# def upload_pdf(request):
#     if request.method == 'POST' and request.FILES['pdf_file']:
#         pdf_file = request.FILES['pdf_file']
#         fs = FileSystemStorage()
#         filename = fs.save(pdf_file.name, pdf_file)
#         file_path = fs.path(filename)
#
#         # Извлечение текста из PDF и получение ответа от модели
#         extracted_text = extract_text_from_pdf(file_path)
#         if not extracted_text.strip():
#             extracted_text = extract_text_from_images(file_path)
#         summary = send_to_ollama(extracted_text)
#
#         # Создание DOCX файла с summary
#         docx_url = None
#         if summary:
#             docx_file = create_summary_docx(summary)
#             docx_filename = f'summary_{filename}.docx'
#             docx_path = fs.save(docx_filename, docx_file)
#             docx_url = fs.url(docx_filename)
#
#         # Формируем JSON-ответ
#         response_data = {
#             'summary': summary,
#             'docx_url': docx_url,
#             'progress': 100
#         }
#         return JsonResponse(response_data)
#
#     return render(request, 'pdfprocessor/upload.html')
#

# from django.http import JsonResponse
# from django.shortcuts import render
# from django.core.files.storage import FileSystemStorage
# from docx import Document
# import pytesseract
# from pdf2image import convert_from_path
# import os
# from PyPDF2 import PdfReader
# import requests
#
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# def extract_text_from_pdf(pdf_path):
#     reader = PdfReader(pdf_path)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text()
#     return text
#
#
# def extract_text_from_image(image_path):
#     return pytesseract.image_to_string(image_path)
#
#
# def save_text_to_docx(text, docx_filename):
#     doc = Document()
#     doc.add_paragraph(text)
#     doc.save(docx_filename)
#     return docx_filename
#
# import json
# def send_to_ollama(text):
#     """Отправка текста на Ollama и получение ответа."""
#     url = "http://localhost:11434/api/generate"  # Адрес Ollama API с вашим портом
#     headers = {"Content-Type": "application/json"}
#     data = {
#         "model": "llama3",
#         "prompt": f"{text}"
#     }
#
#     response = requests.post(url, json=data, headers=headers)
#
#     try:
#         # Попытка распарсить текст ответа, который может быть разбит на несколько JSON-объектов
#         response_text = response.text.strip()
#         json_lines = response_text.splitlines()
#
#         # Собираем текст из всех частей ответа
#         full_response = ""
#         for line in json_lines:
#             try:
#                 json_obj = json.loads(line)
#                 if "response" in json_obj:
#                     full_response += json_obj["response"]
#             except json.JSONDecodeError:
#                 continue
#
#         return full_response if full_response else "No summary returned"
#
#     except ValueError:
#         # Если декодирование JSON не удалось, возвращаем текст ошибки
#         return "Failed to decode response from Ollama."
#
#
# def upload_file(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(uploaded_file.name, uploaded_file)
#         file_path = fs.path(filename)
#
#         if filename.lower().endswith('.pdf'):
#             extracted_text = extract_text_from_pdf(file_path)
#         elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
#             extracted_text = extract_text_from_image(file_path)
#         else:
#             return JsonResponse({'error': 'Unsupported file format'}, status=400)
#
#         # Сохранение полного распознанного текста в DOCX
#         docx_filename = f"{os.path.splitext(filename)[0]}.docx"
#         docx_file_path = os.path.join(fs.location, docx_filename)
#         save_text_to_docx(extracted_text, docx_file_path)
#
#         # Получение summary от модели Ollama
#         summary_text = send_to_ollama(extracted_text)
#
#         # Сохранение summary в DOCX
#         summary_docx_filename = f"{os.path.splitext(filename)[0]}_summary.docx"
#         summary_docx_file_path = os.path.join(fs.location, summary_docx_filename)
#         save_text_to_docx(summary_text, summary_docx_file_path)
#
#         # Возврат пути к файлам
#         response_data = {
#             'summary': summary_text,
#             'docx_url': fs.url(docx_filename),
#             'summary_docx_url': fs.url(summary_docx_file_path),
#             'progress': 100
#         }
#         return JsonResponse(response_data)
#
#     return render(request, 'pdfprocessor/upload.html')


# from django.http import JsonResponse
# from django.shortcuts import render
# from django.core.files.storage import FileSystemStorage
# from docx import Document
# from transformers import pipeline
#
# import pytesseract
# from pdf2image import convert_from_path
# import os
# from PyPDF2 import PdfReader
#
# # Инициализация модели через Hugging Face API
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
#
# def extract_text_from_pdf(pdf_path):
#     reader = PdfReader(pdf_path)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text()
#     return text
#
# def extract_text_from_image(image_path):
#     return pytesseract.image_to_string(image_path)
#
# def save_text_to_docx(text, docx_filename):
#     doc = Document()
#     doc.add_paragraph(text)
#     doc.save(docx_filename)
#     return docx_filename
#
# def send_to_ollama(text):
#     # Добавление промта к тексту перед отправкой в модель
#     prompt = f"Вот мое ТЗ: {text} сделай summary по нему."
#     summary = summarizer(prompt, max_length=150, min_length=40, do_sample=False)
#     return summary[0]['summary_text']
#
# def upload_file(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(uploaded_file.name, uploaded_file)
#         file_path = fs.path(filename)
#
#         if filename.lower().endswith('.pdf'):
#             extracted_text = extract_text_from_pdf(file_path)
#         elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
#             extracted_text = extract_text_from_image(file_path)
#         else:
#             return JsonResponse({'error': 'Unsupported file format'}, status=400)
#
#         # Сохранение полного распознанного текста в DOCX
#         docx_filename = f"{os.path.splitext(filename)[0]}.docx"
#         docx_file_path = os.path.join(fs.location, docx_filename)
#         save_text_to_docx(extracted_text, docx_file_path)
#
#         # Получение summary от модели Hugging Face
#         summary_text = send_to_ollama(extracted_text)
#
#         # Сохранение summary в DOCX
#         summary_docx_filename = f"{os.path.splitext(filename)[0]}_summary.docx"
#         summary_docx_file_path = os.path.join(fs.location, summary_docx_filename)
#         save_text_to_docx(summary_text, summary_docx_file_path)
#
#         # Возврат пути к файлам
#         response_data = {
#             'summary': summary_text,
#             'docx_url': fs.url(docx_filename),
#             'summary_docx_url': fs.url(summary_docx_file_path),
#             'progress': 100
#         }
#         return JsonResponse(response_data)
#
#     return render(request, 'pdfprocessor/upload.html')

from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from docx import Document
from docx.table import Table
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pytesseract
import os
from PyPDF2 import PdfReader
import torch
import camelot  # Для работы с таблицами в PDF
from huggingface_hub import login

# Аутентификация с Hugging Face
login('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')

# Использование модели LED для длинных текстов
model_name = "t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


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
    prompt = f"Вот мое ТЗ: {text} сделай summary по нему."
    inputs = tokenizer(prompt, return_tensors="pt", max_length=16384, truncation=True)
    with torch.no_grad():
        outputs = model.generate(inputs["input_ids"], max_length=1024, min_length=100, do_sample=False)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary


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