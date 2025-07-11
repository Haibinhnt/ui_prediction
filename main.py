import streamlit as st
from tools.pdf_to_txt import pdf_to_images, convert_images_to_text  # Thêm import từ file pdf_to_txt.py

## PDF to TXT
# Streamlit code
st.title("PDF to Text Converter")
st.write("Tải lên tệp PDF để chuyển đổi thành tệp văn bản (.txt).")

# Tải lên tệp PDF
uploaded_file = st.file_uploader("Chọn tệp PDF", type="pdf")

if uploaded_file is not None:
    # Lưu tệp PDF vào bộ nhớ tạm
    pdf_path = "/tmp/uploaded_pdf.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    # Chuyển đổi PDF thành hình ảnh, rồi chuyển hình ảnh thành văn bản
    images = pdf_to_images(pdf_path)
    text = convert_images_to_text(images)

    # Tạo tệp văn bản từ nội dung trích xuất
    if text:
        txt_file = "/tmp/output_text.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(text)

        # Cung cấp liên kết tải tệp .txt
        st.download_button(
            label="Tải xuống tệp văn bản",
            data=open(txt_file, "rb").read(),
            file_name="output_text.txt",
            mime="text/plain"
        )
    else:
        st.write("Không có văn bản nào được trích xuất từ tệp PDF.")

## Tokenize









