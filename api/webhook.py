from flask import Flask, request, jsonify
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Настройки
TOKEN = os.getenv('BOT_TOKEN')
IMAGE_URL = "https://9qhr1l4qpuouftdm.public.blob.vercel-storage.com/assets/slipper.png"

# Инициализация приложения Telegram
application = Application.builder().token(TOKEN).build()


def get_keyboard():
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


@app.route('/api/webhook', methods=['POST', 'GET'])
def webhook_handler():
    if request.method == 'POST':
        try:
            # Получаем данные от Telegram
            data = request.get_json()
            logger.info(f"Received update: {data}")

            # Создаем объект Update
            update = Update.de_json(data, application.bot)

            # Асинхронная обработка
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(application.process_update(update))
            loop.close()

            return jsonify({"status": "ok"})

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            # Всегда возвращаем 200 Telegram!
            return jsonify({"status": "error", "message": str(e)})

    # GET запрос - для проверки работы
    return "Telegram Bot Webhook is working! ✅", 200


# Обработчик для Vercel
def handler(req):
    with app.app_context():
        return app.full_dispatch_request()