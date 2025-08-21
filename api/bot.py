import os
import json
import requests
from flask import Flask, request, Response

# Настройка переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_BOT_TOKEN')
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
IMAGE_URL = "https://s3.twcstorage.ru/c6bae09a-a5938890-9b68-453c-9c54-76c439a70d3e/Roulette/10_000.png"

app = Flask(__name__)


def send_message(chat_id, text, reply_markup=None):
    """Отправка текстового сообщения через Telegram API"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup

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
        payload['reply_markup'] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending photo: {e}")
        return None


def get_main_menu_keyboard():
    """Клавиатура с двумя кнопками"""
    return {
        'inline_keyboard': [
            [
                {'text': 'Подробнее', 'callback_data': 'more_info'},
                {'text': 'Начать', 'callback_data': 'start_action'}
            ]
        ]
    }


def get_number_buttons_keyboard():
    """Клавиатура с 6 кнопками"""
    return {
        'inline_keyboard': [
            [
                {'text': 'Один', 'callback_data': 'number_1'},
                {'text': 'Два', 'callback_data': 'number_2'},
                {'text': 'Три', 'callback_data': 'number_3'}
            ],
            [
                {'text': 'Четыре', 'callback_data': 'number_4'},
                {'text': 'Пять', 'callback_data': 'number_5'},
                {'text': 'Шесть', 'callback_data': 'number_6'}
            ]
        ]
    }


@app.route('/')
def index():
    return Response(
        'Telegram Interactive Bot is running! 🤖\n\n'
        'Bot sends an image on start and provides interactive buttons.\n'
        'Uses callback queries for button interactions.',
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

        # Обработка входящих сообщений
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            user_name = message['from'].get('first_name', 'Пользователь')

            # Проверяем команду /start
            if 'text' in message and message['text'] == '/start':
                # Отправляем изображение с описанием и кнопками
                caption = (
                    f"Добро пожаловать, {user_name}! 👋\n\n"
                    f"Этот бот демонстрирует интерактивное взаимодействие "
                    f"с помощью inline-кнопок и callback-запросов."
                )

                reply_markup = get_main_menu_keyboard()
                send_photo(chat_id, IMAGE_URL, caption, reply_markup)

        # Обработка callback-запросов от кнопок
        elif 'callback_query' in data:
            callback_query = data['callback_query']
            chat_id = callback_query['message']['chat']['id']
            message_id = callback_query['message']['message_id']
            callback_data = callback_query['data']
            user_name = callback_query['from'].get('first_name', 'Пользователь')

            # Отправляем ответ на callback (удаляет "часики" в Telegram)
            ack_url = f"{BASE_URL}/answerCallbackQuery"
            requests.post(ack_url, json={
                'callback_query_id': callback_query['id'],
                'text': 'Обрабатываю запрос...',
                'show_alert': False
            })

            # Обработка нажатий на кнопки
            if callback_data == 'more_info':
                more_info_text = (
                    f"🔍 <b>Подробная информация</b>\n\n"
                    f"Этот бот предназначен для демонстрации возможностей "
                    f"интерактивного взаимодействия в Telegram.\n\n"
                    f"• Используются inline-кнопки для навигации\n"
                    f"• Callback-запросы для обработки нажатий\n"
                    f"• Динамическое изменение интерфейса\n"
                    f"• Отправка медиа-контента\n\n"
                    f"Бот может быть расширен для любых бизнес-задач!"
                )
                send_message(chat_id, more_info_text)

            elif callback_data == 'start_action':
                numbers_text = (
                    f"🔢 <b>Выберите число</b>\n\n"
                    f"Нажмите на одну из шести кнопок ниже, "
                    f"чтобы выбрать интересующий вас вариант."
                )
                reply_markup = get_number_buttons_keyboard()
                send_message(chat_id, numbers_text, reply_markup)

            elif callback_data.startswith('number_'):
                number = callback_data.split('_')[1]
                response_text = (
                    f"✅ Вы выбрали число: <b>{number}</b>\n\n"
                    f"Это демонстрация обработки нажатий на кнопки. "
                    f"В реальном приложении здесь могла бы быть "
                    f"любая логика в зависимости от выбора пользователя."
                )
                send_message(chat_id, response_text)

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
                'allowed_updates': ['message', 'callback_query']
            },
            timeout=10
        )

        return Response(
            json.dumps({
                'status': 'success',
                'webhook_url': webhook_url,
                'secret_token': 'HIDDEN_FOR_SECURITY',
                'image_url': IMAGE_URL,
                'allowed_updates': ['message', 'callback_query'],
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
            'bot': 'Telegram Interactive Bot',
            'status': 'active',
            'features': [
                'Image sending on start',
                'Inline keyboard buttons',
                'Callback query processing',
                'Interactive menu system',
                'Dynamic UI changes'
            ],
            'image_url': IMAGE_URL,
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