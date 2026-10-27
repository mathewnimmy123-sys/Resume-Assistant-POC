import os
import tempfile
import logging
from google.cloud import storage
from docx import Document
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# 🔧 Point to your installed Tesseract binary
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def parse_resume_from_gcs(gcs_uri: str) -> str:
    try:
        # Validate GCS URI
        if not gcs_uri.startswith("gs://"):
            raise ValueError("Invalid GCS URI format")

        _, bucket_name, *blob_parts = gcs_uri.split("/")
        blob_name = "/".join(blob_parts)

        # Download file to temp location
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            blob.download_to_filename(temp_file.name)
            file_path = temp_file.name
            file_ext = os.path.splitext(file_path)[-1].lower()

        # Extract text
        text = ""
        if file_ext == ".pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            # 🔍 If PyPDF2 fails, try OCR fallback
            if not text.strip():
                images = convert_from_path(file_path)
                for img in images:
                    ocr_text = pytesseract.image_to_string(img)
                    text += ocr_text + "\n"

        elif file_ext == ".docx":
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        logging.info(f"Extracted resume text (first 500 chars):\n{text[:500]}")
        if not text.strip():
            raise ValueError("Resume parsing failed: no text extracted")

        return text.strip()

    except Exception as e:
        logging.error(f"Resume parsing error: {e}")
        return "Resume parsing failed. Please provide a properly formatted resume for analysis."
