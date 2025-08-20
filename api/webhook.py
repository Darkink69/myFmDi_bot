from flask import Flask, request, jsonify
import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TOKEN = os.getenv('BOT_TOKEN')
IMAGE_URL = "https://9qhr1l4qpuouftdm.public.blob.vercel-storage.com/assets/slipper.png"


def get_keyboard():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Перейти в приложение", callback_data='app')],
        [InlineKeyboardButton("Подробнее", callback_data='info')]
    ])


def send_telegram_message(chat_id, text, photo_url=None, reply_markup=None):
    """Отправка сообщения через Telegram API"""
    if photo_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        data = {
            'chat_id': chat_id,
            'photo': photo_url,
            'caption': text,
            'reply_markup': reply_markup.to_json() if reply_markup else None
        }
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': reply_markup.to_json() if reply_markup else None
        }

    try:
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None


@app.route('/api/webhook', methods=['POST', 'GET'])
def webhook_handler():
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.info(f"Received update: {data}")

            update = Update.de_json(data, None)

            if update.message:
                chat_id = update.message.chat.id
                text = update.message.text

                if text == '/start':
                    # Отправляем фото с кнопками
                    keyboard = get_keyboard()
                    send_telegram_message(chat_id,
                                          f"Привет, {update.message.from_user.first_name}!",
                                          IMAGE_URL, keyboard)
                else:
                    # Отправляем ответ на сообщение
                    keyboard = get_keyboard()
                    send_telegram_message(chat_id, f"Привет, {text}!",
                                          IMAGE_URL, keyboard)

            elif update.callback_query:
                # Обработка нажатий кнопок
                chat_id = update.callback_query.message.chat.id
                data = update.callback_query.data

                if data == 'app':
                    send_telegram_message(chat_id,
                                          "Функция 'Перейти в приложение' в разработке 🛠️")
                elif data == 'info':
                    send_telegram_message(chat_id,
                                          "Здесь будет подробная информация ℹ️")

            return jsonify({"status": "ok"})

        except Exception as e:
            logger.error(f"Error: {e}")
            return jsonify({"status": "error", "message": str(e)})

    return "Telegram Bot Webhook is working! ✅", 200


def handler(req):
    with app.app_context():
        return app.full_dispatch_request()