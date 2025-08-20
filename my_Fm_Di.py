from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ContextTypes
from datetime import datetime
import logging
import ssl

# Настройки
TOKEN = "6082546372:AAHM33fkvArJpe8wU5IQeg0L4jOGNpHJe2Q"
WEBHOOK_URL = "https://yourdomain.com/webhook"  # Ваш публичный HTTPS-адрес
PORT = 8443
CERT_PATH = "/path/to/cert.pem"  # Путь к SSL-сертификату

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("День недели", callback_data='day'),
         InlineKeyboardButton("Год", callback_data='year')]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне свое имя")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(
        f"User info: id={user.id}, first_name={user.first_name}, last_name={user.last_name}")
    await update.message.reply_text(f"Привет, {update.message.text}!",
                                    reply_markup=get_keyboard())


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current = datetime.now()
    if query.data == 'day':
        await query.edit_message_text(
            text=f"Сегодня {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][current.weekday()]}")
    elif query.data == 'year':
        await query.edit_message_text(text=f"Сейчас {current.year} год")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")


def main():
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_error_handler(error_handler)

    # Настройка Webhook
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(CERT_PATH)

    logger.info("Starting webhook...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL,
        ssl_context=context
    )


if __name__ == '__main__':
    main()