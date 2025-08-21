import os
import json
import requests
from flask import Flask, request, Response

# Настройка переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_BOT_TOKEN')
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

IMAGE_URL = "https://s3.twcstorage.ru/c6bae09a-a5938890-9b68-453c-9c54-76c439a70d3e/Roulette/10_000.png"

app = Flask(__name__)


def send_message(chat_id, text):
    """Отправка сообщения через Telegram API"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None


def send_photo(chat_id, photo_url, caption=None):
    """Отправка фото через Telegram API"""
    url = f"{BASE_URL}/sendPhoto"
    payload = {
        'chat_id': chat_id,
        'photo': photo_url
    }
    if caption:
        payload['caption'] = caption
        payload['parse_mode'] = 'HTML'

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending photo: {e}")
        return None


@app.route('/')
def index(chat_id, photo_url, caption=None):
    send_photo(chat_id, photo_url, caption=None)
    return Response(
        'Telegram Bot is running! \n\n',
        mimetype='text/plain'
    ), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Проверка авторизации через токен в заголовке
        auth_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if auth_header != os.getenv('WEBHOOK_SECRET', ''):
            print(f"Unauthorized access attempt: {auth_header}")
            return Response('Unauthorized', status=401)

        # Получаем данные от Telegram
        data = request.get_json()
        if not data:
            return Response('No data', status=400)

        # Проверяем наличие сообщения
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']

            # Проверяем, есть ли текст в сообщении
            if 'text' in message:
                user_text = message['text']
                user_name = message['from'].get('first_name', 'Пользователь')

                # Создаем ответное сообщение
                response_text = (
                    f"Привет, {user_name}! 🤖\n\n"
                    f"Ты написал: <b>{user_text}</b>\n\n",
                    data

                )

                # Отправляем сообщение
                result = send_message(chat_id, response_text)
                if result and result.get('ok'):
                    print(f"Message sent to {chat_id}")
                else:
                    print(f"Failed to send message: {result}")

        return Response('ok', status=200, mimetype='text/plain')

    except Exception as e:
        print(f"Error in webhook: {e}")
        return Response('Error', status=500)


@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука с секретом"""
    try:
        # Генерируем случайный секрет
        import secrets
        secret_token = secrets.token_urlsafe(32)
        os.environ['WEBHOOK_SECRET'] = secret_token

        # URL для вебхука
        host = request.headers.get('Host')
        if not host:
            host = os.getenv('VERCEL_URL', 'your-vercel-project.vercel.app')

        webhook_url = f"https://{host}/webhook"

        # Удаляем предыдущий вебхук
        delete_response = requests.get(
            f"{BASE_URL}/deleteWebhook",
            timeout=10
        )

        # Устанавливаем новый вебхук с секретом
        set_response = requests.post(
            f"{BASE_URL}/setWebhook",
            json={
                'url': webhook_url,
                'secret_token': secret_token,
                'allowed_updates': ['message']
            },
            timeout=10
        )

        return Response(
            json.dumps({
                'status': 'success',
                'webhook_url': webhook_url,
                'secret_token': secret_token,
                'delete_response': delete_response.json() if delete_response.status_code == 200 else None,
                'set_response': set_response.json() if set_response.status_code == 200 else None
            }, indent=2),
            mimetype='application/json'
        ), 200

    except Exception as e:
        print(f"Error setting webhook: {e}")
        return Response(
            json.dumps({'status': 'error', 'message': str(e)}),
            mimetype='application/json'
        ), 500


@app.route('/info', methods=['GET'])
def info():
    """Информация о боте"""
    return Response(
        json.dumps({
            'bot': 'Telegram Echo Bot',
            'status': 'active',
            'deployment': 'Vercel',
            'endpoints': {
                'webhook': '/webhook',
                'set_webhook': '/set_webhook',
                'info': '/info'
            },
            'host': request.headers.get('Host'),
            'vercel_url': os.getenv('VERCEL_URL')
        }, indent=2),
        mimetype='application/json'
    ), 200


# Для Vercel - экспорт приложения
app_instance = app

# Для локального тестирования
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)