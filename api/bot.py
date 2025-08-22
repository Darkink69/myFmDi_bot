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


def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения с возможностью добавления клавиатуры"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)

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


def answer_callback_query(callback_query_id):
    """Ответ на callback query"""
    try:
        url = f"{BASE_URL}/answerCallbackQuery"
        payload = {
            'callback_query_id': callback_query_id
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error answering callback: {e}")


def get_main_menu_keyboard():

    return {
        'inline_keyboard': [
            [
                {'text': 'Подробнее', 'callback_data': 'more_info'},
                {'text': 'Начать', 'callback_data': 'start_action'}
            ]
        ]
    }


def get_radio_keyboard():
    """Клавиатура с 6 кнопками радиостанций"""
    return {
        'inline_keyboard': [
            [
                {'text': 'DI', 'callback_data': 'radio_di'},
                {'text': 'Rockradio', 'callback_data': 'radio_rockradio'}
            ],
            [
                {'text': 'Radiotunes', 'callback_data': 'radio_radiotunes'},
                {'text': 'Jazzradio', 'callback_data': 'radio_jazzradio'}
            ],
            [
                {'text': 'Classicalradio',
                 'callback_data': 'radio_classicalradio'},
                {'text': 'Zenradio', 'callback_data': 'radio_zenradio'}
            ]
        ]
    }


@app.route('/app/bot', methods=['POST'])
def webhook():
    """Обработчик вебхука"""
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
                caption = (
                    f"Привет {user_name}! 👋\n\n"
                    f"Я помогу скачать вам весь архив mp3 файлов всех каналов, всех сайтов холдинга DI.FM\n\n"
                    f"Нажмите «Подробнее», если хотите узнать, для чего все это. Нажмите «Начать», если уже знаете."
                )
                reply_markup = get_main_menu_keyboard()
                send_photo(chat_id, photo_url, caption, reply_markup)

        # Обработка callback-запросов от кнопок
        elif 'callback_query' in data:
            callback_query = data['callback_query']
            chat_id = callback_query['message']['chat']['id']
            callback_data = callback_query['data']
            callback_query_id = callback_query['id']

            # Отвечаем на callback query
            answer_callback_query(callback_query_id)

            # Обработка нажатий на кнопки
            if callback_data == 'more_info':
                # Текст с разными шрифтами
                more_info_text = (
                    "<b>🎵 Детальная информация</b>\n\n"
                    "<i>Этот бот создан для настоящих ценителей музыки!</i>\n\n"
                    "<code>• Скачивайте архивы mp3 файлов</code>\n"
                    "<pre>• Все каналы DI.FM холдинга</pre>\n"
                    "<b>• Высокое качество звука</b>\n"
                    "<i>• Регулярные обновления баз</i>\n\n"
                    "<u>Возможности:</u>\n"
                    "✓ DI.FM\n"
                    "✓ RockRadio.com\n"
                    "✓ RadioTunes.com\n"
                    "✓ JazzRadio.com\n"
                    "✓ ClassicalRadio.com\n"
                    "✓ ZenRadio.com\n\n"
                    "<b>Наслаждайтесь музыкой без ограничений! 🎶</b>"
                )
                send_photo(chat_id, photo_url, more_info_text)

            elif callback_data == 'start_action':
                start_text = (
                    "🎧 <b>Выберите радиостанцию:</b>\n\n"
                    "Нажмите на одну из кнопок ниже, чтобы выбрать интересующую вас радиостанцию и получить доступ к архиву mp3 файлов."
                )
                reply_markup = get_radio_keyboard()
                send_message(chat_id, start_text, reply_markup)

            # Обработка выбора радиостанций
            elif callback_data == 'radio_di':
                send_message(chat_id,
                             "Вы выбрали: <b>DI</b>\n\nСкачивание архива начато...")

            elif callback_data == 'radio_rockradio':
                send_message(chat_id,
                             "Вы выбрали: <b>Rockradio</b>\n\nСкачивание архива начато...")

            elif callback_data == 'radio_radiotunes':
                send_message(chat_id,
                             "Вы выбрали: <b>Radiotunes</b>\n\nСкачивание архива начато...")

            elif callback_data == 'radio_jazzradio':
                send_message(chat_id,
                             "Вы выбрали: <b>Jazzradio</b>\n\nСкачивание архива начато...")

            elif callback_data == 'radio_classicalradio':
                send_message(chat_id,
                             "Вы выбрали: <b>Classicalradio</b>\n\nСкачивание архива начато...")

            elif callback_data == 'radio_zenradio':
                send_message(chat_id,
                             "Вы выбрали: <b>Zenradio</b>\n\nСкачивание архива начато...")

        return Response('ok', status=200)

    except Exception as e:
        print(f"Error: {e}")
        return Response('Error', status=500)


@app.route('/app/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука"""
    try:
        webhook_url = f"https://my-fm-di-bot.vercel.app/app/bot"
        print(f"Setting webhook to: {webhook_url}")

        # Устанавливаем вебхук с поддержкой callback queries
        response = requests.post(
            f"{BASE_URL}/setWebhook",
            json={
                'url': webhook_url,
                'allowed_updates': ['message', 'callback_query']
                # Добавляем поддержку callback
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
    return "Telegram Radio Bot is running! Use /app/set_webhook to setup"


# Для Vercel
app_instance = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)