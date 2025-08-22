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

            # Обработка callback-запросов от кнопок
            elif 'callback_query' in data:
                callback_query = data['callback_query']
                chat_id = callback_query['message']['chat']['id']
                message_id = callback_query['message']['message_id']
                callback_data = callback_query['data']
                user_name = callback_query['from'].get('first_name',
                                                       'Пользователь')

            # Отправляем ответ на callback (удаляет "часики" в Telegram)
            # ack_url = f"{BASE_URL}/answerCallbackQuery"
            # requests.post(ack_url, json={
            #     'callback_query_id': callback_query['id'],
            #     'text': 'Обрабатываю запрос...',
            #     'show_alert': False
            # })

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