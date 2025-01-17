from flask import Flask, request, jsonify
from utils.helpers import get_trello_id
from services.trello_service import trello_request

app = Flask(__name__)

# Обработка действий
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

    elif action == "update_card":
        card_name = action_data.get("card_name")
        board_name = action_data.get("board_name", "").lower()
        new_name = action_data.get("new_name")

        if not card_name or not board_name or not new_name:
            return {"error": "Параметры 'card_name', 'board_name' и 'new_name' обязательны для действия 'update_card'."}

        # Получаем ID доски
        board_id = get_trello_id("members/me/boards", board_name)
        if not board_id:
            return {"error": f"Доска '{board_name}' не найдена"}

        # Поиск карточки
        cards = trello_request("GET", f"boards/{board_id}/cards")
        card_id = next((c['id'] for c in cards if c['name'] == card_name), None)
        if not card_id:
            return {"error": f"Карточка '{card_name}' не найдена на доске '{board_name}'"}

        # Обновляем название карточки
        updated_card = trello_request("PUT", f"cards/{card_id}", params={"name": new_name})
        if updated_card:
            return {"status": "success", "message": f"Название карточки '{card_name}' обновлено на '{new_name}'."}
        return {"error": "Не удалось обновить название карточки"}

    elif action == "update_card_desc":
        card_name = action_data.get("card_name")
        board_name = action_data.get("board_name", "").lower()
        new_desc = action_data.get("new_desc", "")

        if not card_name or not board_name:
            return {"error": "Параметры 'card_name' и 'board_name' обязательны для действия 'update_card_desc'."}

        # Получаем ID доски
        board_id = get_trello_id("members/me/boards", board_name)
        if not board_id:
            return {"error": f"Доска '{board_name}' не найдена"}

        # Поиск карточки
        cards = trello_request("GET", f"boards/{board_id}/cards")
        card_id = next((c['id'] for c in cards if c['name'] == card_name), None)
        if not card_id:
            return {"error": f"Карточка '{card_name}' не найдена на доске '{board_name}'"}

        # Обновляем описание карточки
        updated_card = trello_request("PUT", f"cards/{card_id}", params={"desc": new_desc})
        if updated_card:
            return {"status": "success", "message": f"Описание карточки '{card_name}' обновлено."}
        return {"error": "Не удалось обновить описание карточки"}

    elif action == "delete_card":
        card_name = action_data.get("card_name")
        board_name = action_data.get("board_name", "").lower()

        if not card_name or not board_name:
            return {"error": "Параметры 'card_name' и 'board_name' обязательны для действия 'delete_card'."}

        # Получаем ID доски
        board_id = get_trello_id("members/me/boards", board_name)
        if not board_id:
            return {"error": f"Доска '{board_name}' не найдена"}

        # Поиск карточки
        cards = trello_request("GET", f"boards/{board_id}/cards")
        card_id = next((c['id'] for c in cards if c['name'] == card_name), None)
        if not card_id:
            return {"error": f"Карточка '{card_name}' не найдена на доске '{board_name}'"}

        # Удаляем карточку
        deleted_card = trello_request("DELETE", f"cards/{card_id}")
        if deleted_card:
            return {"status": "success", "message": f"Карточка '{card_name}' удалена."}
        return {"error": "Не удалось удалить карточку"}

    elif action == "get_all_cards":
        board_name = action_data.get("board_name", "").lower()
        list_name = action_data.get("list_name", "").lower()

        if not board_name or not list_name:
            return {"error": "Параметры 'board_name' и 'list_name' обязательны для действия 'get_all_cards'."}

        # Получаем ID доски
        board_id = get_trello_id("members/me/boards", board_name)
        if not board_id:
            return {"error": f"Доска '{board_name}' не найдена"}

        # Получаем ID списка
        list_id = get_trello_id(f"boards/{board_id}/lists", list_name)
        if not list_id:
            return {"error": f"Список '{list_name}' не найден на доске '{board_name}'"}

        # Получаем карточки
        cards = trello_request("GET", f"lists/{list_id}/cards")
        if cards is not None:
            simplified_cards = [{"name": card["name"], "desc": card["desc"], "url": card["url"]} for card in cards]
            return {"status": "success", "cards": simplified_cards}

        return {"error": "Не удалось получить список карточек."}

    elif action == "move_card":
        board_name = action_data.get("board_name", "").lower()
        current_list_name = action_data.get("current_list_name", "").lower()
        new_list_name = action_data.get("new_list_name", "").lower()
        card_name = action_data.get("card_name")

        if not board_name or not current_list_name or not new_list_name or not card_name:
            return {"error": "Параметры 'board_name', 'current_list_name', 'new_list_name' и 'card_name' обязательны для действия 'move_card'."}

        # Получаем ID доски
        board_id = get_trello_id("members/me/boards", board_name)
        if not board_id:
            return {"error": f"Доска '{board_name}' не найдена"}

        # Получаем ID текущего списка
        current_list_id = get_trello_id(f"boards/{board_id}/lists", current_list_name)
        if not current_list_id:
            return {"error": f"Список '{current_list_name}' не найден на доске '{board_name}'"}

        # Получаем ID нового списка
        new_list_id = get_trello_id(f"boards/{board_id}/lists", new_list_name)
        if not new_list_id:
            return {"error": f"Список '{new_list_name}' не найден на доске '{board_name}'"}

        # Поиск карточки
        cards = trello_request("GET", f"lists/{current_list_id}/cards")
        card_id = next((c['id'] for c in cards if c['name'] == card_name), None)
        if not card_id:
            return {"error": f"Карточка '{card_name}' не найдена в списке '{current_list_name}' на доске '{board_name}'"}

        # Перемещение карточки
        moved_card = trello_request("PUT", f"cards/{card_id}", params={"idList": new_list_id})
        if moved_card:
            return {"status": "success", "message": f"Карточка '{card_name}' перемещена из списка '{current_list_name}' в '{new_list_name}'."}
        return {"error": "Не удалось переместить карточку."}

    elif action == "get_board_info":
        board_name = action_data.get("board_name", "").lower()

        if not board_name:
            return {"error": "Параметр 'board_name' обязателен для действия 'get_board_info'."}

        # Получаем ID доски
        board_id = get_trello_id("members/me/boards", board_name)
        if not board_id:
            return {"error": f"Доска '{board_name}' не найдена."}

        # Получаем списки на доске
        lists = trello_request("GET", f"boards/{board_id}/lists")
        if not lists:
            return {"error": "Не удалось получить списки на доске."}

        # Формируем структуру доски
        board_info = {
            "name": board_name,
            "lists": []
        }

        for lst in lists:
            list_id = lst["id"]
            list_name = lst["name"]

            # Получаем карточки в списке
            cards = trello_request("GET", f"lists/{list_id}/cards")
            simplified_cards = [{"name": card["name"], "desc": card["desc"], "url": card["url"]} for card in cards]

            board_info["lists"].append({
                "name": list_name,
                "cards": simplified_cards
            })

        return {"status": "success", "board": board_info}

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
