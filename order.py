"""
Модуль с описанием модели заказа и параметрами стэйтмашины
содержит метод фабрику для создания стэйтмашин
"""

from transitions import Machine
from utils import get_respond_mapper

TRANSITIONS = [
    {'trigger': 'start', 'source': 'initial', 'dest': 'size_selection'},
    {'trigger': 'select_size', 'source': 'size_selection', 'dest': 'payment_selection',
        'conditions': "validators.validate_size", 'before': 'set_size'},
    {'trigger': 'select_payment', 'source': 'payment_selection', 'dest': 'confirm',
        'conditions': "validators.validate_payment", 'before': 'set_payment'},
    {'trigger': 'apply', 'source': 'confirm', 'dest': 'end', 'before': 'confirm'},
    {'trigger': 'abort', 'source': 'confirm', 'dest': 'size_selection', 'before': 'reset'},
]

STATES = [
    {'name': 'initial', },
    {'name': 'size_selection', 'on_enter_message': 'Какую вы хотите пиццу?  Большую или маленькую?'},
    {'name': 'payment_selection', 'on_enter_message': 'Как вы будете платить?'},
    {'name': 'confirm',
        'on_enter_message': lambda order: f'Подтверждаете заказ: {order.size} пицца, оплата {order.payment}?'},
    {'name': 'end', 'on_enter_message': 'Спасибо за заказ'}
]


class Order(object):
    def __init__(self):
        self.size = None
        self.payment = None

    def set_size(self, size):
        self.size = size

    def set_payment(self, payment):
        self.payment = payment

    def reset(self):
        self.size = None
        self.payment = None

    def confirm(self):
        # отправка заказа куданибудь на сервер
        print(f'Новый заказ {self.size} пицца, оплата {self.payment}')


def get_order_state_machine(responder):
    """Фабрика стэйт машин для чатов

    Принимает:
    responder -- функция ответа в текущий чат
    """
    order = Order()
    mapper = get_respond_mapper(responder, order)
    states = list(map(mapper, STATES))
    machine = Machine(order, states=states, transitions=TRANSITIONS, initial='initial', auto_transitions=False)
    return machine
