import os
import requests
import json
from flask import Flask, request, Response

# Настройка переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is required")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
photo_url = "https://4pda.to/s/PXticcA7C2YgYaRJl9z1jCUxDne0Bcrj7uxw.png"

app = Flask(__name__)


def send_message(chat_id, text):
    """Простая отправка сообщения"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None


def send_photo(chat_id, photo_url, caption=None, reply_markup=None):
    """Отправка фото через Telegram API"""
    url = f"{BASE_URL}/sendPhoto"
    payload = {
        'chat_id': chat_id,
        'photo': photo_url
    }
    if caption:
        payload['caption'] = caption
        payload['parse_mode'] = 'HTML'
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error sending photo: {e}")
        return None


def get_main_menu_keyboard():
    """Клавиатура с двумя кнопками"""
    return {
        'inline_keyboard': [
            [
                {'text': 'Начать', 'callback_data': 'start_action'},
                {'text': 'Подробнее', 'callback_data': 'more_info'}
            ]
        ]
    }


@app.route('/app/bot', methods=['POST'])
def webhook():
    """Обработчик вебхука - простой эхо-бот"""
    try:
        # Получаем данные от Telegram
        data = request.get_json()
        print(f"Received data: {data}")

        if not data:
            return Response('No data', status=400)

        # Обработка сообщений
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')

            if text == '/start':
                user_name = message['from'].get('first_name', 'Пользователь')
                send_message(chat_id,
                             f"Привет {user_name}! Я помогу скачать вам весь архив mp3 файлов всех каналов, всех сайтов холдинга DI.FM\n\n"
                             f"Нажмите «Подробнее», если хотите узнать, для чего все это. Нажмите «Начать», если уже знаете.")
                send_photo(chat_id, photo_url)
                reply_markup = get_main_menu_keyboard()

            elif text:
                send_message(chat_id, f"Вы сказали: {text}")

        return Response('ok', status=200)

    except Exception as e:
        print(f"Error: {e}")
        return Response('Error', status=500)


@app.route('/app/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука"""
    try:
        # Получаем URL вебхука
        # vercel_url = os.getenv('VERCEL_URL', 'my-fm-di-bot.vercel.app')
        # webhook_url = f"https://{vercel_url}/app/bot"
        webhook_url = f"https://my-fm-di-bot.vercel.app/app/bot"

        print(f"Setting webhook to: {webhook_url}")

        # Устанавливаем вебхук
        response = requests.post(
            f"{BASE_URL}/setWebhook",
            json={
                'url': webhook_url,
                'allowed_updates': ['message']
            },
            timeout=15
        )

        result = response.json()
        print(f"Webhook result: {result}")

        if result.get('ok'):
            return Response(f"Webhook установлен: {webhook_url}", status=200)
        else:
            return Response(f"Ошибка: {result}", status=500)

    except Exception as e:
        return Response(f"Error: {e}", status=500)


@app.route('/app/delete_webhook', methods=['GET'])
def delete_webhook():
    """Удаление вебхука"""
    try:
        response = requests.get(f"{BASE_URL}/deleteWebhook", timeout=10)
        result = response.json()
        return Response(f"Webhook удален: {result}", status=200)
    except Exception as e:
        return Response(f"Error: {e}", status=500)


@app.route('/')
def index():
    return "Telegram Echo Bot is running! Use /app/set_webhook to setup"


# Для Vercel
app_instance = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)