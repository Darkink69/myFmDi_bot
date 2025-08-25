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
photo2_url = "https://www.di.fm/assets/plans/feature_graphics/curation@2x-30d8902e54fdae9fa63694ebb591ded0f481103a5b6c652b238b4ac58b849a9b.png"

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
    """Клавиатура с кнопками"""
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
                {'text': 'DI', 'callback_data': 'di'},
                {'text': 'Rockradio', 'callback_data': 'rockradio'}
            ],
            [
                {'text': 'Radiotunes', 'callback_data': 'radiotunes'},
                {'text': 'Jazzradio', 'callback_data': 'jazzradio'}
            ],
            [
                {'text': 'Classicalradio', 'callback_data': 'classicalradio'},
                {'text': 'Zenradio', 'callback_data': 'zenradio'}
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
                    f"Я помогу скачать вам mp3-файлы всех каналов содружества DI.FM\n\n"
                    f"Нажмите «Подробнее», если хотите узнать, для чего все это. Нажмите «Начать», если уже знаете."
                )
                reply_markup = get_main_menu_keyboard()
                send_photo(chat_id, photo_url, caption, reply_markup)
                return Response('ok', status=200)

        # Обработка callback-запросов от кнопок
        if 'callback_query' in data:
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
                    "🎵 <b>Как получить все mp3</b>\n\n"
                    "<i>Мы скачаем для вас архив mp3-файлов любой радиостанции всех 6 сайтов содружества DI.FM. Всего их 431.</i>\n\n"
                    "• На каждом из сайтов холдинга Di.FM находятся десятки каналов (радиостанций).\n"
                    "• Через несколько кликов мы можете получить ссылку на скачивание всех mp3-файлов premium качества конкретного канала. "
                    "Всех файлов, которые составляют их эфир вещания.\n"
                    "• Например на портале DI.FM существует 100 каналов, среди которых есть радиостанция <b>Trance</b>. На ней, на данный момент, звучит 1275 треков. \n"
                    "• Общий размер архивов, который будет доступен по ссылке - 12.69 ГБайт\n\n"
                    "<b>Услуга платная.\nНеобходимо сделать донат в размере 49 рублей.\n</b>\n\n"
                    "<u>Что будет после оплаты?</u>\n"
                    "• После проверки факта доната ваш заказ встанет в очередь и начнется закачка файлов mp3 с серверов холдинга\n"
                    "• Все файлы в формате mp3 с битрейдом 320 кбит/с. С обложками и id3-тегами\n"
                    "• Через несколько минут вам будет доступна ссылка на Яндекс Диск\n"
                    "• Полная закачка всех файлов может занять до 6 часов. Это связано с техническими ограничениями. Но первые файлы будут доступны уже через несколько минут\n"
                    "• Дождитесь загрузки всех файлов mp3 (об этом вам придет уведомление) и скачайте все одним архивом. Но начать скачивать или слушать выборочно, по одному треку, вы можете сразу\n"
                    "• Ссылка доступна ровно 7 дней. После этого файлы, по техническим причинам, удалятся с Яндекс Диска\n"
                    "• Теперь вы можете слушать музыку где и как хотите! 🎶\n\n"
                    "<u>Подробнее о сайтах:</u>\n"
                    "✓ DI.FM\n"
                    "✓ RockRadio.com\n"
                    "✓ RadioTunes.com\n"
                    "✓ JazzRadio.com\n"
                    "✓ ClassicalRadio.com\n"
                    "✓ ZenRadio.com\n\n"
                    "<b>Наслаждайтесь музыкой без ограничений! 🎶</b>"
                )
                # Отправляем картинку с текстом и кнопками
                reply_markup = get_main_menu_keyboard()
                result = send_photo(chat_id, photo2_url, more_info_text,
                                    reply_markup)
                print(f"Photo send result: {result}")
                return Response('ok', status=200)

            elif callback_data == 'start_action':
                start_text = (
                    "🎧 <b>Первый шаг - Выберете сайт</b>\n\n"
                    "Для скачивания вам нужно пройти 3 шага. На каком портале находиться интересующая вас радиостанция?"
                )
                reply_markup = get_radio_keyboard()
                send_message(chat_id, start_text, reply_markup)
                return Response('ok', status=200)

            # Обработка выбора радиостанций через цикл
            elif callback_data in ['di', 'rockradio', 'radiotunes', 'jazzradio',
                                   'classicalradio', 'zenradio']:
                # Словарь с названиями радиостанций
                radio_names = {
                    'di': 'DI',
                    'rockradio': 'Rockradio',
                    'radiotunes': 'Radiotunes',
                    'jazzradio': 'Jazzradio',
                    'classicalradio': 'Classicalradio',
                    'zenradio': 'Zenradio'
                }

                # Получаем название радиостанции из callback_data
                radio_name = radio_names.get(callback_data, 'радиостанцию')

                send_message(chat_id,
                             f"Вы выбрали: <b>{radio_name}</b>\n\nВторой шаг - выберете интересующую вас радиостанцию:")
                return Response('ok', status=200)

        # Если не обработали другие случаи, возвращаем ok
        return Response('ok', status=200)

    except Exception as e:
        print(f"Error in webhook: {e}")
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