"""
Модуль с валидаторами входящих данных
и константами возможных значений для опций
"""


PAYMENT_OPTIONS = ('наличными', 'картой')
SIZE_OPTIONS = ('большая', 'маленькая')


def validate_size(size):
    return size in SIZE_OPTIONS


def validate_payment(payment):
    return payment in PAYMENT_OPTIONS
