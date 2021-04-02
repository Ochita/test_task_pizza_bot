import unittest
from mock import Mock, patch
from order import STATES
from validators import SIZE_OPTIONS, PAYMENT_OPTIONS
from communication import parse_dictionary_option, parse_yes_no_option, start_order, handle_message
from utils import get_respond_mapper, processed_message


@processed_message
def processing_return(message, *args, **kwargs):
    return message


class OrderMock:
    def __init__(self, size, payment):
        self.size = size
        self.payment = payment


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.responder = Mock(return_value=None)

    def test_mapper_str(self):
        expected_order = OrderMock(SIZE_OPTIONS[0], PAYMENT_OPTIONS[0])
        mapper = get_respond_mapper(self.responder, expected_order)
        states = [{'name': 'test', 'on_enter_message': 'test_message'}]
        new_state = list(map(mapper, states))[0]
        self.assertEqual('test', new_state['name'])
        self.assertIsNone(new_state.get('on_enter_message'))
        new_state['on_enter']()
        self.responder.assert_called_once_with('test_message')

    def test_mapper_fun(self):
        expected_order = OrderMock(SIZE_OPTIONS[1], PAYMENT_OPTIONS[1])
        mapper = get_respond_mapper(self.responder, expected_order)
        states = [{'name': 'test', 'on_enter_message': lambda order: f'{order.size}_{order.payment}'}]
        new_state = list(map(mapper, states))[0]
        self.assertEqual('test', new_state['name'])
        self.assertIsNone(new_state.get('on_enter_message'))
        new_state['on_enter']()
        self.responder.assert_called_once_with(f'{expected_order.size}_{expected_order.payment}')

    def test_processing_short(self):
        result = processing_return('тест')
        self.assertEqual('тест', result)

    def test_processing_end(self):
        result = processing_return('тестец')
        self.assertEqual('тест', result)

    def test_processing_junk(self):
        result = processing_return('!,!тестец!.!')
        self.assertEqual('тест', result)

    def test_processing_lot_arguments(self):
        result = processing_return('!!!тестец!!!', '', None, [], test='')
        self.assertEqual('тест', result)


class TestCommunications(unittest.TestCase):
    def test_parse_option(self):  # TODO split tests
        res = parse_dictionary_option('большая')
        self.assertEqual(SIZE_OPTIONS[0], res)
        res = parse_dictionary_option('большое')
        self.assertEqual(SIZE_OPTIONS[0], res)
        res = parse_dictionary_option('большые')
        self.assertEqual(SIZE_OPTIONS[0], res)
        res = parse_dictionary_option('большн')
        self.assertEqual(SIZE_OPTIONS[0], res)
        res = parse_dictionary_option('бльшая')
        self.assertEqual(SIZE_OPTIONS[0], res)
        res = parse_dictionary_option('бальшая')
        self.assertEqual(SIZE_OPTIONS[0], res)
        res = parse_dictionary_option('БолШущая')
        self.assertEqual(SIZE_OPTIONS[0], res)

    def test_parse_yes_no(self):
        res = parse_yes_no_option('да')
        self.assertEqual(True, res)
        res = parse_yes_no_option('нет')
        self.assertEqual(False, res)
        res = parse_yes_no_option('отклаадр')
        self.assertIsNone(res)


@patch('order.Order.confirm', Mock(return_value=None))  # что бы не дергать отправку на сервер в confirm
class TestDialog(unittest.TestCase):
    def setUp(self):
        self.responder = Mock(return_value=None)
        self.session_id = 12345

    def test_dialog__big_cash_short(self):
        start_order(self.session_id, self.responder)
        expected_order = OrderMock(SIZE_OPTIONS[0], PAYMENT_OPTIONS[0])

        self.responder.assert_called_with(STATES[1]['on_enter_message'])
        handle_message(self.session_id, expected_order.size, self.responder)
        self.responder.assert_called_with(STATES[2]['on_enter_message'])
        handle_message(self.session_id, expected_order.payment, self.responder)
        msg_func = STATES[3]['on_enter_message']
        self.responder.assert_called_with(msg_func(expected_order))
        handle_message(self.session_id, 'да', self.responder)
        self.responder.assert_called_with(STATES[4]['on_enter_message'])

    def test_dialog__small_card_short(self):
        start_order(self.session_id, self.responder)
        expected_order = OrderMock(SIZE_OPTIONS[1], PAYMENT_OPTIONS[1])

        self.responder.assert_called_with(STATES[1]['on_enter_message'])
        handle_message(self.session_id, expected_order.size, self.responder)
        self.responder.assert_called_with(STATES[2]['on_enter_message'])
        handle_message(self.session_id, expected_order.payment, self.responder)
        msg_func = STATES[3]['on_enter_message']
        self.responder.assert_called_with(msg_func(expected_order))
        handle_message(self.session_id, 'да', self.responder)
        self.responder.assert_called_with(STATES[4]['on_enter_message'])

    def test_dialog__big_card_long(self):
        start_order(self.session_id, self.responder)
        expected_order = OrderMock(SIZE_OPTIONS[0], PAYMENT_OPTIONS[1])

        self.responder.assert_called_with(STATES[1]['on_enter_message'])
        handle_message(self.session_id, expected_order.size, self.responder)
        self.responder.assert_called_with(STATES[2]['on_enter_message'])
        handle_message(self.session_id, expected_order.payment, self.responder)
        msg_func = STATES[3]['on_enter_message']
        self.responder.assert_called_with(msg_func(expected_order))
        handle_message(self.session_id, 'нет', self.responder)
        self.responder.assert_called_with(STATES[1]['on_enter_message'])
        handle_message(self.session_id, expected_order.size, self.responder)
        self.responder.assert_called_with(STATES[2]['on_enter_message'])
        handle_message(self.session_id, expected_order.payment, self.responder)

    def test_dialog__small_card_re_ask(self):
        start_order(self.session_id, self.responder)
        expected_order = OrderMock(SIZE_OPTIONS[1], PAYMENT_OPTIONS[1])

        self.responder.assert_called_with(STATES[1]['on_enter_message'])
        handle_message(self.session_id, expected_order.size, self.responder)
        self.responder.assert_called_with(STATES[2]['on_enter_message'])
        handle_message(self.session_id, 'отклаадр', self.responder)
        self.responder.assert_called_with('Я вас не понял. Попробуйте ответить еще раз.')


if __name__ == '__main__':
    unittest.main()
