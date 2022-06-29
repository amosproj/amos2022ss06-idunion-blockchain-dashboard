import unittest


class MyTestCase(unittest.TestCase):
    def test_export_as_prometheus_format(self):
        # self.assertEqual(True, False)  # add assertion here
        f = open("test_data.prom", "r")
        self.assertEqual(f.read(4), "indy")


if __name__ == '__main__':
    unittest.main()
