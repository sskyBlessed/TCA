import customtkinter as ctk
import tkinter.filedialog as fd
import asyncio
from services import TelegramService, StorageService
from config import API_ID, API_HASH, SESSION_NAME
import threading

class TelegramContactAdderApp:
    """Графический интерфейс для добавления контактов в Telegram."""

    def __init__(self, root):
        self.root = root
        self.root.title("Добавление контактов в Telegram")
        self.root.geometry("500x400")

        self.file_path = ctk.StringVar()
        self.service = TelegramService(API_ID, API_HASH, SESSION_NAME)

        # UI Elements
        self.label = ctk.CTkLabel(root, text="Выберите файл со списком контактов:")
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(root, textvariable=self.file_path, width=300)
        self.entry.pack()

        self.browse_button = ctk.CTkButton(root, text="Обзор", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.start_button = ctk.CTkButton(root, text="Запустить", command=self.start_addition)
        self.start_button.pack(pady=10)

        self.progress = ctk.CTkProgressBar(root, width=300)
        self.progress.set(0)
        self.progress.pack(pady=5)

        self.status_label = ctk.CTkLabel(root, text="Статус: Ожидание...")
        self.status_label.pack(pady=10)

        self.save_button = ctk.CTkButton(root, text="Сохранить результаты", command=self.save_results, state='disabled')
        self.save_button.pack(pady=5)
        
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        self.results = None

    def browse_file(self):
        """Выбор файла с контактами."""
        file = fd.askopenfilename(filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
        self.file_path.set(file)

    def start_addition(self):
        """Запуск процесса добавления контактов."""
        file_path = self.file_path.get()
        if not file_path:
            self.status_label.configure(text="Ошибка: файл не выбран!")
            return

        contacts = StorageService.load_contacts(file_path)
        asyncio.run_coroutine_threadsafe(self.process_contacts(contacts), self.loop)

    async def process_contacts(self, contacts):
        """Асинхронный процесс добавления контактов в Telegram."""
        self.status_label.configure(text="Запуск...")
        await self.service.start()
        self.results = await self.service.add_contacts(contacts, self.progress.set)
        await self.service.stop()

        self.status_label.configure(text=f"Готово! Добавлено: {self.results[0]}, Уже добавлены: {self.results[1]}, Не найдено: {self.results[2]}")
        self.save_button.configure(state='normal')

    def save_results(self):
        """Сохранение результатов в файл."""
        file_path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
        if file_path:
            StorageService.save_results(file_path, self.results[:3], self.results[3])
            self.status_label.configure(text="Результаты сохранены")


if __name__ == "__main__":
    app = ctk.CTk()
    TelegramContactAdderApp(app)
    app.mainloop()
