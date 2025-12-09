import boto3
from botocore.client import Config
from typing import BinaryIO
import uuid
from ..config import settings

# Cloudflare R2 is S3-compatible
s3_client = boto3.client(
    's3',
    endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)


async def upload_file(file: BinaryIO, filename: str, content_type: str) -> str:
    """Upload file to R2 and return URL"""
    
    # Generate unique filename
    file_extension = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Upload to R2
    s3_client.upload_fileobj(
        file,
        settings.R2_BUCKET_NAME,
        unique_filename,
        ExtraArgs={'ContentType': content_type}
    )
    
    # Return public URL
    return f"https://{settings.R2_BUCKET_NAME}.{settings.R2_ACCOUNT_ID}.r2.dev/{unique_filename}"


async def delete_file(file_url: str) -> bool:
    """Delete file from R2"""
    try:
        # Extract filename from URL
        filename = file_url.split('/')[-1]
        s3_client.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=filename)
        return True
    except Exception:
        return False
