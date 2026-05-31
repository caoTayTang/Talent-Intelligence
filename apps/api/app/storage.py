import re
import uuid

import boto3

from app.config import settings


def create_presigned_upload_url(kind: str, file_name: str, content_type: str) -> dict:
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", file_name)
    object_key = f"{kind}/{uuid.uuid4()}/{safe_name}"

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

    upload_url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.r2_bucket,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=300,
    )

    return {
        "object_key": object_key,
        "upload_url": upload_url,
        "expires_in_seconds": 300,
    }
