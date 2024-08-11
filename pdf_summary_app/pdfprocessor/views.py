from django.shortcuts import render
from .utils import extract_text_from_pdf, extract_text_from_images, send_to_ollama, create_summary_docx
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage


def upload_pdf(request):
    if request.method == 'POST' and request.FILES['pdf_file']:
        pdf_file = request.FILES['pdf_file']
        fs = FileSystemStorage()
        filename = fs.save(pdf_file.name, pdf_file)
        file_path = fs.path(filename)

        # Извлечение текста из PDF и получение ответа от модели
        extracted_text = extract_text_from_pdf(file_path)
        if not extracted_text.strip():
            extracted_text = extract_text_from_images(file_path)
        summary = send_to_ollama(extracted_text)

        # Создание DOCX файла с summary
        docx_url = None
        if summary:
            docx_file = create_summary_docx(summary)
            docx_filename = f'summary_{filename}.docx'
            docx_path = fs.save(docx_filename, docx_file)
            docx_url = fs.url(docx_filename)

        # Формируем JSON-ответ
        response_data = {
            'summary': summary,
            'docx_url': docx_url,
            'progress': 100
        }
        return JsonResponse(response_data)

    return render(request, 'pdfprocessor/upload.html')

