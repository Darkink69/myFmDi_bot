from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('BOT_TOKEN')
IMAGE_URL = "https://9qhr1l4qpuouftdm.public.blob.vercel-storage.com/assets/slipper.png"


def get_keyboard_json():
    """Создает клавиатуру в формате JSON"""
    return {
        "inline_keyboard": [
            [{"text": "Перейти в приложение", "callback_data": "app"}],
            [{"text": "Подробнее", "callback_data": "info"}]
        ]
    }


def send_telegram_message(chat_id, text, photo_url=None, reply_markup=None):
    """Отправляет сообщение через Telegram API"""
    try:
        if photo_url:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            data = {
                'chat_id': chat_id,
                'photo': photo_url,
                'caption': text,
                'reply_markup': json.dumps(
                    reply_markup) if reply_markup else None
            }
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'reply_markup': json.dumps(
                    reply_markup) if reply_markup else None
            }

        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Telegram Bot Webhook is working! ✅')

    def do_POST(self):
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            logger.info(f"Received update: {data}")

            # Обрабатываем сообщение
            if 'message' in data:
                message = data['message']
                chat_id = message['chat']['id']
                text = message.get('text', '')

                keyboard = get_keyboard_json()

                if text.startswith('/start'):
                    # Команда /start
                    first_name = message['from'].get('first_name', 'друг')
                    send_telegram_message(chat_id, f"Привет, {first_name}!",
                                          IMAGE_URL, keyboard)
                else:
                    # Обычное сообщение
                    send_telegram_message(chat_id, f"Привет, {text}!",
                                          IMAGE_URL, keyboard)

            # Обрабатываем callback от кнопок
            elif 'callback_query' in data:
                callback = data['callback_query']
                chat_id = callback['message']['chat']['id']
                callback_data = callback['data']

                # Отвечаем на нажатие кнопки
                answer_url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
                requests.post(answer_url, data={
                    'callback_query_id': callback['id']
                })

                # Отправляем сообщение в зависимости от кнопки
                if callback_data == 'app':
                    send_telegram_message(chat_id,
                                          "Функция 'Перейти в приложение' в разработке 🛠️")
                elif callback_data == 'info':
                    send_telegram_message(chat_id,
                                          "Здесь будет подробная информация ℹ️")

            # Успешный ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "ok"})
            self.wfile.write(response.encode('utf-8'))

        except Exception as e:
            logger.error(f"Error: {e}")
            # Всегда возвращаем 200 для Telegram
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "error", "message": str(e)})
            self.wfile.write(response.encode('utf-8'))