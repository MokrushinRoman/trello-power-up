from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

app.config["DEBUG"] = True

# Константы для Trello API
TRELLO_API_KEY = "a735e40d5c7e8287555a60ac3bf51493"
TRELLO_TOKEN = "ATTAe14936be75ded476e373e3a51e85225e60bd53cccb67c877f805663489c927c542DA8AAD"
BASE_TRELLO_URL = "https://api.trello.com/1"

# Универсальная функция для получения ID объекта (доски или списка)
def get_trello_id(url, name, params):
    response = requests.get(url, params=params).json()
    return next((item['id'] for item in response if item['name'] == name), None)

# Обработка действий Trello
def handle_trello_action(action_data):
    action = action_data.get("action")

    if action == "create_card":
        board_name = action_data.get("board_name")
        list_name = action_data.get("list_name")
        card_name = action_data.get("card_name")
        card_desc = action_data.get("card_desc", "")

        if not board_name or not list_name or not card_name:
            return {"error": "Отсутствуют обязательные параметры"}

        # Получение ID доски
        board_id = get_trello_id(f"{BASE_TRELLO_URL}/members/me/boards", board_name, {
            'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN
        })
        if not board_id:
            return {"error": "Доска не найдена"}

        # Получение ID списка
        list_id = get_trello_id(f"{BASE_TRELLO_URL}/boards/{board_id}/lists", list_name, {
            'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN
        })
        if not list_id:
            return {"error": "Список не найден"}

        # Создание карточки
        response = requests.post(f"{BASE_TRELLO_URL}/cards", params={
            'key': TRELLO_API_KEY,
            'token': TRELLO_TOKEN,
            'idList': list_id,
            'name': card_name,
            'desc': card_desc
        })

        if response.status_code == 200:
            return {"status": "success", "message": "Карточка создана!"}
        else:
            return {"error": "Не удалось создать карточку", "details": response.text}

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

# Тестовый маршрут для проверки
@app.route("/", methods=["GET"])
def home():
    return "Flask сервер работает! 🚀", 200

if __name__ == "__main__":
    app.run(port=5000)
