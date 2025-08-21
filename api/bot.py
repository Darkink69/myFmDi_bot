import os
import json
import requests
from flask import Flask, request

# Настройка переменных окружения
# TOKEN = os.getenv('TELEGRAM_TOKEN')
TOKEN = '8315097557:AAH4xALNwTxjecuAxzyUbCdLrsDBxi2tWQc'
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)


def send_message(chat_id, text):
    """Отправка сообщения через Telegram API"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None


@app.route('/')
def index():
    return 'Telegram Echo Bot is running! 🤖', 200


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Получаем данные от Telegram
        data = request.get_json()

        # Проверяем наличие сообщения
        if data and 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']

            # Проверяем, есть ли текст в сообщении
            if 'text' in message:
                user_text = message['text']
                user_name = message['from'].get('first_name', 'Пользователь')

                # Создаем ответное сообщение
                response_text = f"Привет, {user_name}! 🤖\n\nТы написал: <b>{user_text}</b>\n\nЯ эхо-бот и повторяю всё, что ты пишешь!"

                # Отправляем сообщение
                send_message(chat_id, response_text)

        return {'status': 'ok'}, 200

    except Exception as e:
        print(f"Error: {e}")
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука"""
    try:
        # URL для вебхука
        host = os.getenv('VERCEL_URL') or request.headers.get('Host')
        webhook_url = f"https://{host}/api/webhook"

        # Удаляем предыдущий вебхук
        delete_response = requests.get(f"{BASE_URL}/deleteWebhook")

        # Устанавливаем новый вебхук
        set_response = requests.post(
            f"{BASE_URL}/setWebhook",
            json={'url': webhook_url}
        )

        return {
            'status': 'success',
            'webhook_url': webhook_url,
            'delete_response': delete_response.json() if delete_response.status_code == 200 else None,
            'set_response': set_response.json() if set_response.status_code == 200 else None
        }, 200

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/info', methods=['GET'])
def info():
    """Информация о боте"""
    return {
        'bot': 'Telegram Echo Bot',
        'status': 'active',
        'features': ['Echo messages', 'Webhook support', 'Vercel deployment'],
        'endpoints': {
            'webhook': '/api/webhook',
            'set_webhook': '/api/set_webhook',
            'info': '/api/info'
        }
    }, 200


# Для локального тестирования
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)