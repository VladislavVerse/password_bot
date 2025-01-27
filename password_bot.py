import sqlite3
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Создание базы данных
conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()

# Генерация пароля
def generate_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот для генерации и хранения паролей.\n\n"
        "Команды:\n"
        "/add - добавить пароль для сервиса\n"
        "/view - посмотреть все сохранённые пароли\n"
        "/delete_all - удалить все сохранённые пароли"
    )

# Добавление пароля
async def add_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите название сервиса:")
    context.user_data["adding_password"] = True

# Обработка текста после команды /add
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("adding_password"):
        service = update.message.text
        password = generate_password()
        cursor.execute("INSERT INTO passwords (service, password) VALUES (?, ?)", (service, password))
        conn.commit()
        context.user_data["adding_password"] = False
        await update.message.reply_text(
            f"Пароль для сервиса '{service}' создан: {password}"
        )
    else:
        await update.message.reply_text("Я не понял вас. Используйте /start для начала.")

# Просмотр паролей
async def view_passwords(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor.execute("SELECT service, password FROM passwords")
    rows = cursor.fetchall()

    if rows:
        message = "Список сохранённых паролей:\n\n"
        for service, password in rows:
            message += f"Сервис: {service}\nПароль: {password}\n\n"
    else:
        message = "Список паролей пуст."

    await update.message.reply_text(message)

# Удаление всех паролей
async def delete_all_passwords(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor.execute("DELETE FROM passwords")
    conn.commit()
    await update.message.reply_text("Все пароли удалены!")

# Основная функция
def main() -> None:
    # Создание приложения
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_password))
    application.add_handler(CommandHandler("view", view_passwords))
    application.add_handler(CommandHandler("delete_all", delete_all_passwords))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
