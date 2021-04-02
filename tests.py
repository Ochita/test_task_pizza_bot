import unittest
import itertools
from mock import Mock
from order import STATES
from validators import SIZE_OPTIONS, PAYMENT_OPTIONS
from communication import parse_dictionary_option, parse_yes_no_option, start_order, handle_message
from utils import get_respond_mapper, processed_message


@processed_message
def processing_return(message, *args, **kwargs):
    return message


class TestUtils(unittest.TestCase):
    def test_mapper(self):
        pass

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
    def test_parse_option(self):
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


class OrderMock:
    def __init__(self, size, payment):
        self.size = size
        self.payment = payment


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
