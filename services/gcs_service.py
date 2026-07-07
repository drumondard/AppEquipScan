from google.cloud import storage
import os

def upload_file(file_obj, destination_blob_name):
    print(f"DEBUG GCS: Tentando salvar em {destination_blob_name}")
    """Faz upload de um arquivo para o GCS."""
    # O BUCKET_NAME deve ser apenas o nome do bucket, ex: 'meu-bucket'
    bucket_name = os.getenv("BUCKET_NAME") 
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Faz o upload
    blob.upload_from_file(file_obj)
    
    # Retorna a URL pública (ou o caminho)
    return f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"