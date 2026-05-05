import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from src.core.config import get_settings


class CloudinaryService:
    def __init__(self):
        settings = get_settings()
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
        )

    async def upload(self, file: UploadFile) -> str:
        content = await file.read()
        result = cloudinary.uploader.upload(
            content,
            use_filename=True,
            unique_filename=True,
            overwrite=False,
            transformation=[{"width": 800, "height": 600, "crop": "limit"}],
        )
        return result["secure_url"]
