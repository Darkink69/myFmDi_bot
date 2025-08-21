import os
from flask import Flask, request, jsonify
import requests
import json

# Настройка переменных окружения
TOKEN = os.getenv(
    'TELEGRAM_TOKEN')  # Установите этот токен в переменных окружения Vercel
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
    response = requests.post(url, json=payload)
    return response.json()


@app.route('/')
def index():
    return 'Bot is running!', 200


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Получаем данные от Telegram
        data = request.get_json()

        # Проверяем наличие сообщения
        if 'message' in data:
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

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука"""
    try:
        # URL для вебхука (замените на ваш Vercel URL)
        webhook_url = f"https://{request.host}/webhook"

        # Удаляем предыдущий вебхук
        requests.get(f"{BASE_URL}/deleteWebhook")

        # Устанавливаем новый вебхук
        response = requests.post(
            f"{BASE_URL}/setWebhook",
            json={'url': webhook_url}
        )

        return jsonify({
            'status': 'success',
            'webhook_url': webhook_url,
            'telegram_response': response.json()
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/info', methods=['GET'])
def info():
    """Информация о боте"""
    return jsonify({
        'bot': 'Telegram Echo Bot',
        'status': 'active',
        'features': ['Echo messages', 'Webhook support', 'Vercel deployment'],
        'endpoints': {
            'webhook': '/webhook',
            'set_webhook': '/set_webhook',
            'info': '/info'
        }
    }), 200


# Обработчик для Vercel
def handler(event, context):
    from mangum import Mangum
    handler = Mangum(app)
    return handler(event, context)


if __name__ == "__main__":
    # Для локального тестирования
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))