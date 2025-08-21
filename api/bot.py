import os
import json
import requests
from flask import Flask, request, Response

# Настройка переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is required")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
IMAGE_URL = "https://4pda.to/s/PXticcA7C2YgYaRJl9z1jCUxDne0Bcrj7uxw.png"

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
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
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


def delete_webhook():
    """Удаление вебхука"""
    try:
        response = requests.get(f"{BASE_URL}/deleteWebhook", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error deleting webhook: {e}")
        return None


def set_webhook():
    """Установка вебхука без секретного токена"""
    try:
        # Определяем URL для вебхука
        vercel_url = os.getenv('VERCEL_URL')
        if vercel_url:
            webhook_url = f"https://{vercel_url}/api/webhook"
        else:
            # Если VERCEL_URL не установлен, используем заглушку
            webhook_url = "https://my-fm-di-bot.vercel.app/api/webhook"

        print(f"Setting webhook to: {webhook_url}")

        # Устанавливаем вебхук БЕЗ секретного токена
        response = requests.post(
            f"{BASE_URL}/setWebhook",
            json={
                'url': webhook_url,
                'allowed_updates': ['message', 'callback_query'],
                'drop_pending_updates': True
            },
            timeout=15
        )

        result = response.json()
        if result.get('ok'):
            print("Webhook set successfully")
        else:
            print(f"Webhook setting failed: {result}")

        return result

    except Exception as e:
        print(f"Error setting webhook: {e}")
        return {'ok': False, 'error': str(e)}


def get_webhook_info():
    """Получение информации о текущем вебхуке"""
    try:
        response = requests.get(f"{BASE_URL}/getWebhookInfo", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting webhook info: {e}")
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
        'Telegram Bot is running! 🤖\n\n'
        'Endpoints:\n'
        '- /api/set_webhook - Setup webhook\n'
        '- /api/webhook_info - Get webhook info\n'
        '- /api/webhook - Telegram webhook endpoint',
        mimetype='text/plain'
    ), 200


@app.route('/api/webhook', methods=['POST'])
def webhook_handler():
    """Основной обработчик вебхука от Telegram"""
    try:
        # Без проверки секретного токена - принимаем все запросы
        print("Webhook request received")

        # Получаем данные от Telegram
        data = request.get_json()
        if not data:
            print("No data received")
            return Response('No data', status=400)

        print(
            f"Received update: {json.dumps(data, indent=2, ensure_ascii=False)}")

        # Обработка сообщений
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            user_name = message['from'].get('first_name', 'Пользователь')

            if 'text' in message and message['text'] == '/start':
                caption = (
                    f"Добро пожаловать, {user_name}! 👋\n\n"
                    f"Этот бот демонстрирует интерактивное взаимодействие "
                    f"с помощью inline-кнопок и callback-запросов."
                )
                reply_markup = get_main_menu_keyboard()
                send_photo(chat_id, IMAGE_URL, caption, reply_markup)
                print(f"Sent welcome message to {chat_id}")

        # Обработка callback-запросов
        elif 'callback_query' in data:
            callback_query = data['callback_query']
            chat_id = callback_query['message']['chat']['id']
            callback_data = callback_query['data']
            user_name = callback_query['from'].get('first_name', 'Пользователь')

            # Ответ на callback query
            try:
                requests.post(
                    f"{BASE_URL}/answerCallbackQuery",
                    json={'callback_query_id': callback_query['id']},
                    timeout=5
                )
            except Exception as e:
                print(f"Error answering callback: {e}")

            # Обработка различных callback данных
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
                print(f"Sent more info to {chat_id}")

            elif callback_data == 'start_action':
                numbers_text = (
                    f"🔢 <b>Выберите число</b>\n\n"
                    f"Нажмите на одну из шести кнопок ниже, "
                    f"чтобы выбрать интересующий вас вариант."
                )
                reply_markup = get_number_buttons_keyboard()
                send_message(chat_id, numbers_text, reply_markup)
                print(f"Sent number selection to {chat_id}")

            elif callback_data.startswith('number_'):
                number = callback_data.split('_')[1]
                response_text = (
                    f"✅ Вы выбрали число: <b>{number}</b>\n\n"
                    f"Это демонстрация обработки нажатий на кнопки. "
                    f"В реальном приложении здесь могла бы быть "
                    f"любая логика в зависимости от выбора пользователя."
                )
                send_message(chat_id, response_text)
                print(f"Sent number response to {chat_id}")

        return Response('ok', status=200, mimetype='text/plain')

    except Exception as e:
        print(f"Error in webhook handler: {e}")
        return Response('Server Error', status=500)


@app.route('/api/set_webhook', methods=['GET', 'POST'])
def setup_webhook():
    """Установка вебхука без секретного токена"""
    try:
        # Сначала удаляем старый вебхук
        delete_result = delete_webhook()
        print(f"Delete webhook result: {delete_result}")

        # Устанавливаем новый вебхук БЕЗ секретного токена
        set_result = set_webhook()

        if set_result and set_result.get('ok'):
            webhook_info = get_webhook_info()
            return Response(
                json.dumps({
                    'status': 'success',
                    'message': 'Webhook установлен успешно (без секретного токена)',
                    'set_result': set_result,
                    'webhook_info': webhook_info,
                    'note': 'Секретный токен отключен - все запросы принимаются'
                }, indent=2, ensure_ascii=False),
                mimetype='application/json'
            ), 200
        else:
            return Response(
                json.dumps({
                    'status': 'error',
                    'message': 'Не удалось установить вебхук',
                    'details': set_result
                }, indent=2),
                mimetype='application/json'
            ), 500

    except Exception as e:
        print(f"Error in setup_webhook: {e}")
        return Response(
            json.dumps({
                'status': 'error',
                'message': str(e)
            }),
            mimetype='application/json'
        ), 500


@app.route('/api/webhook_info', methods=['GET'])
def webhook_info():
    """Получение информации о вебхуке"""
    try:
        info = get_webhook_info()

        response_data = {
            'webhook_info': info,
            'status': 'success',
            'note': 'Секретный токен отключен'
        }

        return Response(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            mimetype='application/json'
        ), 200

    except Exception as e:
        return Response(
            json.dumps({'status': 'error', 'message': str(e)}),
            mimetype='application/json'
        ), 500


@app.route('/api/delete_webhook', methods=['GET'])
def delete_webhook_route():
    """Удаление вебхука"""
    try:
        result = delete_webhook()
        return Response(
            json.dumps({
                'status': 'success',
                'message': 'Webhook удален',
                'result': result
            }, indent=2),
            mimetype='application/json'
        ), 200
    except Exception as e:
        return Response(
            json.dumps({'status': 'error', 'message': str(e)}),
            mimetype='application/json'
        ), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Статус бота"""
    return Response(
        json.dumps({
            'status': 'active',
            'bot_token_set': bool(TOKEN),
            'webhook_secret': 'disabled',
            'endpoints': {
                'webhook': '/api/webhook',
                'set_webhook': '/api/set_webhook',
                'webhook_info': '/api/webhook_info',
                'delete_webhook': '/api/delete_webhook',
                'status': '/api/status'
            }
        }, indent=2),
        mimetype='application/json'
    ), 200


# Обработчик для favicon.ico
@app.route('/favicon.ico')
def favicon():
    return Response('', status=204)


# Экспорт для Vercel
app_instance = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    print("Webhook secret: DISABLED")
    app.run(debug=True, host='0.0.0.0', port=port)