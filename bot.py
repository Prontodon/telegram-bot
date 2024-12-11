import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yookassa import Configuration, Payment
import urllib.parse  # Для кодирования текста в URL
import logging

# Логирование
logging.basicConfig(level=logging.INFO)

# ЮKassa Данные
Configuration.account_id = "496344"  # SHOP_ID
Configuration.secret_key = "live_v8fKRfAp1mE3Y0mCTPE-a0L8p3SnvA2XoxtUUAsdyk8"  # SECRET_KEY
CHANNEL_INVITE_LINK = "https://t.me/+m01bmpeUanVlYWMy"  # Ссылка на приватный канал

# Настройка Google Sheets
def setup_google_sheets():
    credentials_file = "C:\\Users\\ASUS TUF\\Downloads\\bot-blog-443504-d3b23e48879c.json"  # Путь к JSON-файлу
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open("date of bot")
    return spreadsheet.sheet1

def log_to_google_sheets(user_id, username, action):
    sheet = setup_google_sheets()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sheet.append_row([user_id, username, action, timestamp])

# Создание ссылки на оплату
def create_payment_link(user_id):
    try:
        payment = Payment.create({
            "amount": {
                "value": "2990.00",  # Цена подписки
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://your-server.com/payment-success/{user_id}"
            },
            "capture": True,
            "description": f"Оплата подписки пользователем {user_id}",
        })

        return payment.confirmation["confirmation_url"]
    except Exception as e:
        logging.error(f"Ошибка при создании платежа: {e}")
        raise

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id
    username = update.message.chat.username
    log_to_google_sheets(user_id, username, "Запустил /start")

    keyboard = [["Оплатить Доступ", "Подробнее о канале", "Задать вопрос"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_text = (
        "Приветствую тебя✨\n"
        "Это marryyme_bot, здесь ты можешь оформить подписку на обучающий канал от @marryyme.me «Твой путь в блогинг».\n\n"
        "Покупка канала происходит единоразово и навсегда♥️"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_choice = update.message.text
    user_id = update.message.chat_id
    username = update.message.chat.username

    keyboard = [["Оплатить Доступ", "Подробнее о канале", "Задать вопрос"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if user_choice == "Оплатить Доступ":
        log_to_google_sheets(user_id, username, "Нажал 'Оплатить Доступ'")

        try:
            # Создание ссылки на оплату
            payment_link = create_payment_link(user_id)

            # Отправка сообщения с платёжной ссылкой
            await update.message.reply_text(
                f"🎉 Для оформления подписки на обучающий канал нажмите на ссылку для оплаты:\n\n"
                f"💳 **Цена:** 2990₽\n"
                f"📅 **Продолжительность:** Навсегда\n\n"
                f"[🔗 Оплатить Доступ]({payment_link})",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            await update.message.reply_text(
                "Произошла ошибка при создании ссылки на оплату. Попробуйте снова или обратитесь в поддержку.",
                reply_markup=reply_markup
            )

    elif user_choice == "Подробнее о канале":
        log_to_google_sheets(user_id, username, "Нажал 'Подробнее о канале'")

        # Подробное описание канала
        channel_info_text = (
            "📚 **Информация о канале:**\n\n"
            "🎥 Изучив гайд, вы узнаете все фишки и тонкости ведения Instagram. "
            "Я помогу вам пройти непростой путь в мир блогинга:\n\n"
            "💡 **Основные темы:**\n"
            "• Оформление аккаунта от А до Я\n"
            "• Где находить локации для съёмки\n"
            "• Какие приложения помогают подобрать образ\n"
            "• Разборы видео Reels, как попасть в топ\n"
            "• Алгоритмы Instagram\n"
            "• Настройка камеры на телефоне\n"
            "• Еженедельные вопрос-ответы\n"
            "• Детальные разборы ваших аккаунтов\n"
            "• Как создавать красивые видео в Stories и Reels\n"
            "• Лайфхаки по видео и озвучке\n\n"
            "🔥 **Информация в гайде будет пополняться всегда!**\n"
            "Ваша Мери ❤️"
        )

        await update.message.reply_text(channel_info_text, parse_mode="Markdown", reply_markup=reply_markup)

    elif user_choice == "Задать вопрос":
        log_to_google_sheets(user_id, username, "Нажал 'Задать вопрос'")
        button = InlineKeyboardButton("Перейти в чат", url="https://t.me/manemanvelovna")
        inline_reply_markup = InlineKeyboardMarkup([[button]])
        await update.message.reply_text(
            "Нажмите на кнопку ниже, чтобы перейти в чат с администратором:",
            reply_markup=inline_reply_markup
        )

# Основная функция
def main():
    application = Application.builder().token("8072320649:AAG2Rd2QKCKesruNF4-PwmqtV9PRVQBQ84s").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(timeout=10, read_timeout=10)

if __name__ == '__main__':
    main()
