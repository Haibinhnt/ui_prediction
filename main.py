import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageOps
import pytesseract
import io


# Mã IMG2Txt và các phương thức convert PDF sang text

class IMG2Txt:
    def __init__(self):
        self.custom_config = r'--psm 3 --oem 3'
        self.blocks = None
        self.image = None

    def scan_image(self, img):
        self.texts = []
        self.image = ImageOps.grayscale(img)
        info_text = pytesseract.image_to_data(self.image, config=self.custom_config, lang="vie",
                                              output_type=pytesseract.Output.DICT)
        high_image = self.image.height
        data = []

        for i in range(len(info_text['text'])):
            point_data = {}
            if self.pre_clean_word_image(str(info_text['text'][i])):
                point_data["top"] = [info_text['left'][i], high_image - info_text['top'][i]]
                point_data["bot"] = [info_text['left'][i] + info_text['width'][i],
                                     high_image - info_text['top'][i] - info_text['height'][i]]
                point_data["height"] = info_text['height'][i]
                point_data["text"] = info_text['text'][i]
                point_data["len"] = len(point_data["text"])
                data.append(point_data)

        for _ in range(5):
            c1 = data
            data = self.merge_words_line(c1)
            if len(c1) == len(data):
                break

        blocks = self.merge_lines_block(data)

        for _ in range(5):
            c2 = blocks
            blocks = self.merge_blocks_para(blocks)
            if len(c2) == len(blocks):
                break

        for block in blocks:
            img1 = self.image.crop((block["top"][0] - 5, high_image - block["top"][1] - 5, block["bot"][0] + 5,
                                    high_image - block["bot"][1] + 5))
            text_blocks = pytesseract.image_to_string(img1, lang="vie", config=self.custom_config)
            self.texts.extend([self.clean_text_blocks(line) for line in text_blocks.split("\n") if line.strip()])

        self.blocks = blocks

        if not self.texts:
            return None

        output = self._construct_output()
        return output

    # Các phương thức merge_blocks_para, merge_lines_block, merge_words_line, pre_clean_word_image và clean_text_blocks sẽ giữ nguyên


# Hàm để chuyển đổi PDF thành hình ảnh từ file trong bộ nhớ
def pdf_to_images(pdf_file):
    images = convert_from_bytes(pdf_file.read())  # Sử dụng convert_from_bytes thay vì convert_from_path
    return images


# Hàm chuyển đổi ảnh thành văn bản
def convert_images_to_text(images):
    img2txt = IMG2Txt()
    texts = []

    for img in images:
        text = img2txt.scan_image(img)
        if text:
            texts.append(text)

    return "\n\n".join(texts)


# Hàm để chuyển đổi PDF thành văn bản và trả về file TXT dưới dạng str
def pdf_to_text(pdf_file):
    images = pdf_to_images(pdf_file)
    text = convert_images_to_text(images)

    return text


# Giao diện Streamlit
def main():
    st.title("Chuyển đổi PDF thành văn bản")

    # Tải lên file PDF
    uploaded_file = st.file_uploader("Tải lên file PDF", type="pdf")

    if uploaded_file is not None:
        # Đọc file PDF trực tiếp từ bộ nhớ (sử dụng io.BytesIO)
        pdf_file = io.BytesIO(uploaded_file.read())

        # Chuyển đổi PDF sang văn bản
        text = pdf_to_text(pdf_file)

        if text:
            # Hiển thị văn bản và cung cấp link tải về
            st.success("Chuyển đổi thành công!")
            st.text_area("Văn bản đã chuyển đổi:", text, height=300)

            # Cung cấp file TXT cho người dùng tải về
            st.download_button(
                label="Tải file văn bản (.txt)",
                data=text,
                file_name="converted_text.txt",
                mime="text/plain"
            )
        else:
            st.error("Không thể chuyển đổi văn bản từ PDF.")


if __name__ == "__main__":
    main()






