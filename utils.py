"""
Модуль со вспомогательными функциями
"""

import string


def get_respond_mapper(responder, order):
    """Фабрика функций для маппинга списка стэйтов
    возвращает копию стэйта, чтоб небыло проблем с изменением
    одного и того же объекта по ссылке
    добавляет ключ on_enter с колбэком входа в стэйт
    сгенерированным на основе данных из on_enter_message
    и удаляет ключ on_enter_message что бы конструктор стэйта не падал

    Необходима что бы колбэки стэйтмашины умели писать в свой чат
    через функцию responder
    """
    def mapper(state):
        state_cp = state.copy()
        if state_cp.get('on_enter_message'):
            msg = state_cp.pop('on_enter_message')
            if callable(msg):
                state_cp['on_enter'] = lambda *args, **kwargs: responder(msg(order))
            else:
                state_cp['on_enter'] = lambda *args, **kwargs: responder(msg)
        return state_cp

    return mapper


def processed_message(func):
    """Декоратор предварительной обработки сообщения
    убирает знаки препинания, переводит в нижний регистр
    и отрезает окончание (2 символа)
    """
    def wrapper(message, *args, **kwargs):
        processed = message.translate(str.maketrans('', '', string.punctuation)).lower()
        end_cut = processed[:2] if len(processed) > 4 else processed
        return func(end_cut, *args, **kwargs)
    return wrapper
