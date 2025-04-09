import pytest
from fastapi.testclient import TestClient
import os
from main import app, init_environment
from config import settings
from db import connect
from unittest.mock import patch

@pytest.fixture(scope='session', autouse=True)
def override_dir():
    with patch.object(settings, 'app_data_directory', 'test_app_data') as mock:
        db_path = os.path.join(settings.app_data_directory, settings.db_file_name)
        if os.path.exists(db_path):
            os.remove(db_path)

        init_environment()
        yield mock
        
@pytest.fixture(scope='session')
def client():
    return TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def reset_database():
    yield  # Run the test

    # Clean up database after each test
    with connect() as conn:
        conn.execute("DELETE FROM detection")

    # Clean up files after each test
    image_dir = os.path.join(os.getcwd(), settings.app_data_directory, settings.images_directory)
    for file_name in os.listdir(image_dir):
        file_path = os.path.join(image_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)