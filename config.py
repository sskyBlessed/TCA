import os
from dotenv import load_dotenv

ENV_PATH = ".env"

def ensure_env():
    if not os.path.exists(ENV_PATH):
        api_id = input("Введите ваш API_ID: ").strip()
        api_hash = input("Введите ваш API_HASH: ").strip()
        session_name = input("Введите имя сессии (SESSION_NAME): ").strip()

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f"API_ID={api_id}\n")
            f.write(f"API_HASH={api_hash}\n")
            f.write(f"SESSION_NAME={session_name}\n")

        print("Файл .env создан.")
    else:
        print(".env найден, продолжаем...")

    load_dotenv(ENV_PATH)

# Получение переменных (можно импортировать прямо из config)
ensure_env()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")
