import json
import http.client
import urllib.parse
import os


class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = "api.telegram.org"

    def make_request(self, method, params=None):
        """Выполняет запрос к API Telegram"""
        conn = http.client.HTTPSConnection(self.base_url)
        url = f"/bot{self.token}/{method}"

        if params:
            params = urllib.parse.urlencode(params)
            url = f"{url}?{params}"

        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()

        return json.loads(data)

    def set_webhook(self, url):
        """Устанавливает webhook"""
        params = {'url': url}
        return self.make_request('setWebhook', params)

    def delete_webhook(self):
        """Удаляет webhook"""
        return self.make_request('deleteWebhook')

    def send_message(self, chat_id, text, reply_markup=None):
        """Отправляет сообщение"""
        params = {
            'chat_id': chat_id,
            'text': text
        }

        if reply_markup:
            params['reply_markup'] = json.dumps(reply_markup)

        return self.make_request('sendMessage', params)

    def create_inline_keyboard(self):
        """Создает клавиатуру с кнопкой для перехода на сайт"""
        return {
            'inline_keyboard': [[
                {
                    'text': 'Перейти на GitHub',
                    'url': 'https://github.com'
                }
            ]]
        }

    def handle_update(self, update):
        """Обрабатывает входящее обновление"""
        try:
            if 'message' in update and 'text' in update['message']:
                chat_id = update['message']['chat']['id']
                text = update['message']['text']

                # Отправляем эхо-сообщение
                self.send_message(chat_id, f"Вы сказали: {text}")

                # Отправляем сообщение с кнопкой
                keyboard = self.create_inline_keyboard()
                self.send_message(
                    chat_id,
                    "Нажмите кнопку ниже, чтобы перейти на GitHub:",
                    keyboard
                )

                return {'status': 'success'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

        return {'status': 'no_message'}


# Глобальная инициализация бота
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = TelegramBot(BOT_TOKEN)


def handler(request):
    """Обработчик для Vercel Serverless Function"""
    if request.method == 'POST':
        try:
            # Парсим входящее обновление
            update = json.loads(request.body)

            # Обрабатываем обновление
            result = bot.handle_update(update)

            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

    elif request.method == 'GET':
        # Для настройки webhook или проверки работы
        action = request.query.get('action')

        if action == 'set_webhook':
            # Получаем URL вебхука
            webhook_url = f"https://{request.headers.get('host')}/api/bot"
            result = bot.set_webhook(webhook_url)
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

        elif action == 'delete_webhook':
            result = bot.delete_webhook()
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

        elif action == 'info':
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'Bot is running'})
            }

    return {
        'statusCode': 405,
        'body': json.dumps({'error': 'Method not allowed'})
    }