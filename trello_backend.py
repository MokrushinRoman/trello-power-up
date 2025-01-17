import os
from dotenv import load_dotenv  # Импортируем dotenv для работы с .env файлами
from flask import Flask, request, jsonify
import requests

# Загружаем переменные из .env файла
load_dotenv()

app = Flask(__name__)

# Константы для Trello API, читаем их из окружения
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BASE_TRELLO_URL = "https://api.trello.com/1"

if not TRELLO_API_KEY or not TRELLO_TOKEN:
    raise ValueError("Необходимо задать переменные окружения TRELLO_API_KEY и TRELLO_TOKEN.")

# Универсальная функция для работы с Trello API
def trello_request(method, endpoint, params=None, data=None):
    """Обобщенная функция для выполнения запросов к Trello API."""
    url = f"{BASE_TRELLO_URL}/{endpoint}"
    params = params or {}
    params.update({'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN})
    try:
        response = requests.request(method, url, params=params, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка Trello API: {e}")
        return None

# Функция для получения ID объекта (доски или списка)
def get_trello_id(endpoint, name):
    """Ищет ID объекта по имени."""
    items = trello_request("GET", endpoint)
    if not items:
        return None
    name_lower = name.lower()
    return next((item['id'] for item in items if item['name'].lower() == name_lower), None)

# Функция обработки действий
def handle_trello_action(action_data):
    """Обрабатывает действия, переданные через вебхук."""
    action = action_data.get("action", "").lower()

    if action == "create_card":
        board_name = action_data.get("board_name", "").lower()
        list_name = action_data.get("list_name", "").lower()
        card_name = action_data.get("card_name")
        card_desc = action_data.get("card_desc", "")

        if not board_name or not list_name or not card_name:
            missing_params = []
            if not board_name:
                missing_params.append("'board_name'")
            if not list_name:
                missing_params.append("'list_name'")
            if not card_name:
                missing_params.append("'card_name'")
            return {"error": f"Отсутствуют обязательные параметры: {', '.join(missing_params)}."}

        # Получаем ID доски
        board_id = get_trello_id("members/me/boards", board_name)
        if not board_id:
            return {"error": f"Доска '{board_name}' не найдена"}

        # Получаем ID списка
        list_id = get_trello_id(f"boards/{board_id}/lists", list_name)
        if not list_id:
            return {"error": f"Список '{list_name}' не найден на доске '{board_name}'"}

        # Создаем карточку
        card = trello_request("POST", "cards", params={
            'idList': list_id,
            'name': card_name,
            'desc': card_desc
        })
        if card:
            return {"status": "success", "message": f"Карточка '{card_name}' создана в списке '{list_name}'!"}
        return {"error": "Не удалось создать карточку"}

    elif action == "move_card":
        return {"status": "move_card action not implemented"}

    return {"error": "Неизвестное действие"}

# Маршрут для вебхуков
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "Данные не переданы"}), 400

    result = handle_trello_action(data)
    return jsonify(result)

# Тестовый маршрут
@app.route("/", methods=["GET"])
def home():
    return "Flask сервер работает! 🚀", 200

if __name__ == "__main__":
    app.run(port=5000)
