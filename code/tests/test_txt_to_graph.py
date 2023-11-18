import unittest
from networkx import DiGraph, is_isomorphic
from src.parser import Parser
from os import getcwd


class TestTxtToGraph(unittest.TestCase):
    def test_parse_exfig(self):
        G = DiGraph()
        G.add_edges_from([
            ("A", "B", {"name": "f"}),
            ("A", "C", {"name": "g"}),
            ("B", "C", {"name": "h"}),
            ("D", "B", {"name": "i"}),
            ("D", "C", {"name": "j"})
        ])

        prs = Parser("testfiles/exfig.txt")
        self.assertTrue(list(G.edges.data()) == list(prs.get_graph().edges.data()))

    def test_parse_exfig_no_lbl(self):
        G = DiGraph()
        G.add_edges_from([
            ("A", "B", {"name": ""}),
            ("A", "C", {"name": ""}),
            ("B", "C", {"name": ""}),
            ("D", "B", {"name": ""}),
            ("D", "C", {"name": ""})
        ])
        prs = Parser("testfiles/exfig_no_lbl.txt")
        self.assertTrue(list(G.edges.data()) == list(prs.get_graph().edges.data()))


class TestExtractLabel(unittest.TestCase):
    def test_extract_label_basic(self):
        test_str_basic: str = '{A}'
        self.assertEquals('A', Parser.extract_label(test_str_basic, 1))

    def test_extract_label_repeat(self):
        test_str_repeat: str = '{A}{B}'
        self.assertEquals('A', Parser.extract_label(test_str_repeat, 1))

    def test_extract_label_brackets(self):
        test_str_interior_brackets: str = '{\mathbf{I}^{\mathscal{A}}_{X,Y}}'
        self.assertEquals('\mathbf{I}^{\mathscal{A}}_{X,Y}', Parser.extract_label(test_str_interior_brackets, 1))

    def test_extract_label_complex(self):
        test_str_complex: str = '{[\mathscal{A}^{\op},X](-,-)}{H_{A}}'
        self.assertEquals('[\mathscal{A}^{\op},X](-,-)', Parser.extract_label(test_str_complex, 1))

    def test_extract_label_empty(self):
        test_str_empty: str = '{}{A}'
        self.assertEquals('', Parser.extract_label(test_str_empty, 1))


if __name__ == '__main__':
    unittest.main()
