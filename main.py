import time
import streamlit as st
from pdf2image import convert_from_path
import pytesseract
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import base64

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="PDF to Text Converter",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Hàm chuyển ảnh thành Base64 ---
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_path = "image/hinh-nen.png"  # hoặc .png, .jpeg tùy file
b64 = img_to_base64(img_path)

# --- CSS Nhúng Background cho Toàn Bộ Ứng Dụng ---
st.markdown(
    f"""
    <style>
    /* Toàn bộ ứng dụng */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        position: relative;
    }}
    /* Overlay trắng 70% (tuỳ chọn) */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255,255,255,0.6);
        pointer-events: none;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- CSS  ---
st.markdown(
    """
    <style>
    /* Header */
    h1 { color: #0288d1; }

    /* Buttons: nền trắng, chữ đen */
    .stButton>button {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stButton>button:hover {
        background-color: #f0f0f0;
    }

    /* Progress bar */
    .stProgress>div>div>div>div {
        background-color: #0288d1 !important;
    }

    /* Sidebar: nền xanh hoàng gia và chữ trắng */
    [data-testid="stSidebar"] {
        background-color: #4662E9 !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] {
    background-color: rgba(70, 98, 233, 0.7) !important; /* 70% opacity */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- NỘI DUNG TRÊN SIDEBAR ---
with st.sidebar:
    st.title("📊 Dự án nghiên cứu")
    st.write("""
**Nghiên cứu nội dung tường thuật trên báo cáo thường niên và mối quan hệ tương quan giữa nội dung tường thuật với khả năng sinh lợi của các công ty niêm yết tại Việt Nam**
""")

# --- HÀM XỬ LÝ ---
def pdf_to_images(pdf_path: str, dpi: int = 150):
    return convert_from_path(pdf_path, dpi=dpi)

def ocr_image(img) -> str:
    return pytesseract.image_to_string(img, lang='vie+eng')

def convert_images_to_text_parallel(images: list) -> str:
    progress = st.progress(0)
    total = len(images)
    results = [''] * total
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(ocr_image, img): idx for idx, img in enumerate(images)}
        completed = 0
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except:
                results[idx] = ""
            completed += 1
            progress.progress(completed / total)
    return "\n".join(results)

# --- SESSION STATE ---
if 'txt_path' not in st.session_state:
    st.session_state.txt_path = None
    st.session_state.elapsed = None

# --- KHU VỰC CHÍNH: INPUT CONTROLS + KẾT QUẢ ---
st.title("📄 PDF to Text Converter")
st.write("Tải lên tệp PDF và nhấn nút để chuyển đổi sang text:")

uploaded_file = st.file_uploader("Chọn tệp PDF", type="pdf")
start_btn = st.button("▶️ Bắt đầu chuyển đổi")

if start_btn and uploaded_file and st.session_state.txt_path is None:
    pdf_path = "/tmp/uploaded_pdf.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())
    start_time = time.time()
    with st.spinner("Đang xử lý PDF, vui lòng chờ..."):
        images = pdf_to_images(pdf_path)
        text = convert_images_to_text_parallel(images)
    st.session_state.elapsed = time.time() - start_time

    if text.strip():
        txt_path = "/tmp/output_text.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        st.session_state.txt_path = txt_path
        st.success(f"✅ Hoàn tất trong {st.session_state.elapsed:.2f} giây.")
    else:
        st.error(f"❌ Không trích xuất được văn bản ({st.session_state.elapsed:.2f} giây).")

if st.session_state.txt_path:
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Tải xuống tệp văn bản",
            data=open(st.session_state.txt_path, "rb").read(),
            file_name="output_text.txt",
            mime="text/plain"
        )
    with col2:
        if st.button("🔄 Chuyển file khác"):
            st.session_state.txt_path = None
            st.rerun()
