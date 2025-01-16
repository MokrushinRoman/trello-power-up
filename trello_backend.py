from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Trello API ключи
API_KEY = "твой_trello_api_key"
TOKEN = "твой_trello_token"

# Функция для работы с Trello API
def handle_trello_action(action_data):
    if action_data["action"] == "create_card":
        # Получаем ID доски
        boards_url = "https://api.trello.com/1/members/me/boards"
        boards = requests.get(boards_url, params={'key': API_KEY, 'token': TOKEN}).json()
        board_id = next(b['id'] for b in boards if b['name'] == action_data['board_name'])
        
        # Получаем ID списка
        lists_url = f"https://api.trello.com/1/boards/{board_id}/lists"
        lists = requests.get(lists_url, params={'key': API_KEY, 'token': TOKEN}).json()
        list_id = next(l['id'] for l in lists if l['name'] == action_data['list_name'])
        
        # Создаём карточку
        card_url = "https://api.trello.com/1/cards"
        response = requests.post(card_url, params={
            'key': API_KEY,
            'token': TOKEN,
            'idList': list_id,
            'name': action_data['card_name'],
            'desc': action_data.get('card_desc', "")
        })
        return response.json()

    elif action_data["action"] == "move_card":
        # Логика для перемещения карточки
        # Получи ID карточки и списка, чтобы обновить их.
        pass

# Endpoint для обработки запросов от GPT
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json  # Получаем JSON от GPT
    result = handle_trello_action(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000)
