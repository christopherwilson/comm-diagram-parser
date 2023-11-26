import unittest
from src.diagram_parser import DiagramParser


class TestTxtToCoDi(unittest.TestCase):
    def test_exfig_to_codi(self):
        prs = DiagramParser("testfiles/exfig.txt")
        print(prs.to_codi())

    def test_parse_complex_labels(self):
        prs = DiagramParser("testfiles/complex_labels.txt")
        print(prs.to_codi())


if __name__ == '__main__':
    unittest.main()
