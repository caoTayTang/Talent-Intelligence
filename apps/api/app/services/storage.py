import re
import uuid

import boto3 # boto3 is AWS SDK for Python, but it can also be used to interact with Cloudflare R2 since R2 is S3-compatible

from app.config import settings

def create_presigned_upload_url(
    kind: str, file_name: str, content_type: str
) -> dict:
    """
    Geneate a R2 presign url 
    Return:
    - object_key: the key to be stored in DB, used for later retrieval
    - upload_url: the presigned URL for uploading
    - expires_in_seconds: URL expiration time
    """
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", file_name)
    object_key = f"{kind}/{uuid.uuid4()}/{safe_name}"

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id = settings.r2_access_key_id,
        aws_secret_access_key = settings.r2_secret_access_key,
        region_name = "auto",
    )

    upload_url = client.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.r2_bucket, "Key": object_key, "ContentType": content_type},
        ExpiresIn=3600,
    )

    return {
        "object_key": object_key,
        "upload_url": upload_url,
        "expires_in_seconds": 3600,
    }
