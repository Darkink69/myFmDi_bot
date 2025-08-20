from http.server import BaseHTTPRequestHandler
import json
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ContextTypes

# Настройка
TOKEN = os.getenv('BOT_TOKEN')
IMAGE_URL = "https://9qhr1l4qpuouftdm.public.blob.vercel-storage.com/assets/slipper.png"

# Инициализация приложения
application = Application.builder().token(TOKEN).build()


def get_keyboard():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Перейти в приложение", callback_data='app')],
        [InlineKeyboardButton("Подробнее", callback_data='info')]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_photo(
        photo=IMAGE_URL,
        caption=f"Привет, {user.first_name}!",
        reply_markup=get_keyboard()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_photo(
        photo=IMAGE_URL,
        caption=f"Привет, {update.message.text}!",
        reply_markup=get_keyboard()
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'app':
        await query.message.reply_text(
            "Функция 'Перейти в приложение' в разработке 🛠️")
    elif query.data == 'info':
        await query.message.reply_text("Здесь будет подробная информация ℹ️")


# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_click))


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Webhook is ready!')

    def do_POST(self):
        try:
            # Читаем данные
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Создаем и обрабатываем update
            update = Update.de_json(data, application.bot)

            # Запускаем асинхронную обработку
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Обрабатываем update
            loop.run_until_complete(application.process_update(update))

            loop.close()

            # Успешный ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "ok"})
            self.wfile.write(response.encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
            self.send_response(200)  # Всегда возвращаем 200 Telegram!
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "error", "message": str(e)})
            self.wfile.write(response.encode('utf-8'))