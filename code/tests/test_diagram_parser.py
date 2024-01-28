import unittest

from networkx import DiGraph

from src.diagram_parser import DiagramParser

if __name__ == '__main__':
    unittest.main()


class TestDiagTextToFuncComp(unittest.TestCase):
    def test_exfig(self):
        prs = DiagramParser("testfiles/graph_txt/exfig.txt")
        expected = ("{h}{f} = {g}\n"
                    "{h}{i} = {j}")
        self.assertEquals(prs.to_func_comps(), expected)

    def test_rectangle(self):
        prs = DiagramParser("testfiles/graph_txt/rectangle.txt")
        func_comps = prs.to_func_comps()
        print(func_comps)
        self.assertEquals(func_comps.count("\n"), 2)


class TestPathToFuncComp(unittest.TestCase):
    def test_exfig(self):
        prs = DiagramParser("testfiles/graph_txt/exfig.txt")
        path = [("{A}", "{B}"), ("{B}", "{C}")]
        expected = "{h}{f}"
        actual = prs.path_to_func_comp(path)
        self.assertEquals(actual, expected)


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

        prs = DiagramParser("testfiles/graph_txt/exfig.txt")
        self.assertTrue(list(G.edges.data()) == list(prs.get_graph().edges.data()))

    def test_parse_exfig_no_lbl(self):
        self.assertRaises(Exception, DiagramParser, "testfiles/exfig_no_lbl.txt")

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
             "{\\mathbf{Set}}",
             {"name": "{\\mathrm{Hom}_{\\mathscr{A}}}"}),
            ("{\\mathscr{B}^{\\mathrm{op}} \\times \\mathscr{B}}",
             "{\\mathbf{Set}}",
             {"name": "{\\mathrm{Hom}_{\\mathscr{B}}}"})
        ])
        prs = DiagramParser("testfiles/graph_txt/complex_labels.txt")
        self.assertTrue(list(G.edges.data()) == list(prs.get_graph().edges.data()))

    def test_all_endomorphisms(self):
        prs = DiagramParser("testfiles/graph_txt/exfig_all_endo.txt")
        for node in prs.graph.nodes():
            self.assertEquals(prs.graph.nodes[node]['label'], '{X}')

    def test_some_endomorphisms(self):
        prs = DiagramParser("testfiles/graph_txt/exfig_some_endo.txt")
        expected_nodes_values = {
            "{A}": "{X}",
            "{B}": "{X}",
            "{C}": "{C}",
            "{D}": "{D}",
        }
        for node, label in expected_nodes_values.items():
            self.assertEquals(prs.graph.nodes[node]['label'], label)
