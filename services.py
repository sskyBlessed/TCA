import logging
from telethon import TelegramClient
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon import functions

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)


class TelegramService:
    """Сервис для работы с Telegram API (добавление контактов)."""

    def __init__(self, api_id: str, api_hash: str, session_name: str):
        """Инициализация клиента Telegram."""
        self.client = TelegramClient(session_name, api_id, api_hash)

    async def start(self):
        """Запуск клиента Telegram."""
        await self.client.start()

    async def stop(self):
        """Остановка клиента Telegram."""
        await self.client.disconnect()

    async def add_contacts(self, contacts: list, progress_callback) -> tuple:
        """
        Добавление контактов в Telegram.

        :param contacts: Список строк с контактами (номер, имя, фамилия).
        :param progress_callback: Функция для отслеживания прогресса.
        :return: Кортеж (добавлено, уже добавлено, не найдено, результаты).
        """
        results = []
        added, already_added, not_found = 0, 0, 0
        total = len(contacts)

        for i, contact_data in enumerate(contacts):
            identifier, first_name, last_name = self.parse_contact_data(contact_data)

            try:
                # Проверка, добавлен ли контакт
                user = await self.client.get_entity(identifier)
                if user.contact:
                    already_added += 1
                    results.append((identifier, "уже добавлен"))
                    continue
            except Exception:
                pass  # Игнорируем ошибки, если контакт не найден

            # Добавление контакта в Telegram
            if identifier.startswith('@') or identifier[0].isalpha():
                result = await self.client(functions.contacts.AddContactRequest(
                    id=identifier, first_name=first_name, last_name=last_name, phone='', add_phone_privacy_exception=True
                ))
                if result.users:
                    added += 1
                    results.append((identifier, "добавлен"))
                else:
                    not_found += 1
                    results.append((identifier, "не найден"))
            else:
                contact = InputPhoneContact(
                    client_id=0, phone=identifier, first_name=first_name, last_name=last_name
                )
                result = await self.client(ImportContactsRequest([contact]))

                if result.users:
                    added += 1
                    results.append((identifier, "добавлен"))
                else:
                    not_found += 1
                    results.append((identifier, "не найден"))

            # Обновление прогресса
            progress_callback((i + 1) / total)

        return added, already_added, not_found, results

    @staticmethod
    def parse_contact_data(contact_str: str) -> tuple:
        """
        Разбирает строку контакта на идентификатор, имя и фамилию.

        :param contact_str: Строка с контактными данными.
        :return: Кортеж (идентификатор, имя, фамилия).
        """
        parts = contact_str.strip().split(maxsplit=1)
        identifier = parts[0] if parts else ""

        name_part = parts[1] if len(parts) > 1 else ""
        name_parts = name_part.split(maxsplit=1)

        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        return identifier, first_name, last_name


class StorageService:
    """Сервис для работы с файлами (загрузка и сохранение результатов)."""

    @staticmethod
    def load_contacts(file_path: str) -> list:
        """
        Загружает контакты из файла.

        :param file_path: Путь к файлу.
        :return: Список строк с контактами.
        """
        contacts = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                contacts = [line.strip() for line in file if line.strip()]
        except Exception as e:
            logging.error(f"Ошибка загрузки файла: {e}")
        return contacts

    @staticmethod
    def save_results(file_path: str, summary: tuple, details: list):
        """
        Сохраняет результаты добавления контактов в файл.

        :param file_path: Путь к файлу.
        :param summary: Итоги (добавлено, уже добавлено, не найдено).
        :param details: Подробности (контакт, статус).
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(f"Итоги: Добавлено - {summary[0]}, Уже было - {summary[1]}, Не найдено - {summary[2]}\n\n")
                for contact, status in details:
                    file.write(f"{contact} - {status}\n")
        except Exception as e:
            logging.error(f"Ошибка сохранения файла: {e}")


# Пример использования
if __name__ == "__main__":
    # Параметры API и сессии
    api_id = "your_api_id"
    api_hash = "your_api_hash"
    session_name = "your_session_name"

    # Загружаем контакты из файла
    contacts_file = "contacts.txt"
    contacts = StorageService.load_contacts(contacts_file)

    # Создаем экземпляр сервиса Telegram
    telegram_service = TelegramService(api_id, api_hash, session_name)

    # Пример прогресса добавления контактов
    def progress_callback(progress):
        print(f"Прогресс: {progress * 100:.2f}%")

    # Добавляем контакты
    added, already_added, not_found, results = telegram_service.add_contacts(contacts, progress_callback)

    # Сохраняем результаты в файл
    results_file = "add_results.txt"
    StorageService.save_results(results_file, (added, already_added, not_found), results)

    # Останавливаем сервис
    import asyncio
    asyncio.run(telegram_service.stop())
