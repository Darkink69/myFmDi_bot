from flask import Flask, request, jsonify
import os
import logging
import asyncio
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

# Глобальная инициализация приложения
application = None


def init_bot():
    global application
    if application is None:
        application = Application.builder().token(TOKEN).build()

        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(button_click))

        # Запуск обработки обновлений
        application.initialize()


def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Перейти в приложение", callback_data='app')],
        [InlineKeyboardButton("Подробнее", callback_data='info')]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Processing start command for user {user.id}")
    await update.message.reply_photo(
        photo=IMAGE_URL,
        caption=f"Привет, {user.first_name}!",
        reply_markup=get_keyboard()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Processing message from user {user.id}")
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


@app.route('/api/webhook', methods=['POST', 'GET'])
def webhook_handler():
    if request.method == 'POST':
        try:
            # Инициализируем бота при первом вызове
            init_bot()

            # Получаем данные от Telegram
            data = request.get_json()
            logger.info(f"Received update: {data}")

            # Создаем объект Update
            update = Update.de_json(data, application.bot)

            # Добавляем обновление в очередь синхронно
            application.update_queue.put_nowait(update)
            logger.info(f"Update added to queue for processing")

            return jsonify({"status": "ok"})

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return jsonify({"status": "error", "message": str(e)})

    return "Telegram Bot Webhook is working! ✅", 200


# Обработчик для Vercel
def handler(req):
    with app.app_context():
        return app.full_dispatch_request()
