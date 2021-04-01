import logging
import os
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters
from communication import start_order, handle_message

API_KEY = os.getenv('API_KEY')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=API_KEY, use_context=True)
dispatcher = updater.dispatcher


def get_respond_function(session_id, context):
    """Возвращает функцию ответа в текущий чат

    Принимает:
    session_id -- ид текущего чата
    context -- служебный объект библиотеки telegram в котором есть функция отправки сообщения
    """
    return lambda msg: context.bot.send_message(chat_id=session_id, text=msg)


def start(update, context):
    """Обработчик команды старт
    """
    session_id = update.effective_chat.id
    start_order(session_id, get_respond_function(session_id, context))


def text_handler(update, context):
    """Обработчик текстовых сообщений
    """
    session_id = update.effective_chat.id
    responder = get_respond_function(session_id, context)
    msg = update.message.text
    handle_message(session_id, msg, responder)


# вешаем обработчики
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
# фильтр для срабатывания хендлера только на текстовые сообщения и не являющиеся командами
text_handler = MessageHandler(Filters.text & (~Filters.command), text_handler)
dispatcher.add_handler(text_handler)

updater.start_polling()
