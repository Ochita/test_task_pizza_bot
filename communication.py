"""
Модуль обработки сообщений.
"""

from utils import processed_message
from fuzzywuzzy import process
from order import get_order_state_machine
from validators import PAYMENT_OPTIONS, SIZE_OPTIONS


orders = dict()

dictionary = PAYMENT_OPTIONS + SIZE_OPTIONS


@processed_message
def parse_dictionary_option(message):
    """Выбор подходящей опции на основе расстояние Левенштейна от
    обработаного сообщения на случай опечаток.

    Принимает:
    message -- сообщение из одного слова без окончания
    """
    option, score = process.extractOne(message, dictionary)
    if score > 69:
        return option


@processed_message
def parse_yes_no_option(message):
    """Обработка ответов да\нет

    Принимает:
    message -- сообщение из одного слова
    """
    if message == 'да':
        return True
    elif message == 'нет':
        return False


def start_order(session_id, responder):
    """Обработчик начала процесса заказа.
    Создает стэйт машину, сохраняет в хранилище сессий,
    запускает диалог.

    Принимает:
    session_id -- ид чата
    responder -- функция ответа в этот чат
    """
    orders[session_id] = get_order_state_machine(responder)
    orders[session_id].model.start()


def handle_message(session_id, message, responder):
    """Текстовых сообщений.
    Вызывает триггеры стэйт машины.

    Принимает:
    session_id -- ид чата
    message -- пришедшее сообщение
    responder -- функция ответа в этот чат
    """
    machine = orders.get(session_id)
    was_deleted = False
    if machine:
        order = machine.model
        triggers = machine.get_triggers(order.state)
        re_ask = False
        if len(triggers) == 1:  # однозначный переход, парсим опцию
            trigger = getattr(order, triggers[0])
            option = parse_dictionary_option(message)
            triggered = trigger(option)
            if not option or not triggered:
                re_ask = True  # переспрашиваем если опция не найдена или триггер не отработал
        elif len(triggers) == 2:  # выбор, парсим да\нет
            option = parse_yes_no_option(message)
            if option is None:
                re_ask = True  # переспрашиваем если ни да ни нет не определено
            elif option:
                getattr(order, triggers[0])()  # да ведет по первой ветке
            else:
                getattr(order, triggers[1])()
        else:  # если нет переходов ордер дошел до конца, можно удалять.
            del orders[session_id]
            was_deleted = True
        if re_ask:
            responder('Я вас не понял. Попробуйте ответить еще раз.')
    if machine is None or was_deleted:
        responder('Что бы начать заказ введите /start')

