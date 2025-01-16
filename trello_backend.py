from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Константы для Trello API
TRELLO_API_KEY = "твой_trello_api_key"
TRELLO_TOKEN = "твой_trello_token"
BASE_TRELLO_URL = "https://api.trello.com/1"

# Функция для получения ID объекта (доски или списка)
def get_trello_id(url, name, params):
    response = requests.get(url, params=params).json()
    return next((item['id'] for item in response if item['name'] == name), None)

# Обработка действия с Trello
def handle_trello_action(action_data):
    action = action_data.get("action")

    if action == "create_card":
        board_name = action_data.get("board_name")
        list_name = action_data.get("list_name")
        card_name = action_data.get("card_name")
        card_desc = action_data.get("card_desc", "")

        # Получение ID доски
        board_id = get_trello_id(f"{BASE_TRELLO_URL}/members/me/boards", board_name, {
            'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN
        })
        if not board_id:
            return {"error": "Board not found"}

        # Получение ID списка
        list_id = get_trello_id(f"{BASE_TRELLO_URL}/boards/{board_id}/lists", list_name, {
            'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN
        })
        if not list_id:
            return {"error": "List not found"}

        # Создание карточки
        response = requests.post(f"{BASE_TRELLO_URL}/cards", params={
            'key': TRELLO_API_KEY,
            'token': TRELLO_TOKEN,
            'idList': list_id,
            'name': card_name,
            'desc': card_desc
        })
        return response.json()

    elif action == "move_card":
        # Логика для перемещения карточки (можно доработать при необходимости)
        return {"status": "move_card action not implemented"}

    return {"error": "Unsupported action"}

# Маршрут для вебхуков
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    result = handle_trello_action(data)
    return jsonify(result)

# Тестовый маршрут для проверки
@app.route("/", methods=["GET"])
def home():
    return "Flask сервер работает! 🚀", 200

if __name__ == "__main__":
    app.run(port=5000)
