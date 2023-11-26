import unittest
from src.diagram_parser import DiagramParser


class TestTxtToFuncCopm(unittest.TestCase):
    def test_exfig(self):
        prs = DiagramParser("testfiles/exfig.txt")
        expected = ("{h} o {f} = {g}\n"
                    "{h} o {i} = {j}")
        self.assertEquals(prs.to_func_comps(), expected)

    def test_rectangle(self):
        prs = DiagramParser("testfiles/rectangle.txt")
        func_comps = prs.to_func_comps()
        print(func_comps)
        self.assertEquals(func_comps.count("\n"), 2)


class TestPathToFuncComp(unittest.TestCase):
    def test_exfig(self):
        prs = DiagramParser("testfiles/exfig.txt")
        path = [("{A}", "{B}"), ("{B}", "{C}")]
        expected = "{h} o {f}"
        actual = prs.path_to_func_comp(path)
        self.assertEquals(actual, expected)


if __name__ == '__main__':
    unittest.main()
