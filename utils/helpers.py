from services.trello_service import trello_request

def get_trello_id(endpoint, name):
    """Ищет ID объекта (доски или списка) по имени."""
    items = trello_request("GET", endpoint)
    if not items:
        print(f"Ошибка: Объекты из {endpoint} не найдены.")
        return None
    name_lower = name.lower()
    return next((item['id'] for item in items if item['name'].lower() == name_lower), None)
