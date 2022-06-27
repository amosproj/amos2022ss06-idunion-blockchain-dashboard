import unittest
from test_helper import *

class MyTestCase(unittest.TestCase):

    def test_data_not_redundant(self):
        list_line = get_list_line_from_kpi("test_data.prom", "indy_read_transaction_time_all_node")
        print(list_line)
        self.assertEqual(len(list_line), 1)

    def test_read_transaction_time_range(self):
        list_line = get_list_line_from_kpi("test_data.prom", "indy_read_transaction_time_all_node")
        line = list_line[0]
        time = extract_value_from_line(line)
        self.assertTrue(time >= 0)
        self.assertTrue(time < 1)


if __name__ == '__main__':
    unittest.main()
