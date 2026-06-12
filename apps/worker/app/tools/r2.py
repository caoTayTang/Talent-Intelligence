import boto3
from app.config import settings
from app.tools.documents import parse_document_bytes


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )


def download_r2_object(object_key: str) -> bytes:
    """
    Download a private R2 object by key
    """
    client = get_r2_client()
    response = client.get_object(Bucket=settings.r2_bucket, Key=object_key)

    return response["Body"].read()


def load_r2_text_object(object_key: str) -> str:
    file_bytes = download_r2_object(object_key)
    return parse_document_bytes(file_bytes, object_key)
