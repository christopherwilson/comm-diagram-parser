import unittest
from src.parser import Parser


class TestTxtToCoDi(unittest.TestCase):
    def test_exfig_to_codi(self):
        prs = Parser("testfiles/exfig.txt")
        diagram = ("\\obj {A & B \\\\ C & D \\\\};\n\\mor A f:-> B;\n\\mor A g:-> C;\n\\mor B h:-> C;\n\\mor D i:-> "
                   "B;\n\\mor D j:-> C;")
        print(prs.to_codi())
        self.assertEquals(prs.to_codi(), diagram)

    def test_exfig_no_lbl_to_codi(self):
        prs = Parser("testfiles/exfig_no_lbl.txt")
        diagram = ("\\obj {A & B \\\\ C & D \\\\};\n\\mor A :-> B;\n\\mor A :-> C;\n\\mor B :-> C;\n\\mor D :-> "
                   "B;\n\\mor D :-> C;")
        print(prs.to_codi())
        self.assertEquals(prs.to_codi(), diagram)


if __name__ == '__main__':
    unittest.main()
