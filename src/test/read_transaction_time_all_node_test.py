import unittest
from test_helper import *
import numpy as np

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

    def test_read_transaction_time_average_with_prom_data(self):
        list_line = get_list_line_from_kpi_with_ident("test_data.prom", "indy_average_per_second", "read_transactions")
        time_values = [extract_value_from_line(line) for line in list_line]
        average_expect = sum(time_values) / len(time_values)
        average_real = extract_value_from_line(get_list_line_from_kpi("test_data.prom","indy_read_transaction_time_all_node")[0])
        self.assertAlmostEqual(average_real, average_expect, delta= 0.001)


if __name__ == '__main__':
    unittest.main()
