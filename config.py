import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Читаем переменные окружения
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BASE_TRELLO_URL = "https://api.trello.com/1"

# Проверяем наличие ключей
if not TRELLO_API_KEY or not TRELLO_TOKEN:
    raise ValueError("Необходимо задать переменные окружения TRELLO_API_KEY и TRELLO_TOKEN.")
