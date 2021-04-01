import unittest
from order import get_order_state_machine
from communication import parse_dictionary_option, parse_yes_no_option
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
        pass

    def test_parse_yes_no(self):
        pass


if __name__ == '__main__':
    unittest.main()
