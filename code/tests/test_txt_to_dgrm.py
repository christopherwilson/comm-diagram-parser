import unittest
from src.parser import Parser


class TestTxtToCoDi(unittest.TestCase):
    def test_exfig_to_codi(self):
        prs = Parser("testfiles/exfig.txt")
        print(prs.to_codi())

    def test_parse_complex_labels(self):
        prs = Parser("testfiles/complex_labels.txt")
        print(prs.to_codi())


if __name__ == '__main__':
    unittest.main()
