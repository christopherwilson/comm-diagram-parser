import random
import unittest

import networkx as nx

from src.morphism_parser import MorphismParser

if __name__ == '__main__':
    unittest.main()


class TestAddEdge(unittest.TestCase):
    def test_adding_to_empty(self):
        parser = MorphismParser("testfiles/blank.txt")
        expected_morphs = {"{f}": (0, 1)}
        expected_morphs_by_domain = {0: ["{f}"]}
        expected_morphs_by_codomain = {1: ["{f}"]}
        parser.add_edge("{f}", 0, 1)
        self.assertEqual(expected_morphs, parser.morphs)
        self.assertEqual(expected_morphs_by_domain, parser.morphs_by_domain)
        self.assertEqual(expected_morphs_by_codomain, parser.morphs_by_codomain)

    def test_adding_to_existing_func(self):
        parser = MorphismParser("testfiles/blank.txt")
        parser.morphs = {"{g}": (0, 2), "{h}": (3, 1)}
        parser.morphs_by_domain = {0: ["{g}"], 3: ["{h}"]}
        parser.morphs_by_codomain = {2: ["{g}"], 1: ["{h}"]}

        expected_morphs = {"{f}": (0, 1), "{g}": (0, 2), "{h}": (3, 1)}
        expected_morphs_by_domain = {0: ["{g}", "{f}"], 3: ["{h}"]}
        expected_morphs_by_codomain = {1: ["{h}", "{f}"], 2: ["{g}"]}

        parser.add_edge("{f}", 0, 1)

        self.assertEqual(expected_morphs, parser.morphs)
        self.assertEqual(expected_morphs_by_domain, parser.morphs_by_domain)
        self.assertEqual(expected_morphs_by_codomain, parser.morphs_by_codomain)


class TestContractDomain(unittest.TestCase):

    def verify_result(self, expected_edges, expected_graph, expected_morphs, expected_morphs_by_codomain,
                      expected_morphs_by_domain, parser):
        nonempty_morphs_by_domain = {}
        for key in parser.morphs_by_domain.keys():
            if parser.morphs_by_domain[key]:
                nonempty_morphs_by_domain[key] = parser.morphs_by_domain[key]
        nonempty_morphs_by_codomain = {}
        for key in parser.morphs_by_codomain.keys():
            if parser.morphs_by_codomain[key]:
                nonempty_morphs_by_codomain[key] = parser.morphs_by_codomain[key]
        for edge in list(parser.graph.edges.data()):
            expected_edges.pop(expected_edges.index(edge))
        self.assertTrue(expected_edges == [])
        self.assertTrue(nx.is_isomorphic(parser.graph, expected_graph))
        self.assertEqual(expected_morphs, parser.morphs)
        self.assertEqual(expected_morphs_by_domain, nonempty_morphs_by_domain)
        self.assertEqual(expected_morphs_by_codomain, nonempty_morphs_by_codomain)

    def test_two_maps(self):
        parser = MorphismParser("testfiles/blank.txt")
        parser.morphs = {"f": (0, 1), "g": (2, 3)}
        parser.morphs_by_domain = {0: ["f"], 2: ["g"]}
        parser.morphs_by_codomain = {1: ["f"], 3: ["g"]}
        parser.graph = nx.DiGraph([(0, 1, {"name": "f"}), (2, 3, {"name": "g"})])

        parser.contract_objects(2, 0)

        expected_edges = [(0, 1, {"name": "f"}), (0, 3, {"name": "g"})]
        expected_graph = nx.DiGraph([(0, 1, {"name": "f"}), (0, 3, {"name": "g"})])
        expected_morphs = {"f": (0, 1), "g": (0, 3)}
        expected_morphs_by_domain = {0: ["f", "g"]}
        expected_morphs_by_codomain = {1: ["f"], 3: ["g"]}

        self.verify_result(expected_edges, expected_graph, expected_morphs, expected_morphs_by_codomain,
                           expected_morphs_by_domain, parser)

    def test_when_domains_in_chains(self):
        parser = MorphismParser("testfiles/blank.txt")
        parser.morphs = {"f": (0, 1), "g": (1, 2), "h": (3, 4), "k": (4, 5)}
        parser.morphs_by_domain = {
            0: ["f"],
            1: ["g"],
            3: ["h"],
            4: ["k"]
        }
        parser.morphs_by_codomain = {
            1: ["f"],
            2: ["g"],
            4: ["h"],
            5: ["k"]
        }
        parser.graph = nx.DiGraph([
            (0, 1, {"name": "f"}),
            (1, 2, {"name": "g"}),
            (3, 4, {"name": "h"}),
            (4, 5, {"name": "k"}),
        ])

        expected_morphs = {
            "f": (0, 1),
            "g": (1, 2),
            "h": (3, 1),
            "k": (1, 5)
        }
        expected_morphs_by_domain = {
            0: ["f"],
            1: ["g", "k"],
            3: ["h"],
        }

        expected_morphs_by_codomain = {
            1: ["f", "h"],
            2: ["g"],
            5: ["k"],
        }

        expected_edges = [
            (0, 1, {"name": "f"}),
            (1, 2, {"name": "g"}),
            (3, 1, {"name": "h"}),
            (1, 5, {"name": "k"}),
        ]
        expected_graph = nx.DiGraph(expected_edges)

        parser.contract_objects(4, 1)

        self.verify_result(expected_edges, expected_graph, expected_morphs, expected_morphs_by_codomain,
                           expected_morphs_by_domain, parser)

    def test_merging_codomains(self):
        parser = MorphismParser("testfiles/blank.txt")
        parser.morphs = {"f": (0, 1), "g": (2, 3)}
        parser.morphs_by_domain = {0: ["f"], 2: ["g"]}
        parser.morphs_by_codomain = {1: ["f"], 3: ["g"]}
        parser.graph = nx.DiGraph([(0, 1, {"name": "f"}), (2, 3, {"name": "g"})])

        parser.contract_objects(3, 1)

        expected_edges = [(0, 1, {"name": "f"}), (2, 1, {"name": "g"})]
        expected_graph = nx.DiGraph(expected_edges)
        expected_morphs = {"f": (0, 1), "g": (2, 1)}
        expected_morphs_by_domain = {0: ["f"], 2: ["g"]}
        expected_morphs_by_codomain = {1: ["f", "g"]}

        self.verify_result(expected_edges, expected_graph, expected_morphs, expected_morphs_by_codomain,
                           expected_morphs_by_domain, parser)


class TestParseLine(unittest.TestCase):
    def test_triangle(self):
        line = "{g}{f}={h}"
        parser = MorphismParser("testfiles/blank.txt")
        parser.parse_line(line)

        expected_graph = nx.DiGraph([(0, 1), (1, 2), (0, 2)])
        self.assertTrue(nx.is_isomorphic(expected_graph, parser.graph))

    def test_bubble(self):
        line = "{k}{h}{g}{f}={k}{h'}{g'}{f}"
        parser = MorphismParser("testfiles/blank.txt")
        parser.parse_line(line)

        expected_edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (1, 5),
            (5, 3)
        ]
        expected_graph = nx.DiGraph(expected_edges)
        print(parser.to_tikz_diagram())
        self.assertTrue(nx.is_isomorphic(expected_graph, parser.graph))

    def test_intro_ex_fig(self):
        parser = MorphismParser("testfiles/morphisms_txt/intro_ex_fig")
        print(parser.to_tikz_diagram())


class TestMorphismParser(unittest.TestCase):
    def test_fig8_long_first(self):
        parser = MorphismParser("testfiles/morphisms_txt/fig8_long_fst.txt")
        expected_graph = nx.DiGraph([
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
            (3, 4),
            (3, 5),
            (4, 6),
            (5, 6)
        ])

        self.assertTrue(nx.is_isomorphic(expected_graph, parser.graph))
        for node in parser.graph.nodes:
            self.assertTrue(parser.graph.nodes[node]['label'], "$\\bullet$")

    def test_fig8_long_mid(self):
        parser = MorphismParser("testfiles/morphisms_txt/fig8_long_mid.txt")
        expected_graph = nx.DiGraph([
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
            (3, 4),
            (3, 5),
            (4, 6),
            (5, 6)
        ])

        self.assertTrue(nx.is_isomorphic(expected_graph, parser.graph))

    def test_fig8_long_last(self):
        parser = MorphismParser("testfiles/morphisms_txt/fig8_long_last.txt")
        expected_graph = nx.DiGraph([
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
            (3, 4),
            (3, 5),
            (4, 6),
            (5, 6)
        ])

        self.assertTrue(nx.is_isomorphic(expected_graph, parser.graph))

    def test_exfig(self):
        parser = MorphismParser("testfiles/morphisms_txt/exfig.txt")
        expected_graph = nx.DiGraph([
            (0, 1),
            (0, 2),
            (1, 2),
            (3, 1),
            (3, 2)
        ])

        self.assertTrue(nx.is_isomorphic(expected_graph, parser.graph))

    def test_cycle(self):
        parser = MorphismParser("testfiles/morphisms_txt/cycle.txt")
        expected_graph = nx.DiGraph([
            (0, 1),
            (1, 2),
            (2, 0)
        ])

        print(list(parser.graph.edges))
        self.assertTrue(nx.is_isomorphic(expected_graph, parser.graph))

