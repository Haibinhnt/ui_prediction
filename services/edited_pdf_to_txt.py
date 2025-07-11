import os
import pandas as pd
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import shutil
import fitz  # PyMuPDF
import re
from PIL import Image
import pytesseract

def is_scanned_pdf(pdf_path):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        
        # Check if text is selectable on each page
        for page in pdf_document:
            text = page.get_text()
            if len(text.strip()) == 0:
                # If no selectable text found, it's likely a scanned PDF
                return True
        
        return False
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

def classify_pdfs(source_folder, scanned_folder, edited_folder, error_folder):
    # Create destination folders if they don't exist
    os.makedirs(scanned_folder, exist_ok=True)
    os.makedirs(edited_folder, exist_ok=True)
    os.makedirs(error_folder, exist_ok=True)
    
    # Iterate over all files in the source folder
    for filename in os.listdir(source_folder):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(source_folder, filename)
            is_scanned = is_scanned_pdf(pdf_path)
            if is_scanned is None:
                # Move the file to the error folder if there was an error processing it
                shutil.move(pdf_path, os.path.join(error_folder, filename))
                continue
            if is_scanned:
                shutil.move(pdf_path, os.path.join(scanned_folder, filename))
            else:
                shutil.move(pdf_path, os.path.join(edited_folder, filename))

def is_scanned_page(image):
    text = pytesseract.image_to_string(image)
    return len(text.strip()) > 0

def classify_pdf(pdf_path):
    pdf_reader = PdfReader(open(pdf_path, 'rb'))
    total_pages = len(pdf_reader.pages)
    
    edited_text_pages = 0
    scanned_pages = 0
    
    # Check for edited text
    edited_text = extract_text(pdf_path)
    if edited_text.strip():
        edited_text_pages = len(edited_text.strip().split('\n\n'))
    
    # Check for scanned images
    images = convert_from_path(pdf_path)
    for image in images:
        if is_scanned_page(image):
            scanned_pages += 1

    return {
        "total_pages": total_pages,
        "edited_text_pages": edited_text_pages,
        "scanned_pages": scanned_pages
    }

def classify_pdfs_in_folder(folder_path):
    data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(folder_path, file_name)
            classification = classify_pdf(file_path)
            classification['file_name'] = file_name
            data.append(classification)
    
    df = pd.DataFrame(data)
    return df

def extract_text(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Initialize an empty string to store text
    text = ""

    # Iterate through each page of the PDF
    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document.load_page(page_num)

        # Extract text from the page
        page_text = page.get_text()

        # Append the modified page text to the overall text
        text += page_text

    # Close the PDF document
    pdf_document.close()

    return text


def convert_pdfs_in_folder(source_folder_path, destination_folder_path):
    # Get a list of all PDF files in the source folder
    pdf_files = [f for f in os.listdir(source_folder_path) if f.lower().endswith('.pdf')]

    # Ensure the destination folder exists
    os.makedirs(destination_folder_path, exist_ok=True)

    # Iterate over each PDF file
    for pdf_file in pdf_files:
        pdf_path = os.path.join(source_folder_path, pdf_file)
        text_path = os.path.join(destination_folder_path, os.path.splitext(pdf_file)[0] + '.txt')

        # Extract text without tables
        text = extract_text(pdf_path)

        # Write the extracted text to a text file in the destination folder
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)

def process_pdfs_for_all_years(start_year, end_year):
    for year in range(start_year, end_year + 1):
        source_folder_path = f'data/{year}/Edited_pdf'
        destination_folder_path = f'data/{year}/Edited_text'
        convert_pdfs_in_folder(source_folder_path, destination_folder_path)
        print(f'Processed PDFs for the year {year}')    

def process_text_file(content):
    # Loại bỏ các khoảng trắng thừa (giữ lại khoảng trắng phân cách giữa các từ)
    content_single_space = re.sub(r'\s+', ' ', content).strip()

    # Loại bỏ các ký tự không cần thiết (giữ lại chữ cái, chữ số và dấu câu cơ bản)
    cleaned_content = re.sub(r'[^a-zA-Z0-9.,?!ăâđêôơưĂÂĐÊÔƠƯáàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸ ]', '', content_single_space)

    return cleaned_content

def process_files_txt_in_folder(input_folder, output_folder):
    # Tạo thư mục đầu ra nếu nó không tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Duyệt qua tất cả các file trong thư mục đầu vào
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            # Đọc nội dung của file
            with open(input_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Xử lý nội dung của file
            processed_content = process_text_file(content)

            # Lưu nội dung đã xử lý vào file mới
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(processed_content)

            print(f"File {filename} đã được xử lý và lưu tại: {output_file_path}")