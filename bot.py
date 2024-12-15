import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from yookassa import Configuration, Payment
from flask import Flask, request, jsonify

# Загрузка переменных окружения
load_dotenv()

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://telegram-bot-2h7v.onrender.com')
PORT = int(os.getenv('PORT', 443))
CHANNEL_INVITE_LINK = os.getenv('CHANNEL_INVITE_LINK')
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
SUPPORT_CHAT_URL = os.getenv('SUPPORT_CHAT_URL', 'https://t.me/manemanvelovna')

# Проверка обязательных переменных
if not all([TELEGRAM_BOT_TOKEN, WEBHOOK_URL, YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY]):
    logger.error("Отсутствуют обязательные переменные окружения!")
    exit(1)

# Настройка ЮKассы
Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

# Flask приложение
app = Flask(__name__)

@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    data = request.json
    logger.info(f"Получены данные вебхука: {data}")

    if data.get('event') == 'payment.succeeded':
        user_id = data['object']['metadata'].get('user_id')
        if user_id:
            application.create_task(send_access_link(user_id))
            return jsonify({'status': 'success'}), 200
    logger.error("Некорректные данные вебхука или отсутствует user_id")
    return jsonify({'status': 'error'}), 400

# Отправка ссылки доступа
async def send_access_link(user_id):
    invite_message = (
        f"Поздравляем! Оплата прошла успешно.\n"
        f"Вот ваша приватная ссылка на канал: {CHANNEL_INVITE_LINK}"
    )
    await application.bot.send_message(chat_id=user_id, text=invite_message)

# Генерация ссылки на оплату
def generate_payment_link(user_id):
    try:
        payment = Payment.create({
            "amount": {"value": "2990.00", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": f"{WEBHOOK_URL}/payment-webhook"
            },
            "capture": True,
            "description": "Оплата подписки",
            "metadata": {"user_id": str(user_id)}
        })
        payment_link = payment.confirmation.confirmation_url
        logger.info(f"Создана ссылка на оплату: {payment_link}")
        return payment_link
    except Exception as e:
        logger.error(f"Ошибка при создании ссылки на оплату: {e}")
        return None

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["Оплатить Доступ", "Подробнее о канале", "Задать вопрос"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_text = (
        "Приветствую тебя✨\n"
        "Это ваш бот, здесь вы можете оформить подписку на обучающий канал.\n\n"
        "Покупка канала происходит единоразово и навсегда♥️"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_choice = update.message.text

    if user_choice == "Оплатить Доступ":
        payment_link = generate_payment_link(update.message.chat_id)
        if payment_link:
            await update.message.reply_text(
                f"🎉 Для оформления подписки нажмите на ссылку для оплаты:\n\n"
                f"💳 **Цена:** 2990₽\n"
                f"📅 **Продолжительность:** Навсегда\n\n"
                f"[🔗 Оплатить Доступ]({payment_link})",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "Произошла ошибка при создании ссылки на оплату. Попробуйте позже."
            )

    elif user_choice == "Подробнее о канале":
        channel_info_text = (
            "📚 **Информация о канале:**\n"
            "🎥 Узнайте все фишки ведения канала:\n\n"
            "💡 **Основные темы:**\n"
            "• Оформление аккаунта\n"
            "• Локации для съёмок\n"
            "• Разборы видео Reels\n"
            "• Настройки камеры телефона\n"
            "• Лайфхаки по видео\n\n"
            "🔥 **Информация будет пополняться всегда!**"
        )
        await update.message.reply_text(channel_info_text, parse_mode="Markdown")

    elif user_choice == "Задать вопрос":
        button = InlineKeyboardButton("Перейти в чат", url=SUPPORT_CHAT_URL)
        inline_reply_markup = InlineKeyboardMarkup([[button]])
        await update.message.reply_text(
            "Нажмите на кнопку ниже, чтобы перейти в чат с администратором:",
            reply_markup=inline_reply_markup
        )

# Основная функция
if __name__ == '__main__':
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск Flask через Waitress
    from waitress import serve
    serve(app, host="0.0.0.0", port=PORT)
