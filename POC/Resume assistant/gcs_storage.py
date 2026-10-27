import os
import uuid
import logging
from google.cloud import storage

# ----------------------------
# 1️⃣ GCS Config
# ----------------------------
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\AbdusSamad\Documents\dummy\gcp_key.json"
BUCKET_NAME = "demo-resume-file-storage"

def upload_to_gcs(file_path: str, filename: str) -> str:
    """
    Uploads a file to Google Cloud Storage and returns the GCS URI.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob_name = f"uploads/{uuid.uuid4()}_{filename}"
        blob = bucket.blob(blob_name)
        with open(file_path, "rb") as f:
            blob.upload_from_file(f, content_type="application/octet-stream")
        gcs_uri = f"gs://{BUCKET_NAME}/{blob_name}"
        logging.info(f"Uploaded file to GCS: {gcs_uri}")
        return gcs_uri
    except Exception as e:
        logging.error(f"GCS upload failed: {e}")
        raise
