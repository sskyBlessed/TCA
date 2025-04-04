import logging
from telethon import TelegramClient
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest

logging.basicConfig(level=logging.DEBUG)


class TelegramService:
    """Сервис для работы с Telegram API (добавление контактов)."""
    
    def __init__(self, api_id: str, api_hash: str, session_name: str):
        self.client = TelegramClient(session_name, api_id, api_hash)

    async def start(self):
        """Запускает клиент Telegram."""
        await self.client.start()

    async def stop(self):
        """Останавливает клиент Telegram."""
        await self.client.disconnect()

    async def add_contacts(self, contacts: list, progress_callback) -> tuple:
        """
        Добавляет контакты в Telegram.

        :param contacts: Список контактов (строки формата "номер имя фамилия").
        :param progress_callback: Функция для обновления прогресса.
        :return: Кортеж (добавлено, уже добавлено, не найдено, детали).
        """
        results = []
        added, already_added, not_found = 0, 0, 0
        total = len(contacts)

        for i, contact_data in enumerate(contacts):
            identifier, first_name, last_name = self.parse_contact_data(contact_data)

            try:
                user = await self.client.get_entity(identifier)
                if user.contact:
                    already_added += 1
                    results.append((identifier, "уже добавлен"))
                    continue  # Пропускаем добавление
            except Exception:
                pass  # Контакт не найден, пробуем добавить

            contact = InputPhoneContact(
                client_id=0,
                phone=identifier,
                first_name=first_name,
                last_name=last_name
            )
            result = await self.client(ImportContactsRequest([contact]))

            if result.users:
                added += 1
                results.append((identifier, "добавлен"))
            else:
                not_found += 1
                results.append((identifier, "не найден"))

            progress_callback((i + 1) / total)

        return added, already_added, not_found, results

    @staticmethod
    def parse_contact_data(contact_str: str) -> tuple:
        """
        Разбирает строку контакта.

        :param contact_str: Строка с данными (номер имя фамилия).
        :return: Кортеж (номер, имя, фамилия).
        """
        parts = contact_str.strip().split(maxsplit=1)
        identifier = parts[0] if parts else ""

        name_part = parts[1] if len(parts) > 1 else ""
        name_parts = name_part.split(maxsplit=1)

        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        return identifier, first_name, last_name