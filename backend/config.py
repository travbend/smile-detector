from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    app_data_directory: str = "app_data"
    images_directory: str = "images"
    max_image_size: int = 10000000
    db_file_name: str = "smile-detector.db"
    
settings = Settings()