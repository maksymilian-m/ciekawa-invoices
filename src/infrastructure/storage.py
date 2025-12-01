import logging
from pathlib import Path
from src.ports.interfaces import FileStorage

logger = logging.getLogger(__name__)

class LocalFileStorage(FileStorage):
    def __init__(self, base_dir: str = "data/raw_pdfs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, filename: str, content: bytes) -> str:
        file_path = self.base_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"Saved file locally: {file_path}")
        return str(file_path.absolute())

class GCSFileStorage(FileStorage):
    def __init__(self, bucket_name: str):
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(bucket_name)

    def save_file(self, filename: str, content: bytes) -> str:
        blob = self.bucket.blob(filename)
        blob.upload_from_string(content)
        
        # Return the gs:// URI or public URL depending on needs. 
        # For internal processing, gs:// is often better, but for access, https might be needed.
        # Let's return the gs:// URI for now as it's standard for GCP services.
        gcs_uri = f"gs://{self.bucket_name}/{filename}"
        logger.info(f"Saved file to GCS: {gcs_uri}")
        return gcs_uri
