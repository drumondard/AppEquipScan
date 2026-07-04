from google.cloud import storage
import os

class GCSService:
    def __init__(self, credentials=None):
        # O storage.Client() detectará automaticamente o arquivo JSON mapeado no volume
        # quando o argumento credentials for None
        self.client = storage.Client(project="vtal-inventariorede-prd")

    def upload_file(self, bucket_name, data, destination_blob_name):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(data, content_type='image/jpeg')
        return blob.public_url