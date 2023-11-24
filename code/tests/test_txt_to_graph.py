import unittest
from networkx import DiGraph
from src.parser import Parser


class TestTxtToGraph(unittest.TestCase):
    def test_parse_exfig(self):
        G = DiGraph()
        G.add_edges_from([
            ("{A}", "{B}", {"name": "{f}"}),
            ("{A}", "{C}", {"name": "{g}"}),
            ("{B}", "{C}", {"name": "{h}"}),
            ("{D}", "{B}", {"name": "{i}"}),
            ("{D}", "{C}", {"name": "{j}"})
        ])

        prs = Parser("testfiles/exfig.txt")
        self.assertTrue(list(G.edges.data()) == list(prs.get_graph().edges.data()))

    def test_parse_exfig_no_lbl(self):
        G = DiGraph()
        G.add_edges_from([
            ("{A}", "{B}", {"name": ""}),
            ("{A}", "{C}", {"name": ""}),
            ("{B}", "{C}", {"name": ""}),
            ("{D}", "{B}", {"name": ""}),
            ("{D}", "{C}", {"name": ""})
        ])
        prs = Parser("testfiles/exfig_no_lbl.txt")
        self.assertTrue(list(G.edges.data()) == list(prs.get_graph().edges.data()))

    def test_parse_complex(self):
        G = DiGraph()
        G.add_edges_from([
            ("{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{B}}",
             "{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{A}}",
             {"name": "{1 \\times G}"}),
            ("{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{B}}",
             "{\\mathscr{B}^{\\mathrm{op}} \\times \\mathscr{B}}",
             {"name": "{F^{\\mathrm{op}} \\times 1}"}),
            ("{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{A}}",
             "{\\mathbf{Set.}}",
             {"name": "{\\mathrm{Hom}_{\\mathscr{A}}}"}),
            ("{\\mathscr{B}^{\\mathrm{op}} \\times \\mathscr{B}}",
             "{\\mathbf{Set.}}",
             {"name": "{\\mathrm{Hom}_{\\mathscr{B}}}"})
        ])
        prs = Parser("testfiles/complex_labels.txt")
        self.assertTrue(list(G.edges.data()) == list(prs.get_graph().edges.data()))


class TestExtractLabel(unittest.TestCase):
    def test_extract_label_basic(self):
        test_str_basic: str = '{A}'
        self.assertEquals(('{A}', 3), Parser.extract_label(test_str_basic, 1))

    def test_extract_label_repeat(self):
        test_str_repeat: str = '{A}{B}'
        self.assertEquals(('{A}', 3), Parser.extract_label(test_str_repeat, 1))

    def test_extract_label_brackets(self):
        test_str_interior_brackets: str = '{\mathbf{I}^{\mathscal{A}}_{X,Y}}'
        self.assertEquals(('{\\mathbf{I}^{\\mathscal{A}}_{X,Y}}', 33), Parser.extract_label(test_str_interior_brackets, 1))

    def test_extract_label_complex(self):
        test_str_complex: str = '{[\mathscal{A}^{\op},X](-,-)}{H_{A}}'
        self.assertEquals(('{[\mathscal{A}^{\op},X](-,-)}', 29), Parser.extract_label(test_str_complex, 1))

    def test_extract_label_empty(self):
        test_str_empty: str = '{}{A}'
        self.assertEquals(('{}', 2), Parser.extract_label(test_str_empty, 1))

    def test_extract_label_complex_file(self):
        line1 = ["{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{B}}{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{A}}{1 \\times G}",
                 "{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{A}}{1 \\times G}",
                 "{1 \\times G}"]
        self.assertEquals("{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{B}}", Parser.extract_label(line1[0], 1)[0])


if __name__ == '__main__':
    unittest.main()
