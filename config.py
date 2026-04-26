import os
from dotenv import load_dotenv

def config():
    """Загружает параметры подключения к БД из файла .env."""
    load_dotenv()
    return {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
