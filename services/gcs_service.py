from google.cloud import storage

class GCSService:
    def __init__(self, credentials):
        self.client = storage.Client(credentials=credentials, project="vtal-inventariorede-prd")

    def upload_file(self, bucket_name: str, data: bytes, destination_blob_name: str) -> str:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(data, content_type='image/jpeg')
        return f"gs://{bucket_name}/{destination_blob_name}"