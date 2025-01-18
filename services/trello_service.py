import requests
from config import TRELLO_API_KEY, TRELLO_TOKEN, BASE_TRELLO_URL

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

# Проверка ключей Trello
def validate_trello_keys():
    """Проверяет, работают ли ключи API и токен."""
    response = trello_request("GET", "members/me")
    if not response:
        raise ValueError("Ошибка проверки: Проверьте TRELLO_API_KEY и TRELLO_TOKEN.")
    print(f"Ключи валидны. Имя пользователя Trello: {response.get('fullName', 'Неизвестно')}")

# Вызываем в начале для проверки ключей
validate_trello_keys()
