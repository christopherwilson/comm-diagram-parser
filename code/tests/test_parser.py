import unittest
import re

import networkx as nx

from src.parser import Parser

# https://q.uiver.app/#q=WzAsNixbMCwxLCIwIl0sWzEsMSwiMSJdLFsyLDEsIjMiXSxbMywxLCI0Il0sWzEsMCwiMiJdLFsyLDIsIjUiXSxbMCwxLCJmIl0sWzEsMiwiZyJdLFsyLDMsImgiXSxbMCw0LCJpIl0sWzQsMiwiaiJdLFsxLDUsImsiLDJdLFs1LDMsImwiLDJdXQ==
STAGGERED = nx.DiGraph([
    (0, 1, {"name": "{f}"}),
    (1, 3, {"name": "{g}"}),
    (3, 4, {"name": "{h}"}),
    (0, 2, {"name": "{i}"}),
    (2, 3, {"name": "{j}"}),
    (1, 5, {"name": "{k}"}),
    (5, 4, {"name": "{l}"})
])

# https://q.uiver.app/#q=WzAsNCxbMCwxLCIwIl0sWzEsMCwiMSJdLFsxLDEsIjIiXSxbMSwyLCIzIl0sWzAsMSwiZiJdLFswLDIsImciLDJdLFswLDMsImgiLDJdLFsyLDEsImkiLDJdLFsyLDMsImoiXV0=
LIMIT_DEF = nx.DiGraph([
    (0, 1, {"name": "{f}"}),
    (0, 2, {"name": "{g}"}),
    (0, 3, {"name": "{h}"}),
    (2, 1, {"name": "{i}"}),
    (2, 3, {"name": "{j}"})
])

# https://q.uiver.app/#q=WzAsNCxbMCwxLCIwIl0sWzEsMCwiMSJdLFsxLDEsIjIiXSxbMSwyLCIzIl0sWzEsMCwiZiIsMl0sWzIsMCwiZyJdLFszLDAsImgiXSxbMSwyLCJpIl0sWzMsMiwiaiIsMl1d
EXAMPLE_FIG = nx.DiGraph([
    (1, 0, {"name": "{f}"}),
    (2, 0, {"name": "{g}"}),
    (3, 2, {"name": "{h}"}),
    (1, 0, {"name": "{i}"}),
    (3, 0, {"name": "{j}"})
])

# https://q.uiver.app/#q=WzAsNixbMCwyLCIwIl0sWzEsMiwiMSJdLFsyLDIsIjIiXSxbMCwxLCIzIl0sWzEsMCwiNCJdLFsyLDEsIjUiXSxbMCwxLCJmIiwyXSxbMSwyLCJnIiwyXSxbMCwzLCJoIl0sWzMsNCwiaiJdLFs0LDUsImsiXSxbNSwyLCJsIl0sWzMsNSwiaSIsMl1d
BRIDGE = nx.DiGraph([
    (0, 1, {"name": "{f}"}),
    (1, 2, {"name": "{g}"}),
    (0, 3, {"name": "{h}"}),
    (3, 5, {"name": "{i}"}),
    (3, 4, {"name": "{j}"}),
    (4, 5, {"name": "{k}"}),
    (5, 2, {"name": "{l}"})
])

# https://q.uiver.app/#q=WzAsOCxbMCwxLCIwIl0sWzEsMSwiMSJdLFsyLDEsIjMiXSxbMywxLCI0Il0sWzEsMiwiMiJdLFsyLDAsIjUiXSxbNCwxLCI3Il0sWzMsMiwiNiJdLFswLDEsImYiXSxbMSwyLCJnIl0sWzIsMywiaCJdLFswLDQsImkiLDJdLFs0LDIsImoiLDJdLFsxLDUsImsiXSxbNSwzLCJsIl0sWzMsNiwibSJdLFsyLDcsIm4iLDJdLFs3LDYsIm8iLDJdXQ==
DOUBLY_STAGGERED = nx.DiGraph([
    (0, 1, {"name": "{f}"}),
    (1, 3, {"name": "{g}"}),
    (3, 4, {"name": "{h}"}),
    (0, 2, {"name": "{i}"}),
    (2, 3, {"name": "{j}"}),
    (1, 5, {"name": "{k}"}),
    (5, 4, {"name": "{l}"}),
    (4, 7, {"name": "{m}"}),
    (3, 6, {"name": "{n}"}),
    (6, 7, {"name": "{o}"})
])

# https://q.uiver.app/#q=WzAsNyxbMCwwLCIwIl0sWzEsMiwiMiJdLFswLDEsIjEiXSxbMSwxLCIzIl0sWzEsMCwiNCJdLFsyLDEsIjUiXSxbMiwwLCI2Il0sWzAsMiwiZiIsMl0sWzIsMSwiZyIsMl0sWzAsMywiaCJdLFszLDEsImkiXSxbMCw0LCJqIl0sWzQsMywiayJdLFszLDUsImwiXSxbNSwxLCJtIl0sWzYsNCwibiIsMl0sWzYsNSwicCJdXQ==
INTRO_EXFIG = nx.DiGraph([
    (0, 1, {"name": "{f}"}),
    (1, 2, {"name": "{g}"}),
    (0, 3, {"name": "{h}"}),
    (3, 2, {"name": "{i}"}),
    (0, 4, {"name": "{j}"}),
    (4, 3, {"name": "{k}"}),
    (3, 5, {"name": "{l}"}),
    (5, 2, {"name": "{m}"}),
    (6, 4, {"name": "{n}"}),
    (6, 5, {"name": "{p}"})
])

# https://q.uiver.app/#q=WzAsNCxbMCwxLCIwIl0sWzEsMCwiMSJdLFsxLDEsIjIiXSxbMSwyLCIzIl0sWzAsMSwiZiJdLFswLDIsImciLDJdLFswLDMsImgiLDJdLFsxLDIsImkiXSxbMiwzLCJqIl1d
BIG_CYCLE_TRIANGLES = nx.DiGraph([
    (0, 1, {"name": "{f}"}),
    (0, 2, {"name": "{g}"}),
    (0, 3, {"name": "{h}"}),
    (1, 2, {"name": "{i}"}),
    (2, 3, {"name": "{j}"})
])

CONE = nx.DiGraph([
    (0, 1, {"name": "{f}"}),
    (1, 2, {"name": "{g}"}),
    (2, 3, {"name": "{h}"}),
    (2, 4, {"name": "{i}"}),
    (0, 5, {"name": "{j}"}),
    (5, 6, {"name": "{k}"}),
    (6, 3, {"name": "{l}"}),
    (6, 4, {"name": "{m}"})
])



if __name__ == '__main__':
    unittest.main()


class TestListsToLatex(unittest.TestCase):
    def test_sqr_two(self):
        lst = [
            [1, 2],
            [3, 4]
        ]
        txt = "1 & 2 \\\\ 3 & 4"
        self.assertEquals(txt, Parser.lists_to_latex_matrix(lst))

    def test_two_three(self):
        lst = [
            ["A", "B", "C"],
            ["D", "E", "F"]
        ]
        txt = "A & B & C \\\\ D & E & F"
        self.assertEquals(txt, Parser.lists_to_latex_matrix(lst))

    def test_three_two(self):
        lst = [
            ["A", "B"],
            ["C", "D"],
            ["E", "F"]
        ]
        txt = "A & B \\\\ C & D \\\\ E & F"
        self.assertEquals(txt, Parser.lists_to_latex_matrix(lst))

    def test_uncompleted(self):
        lst = [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G"]
        ]
        txt = "A & B & C \\\\ D & E & F \\\\ G"
        self.assertEquals(txt, Parser.lists_to_latex_matrix(lst))


class TestExtractLabel(unittest.TestCase):
    def test_extract_label_basic(self):
        test_str_basic: str = '{A}'
        self.assertEquals(('{A}', 3), Parser.extract_label(test_str_basic, 1))

    def test_extract_label_repeat(self):
        test_str_repeat: str = '{A}{B}'
        self.assertEquals(('{A}', 3), Parser.extract_label(test_str_repeat, 1))

    def test_extract_label_brackets(self):
        test_str_interior_brackets: str = '{\\mathbf{I}^{\\mathscal{A}}_{X,Y}}'
        self.assertEquals(('{\\mathbf{I}^{\\mathscal{A}}_{X,Y}}', 33),
                          Parser.extract_label(test_str_interior_brackets, 1))

    def test_extract_label_complex(self):
        test_str_complex: str = '{[\\mathscal{A}^{\\op},X](-,-)}{H_{A}}'
        self.assertEquals(('{[\\mathscal{A}^{\\op},X](-,-)}', 29), Parser.extract_label(test_str_complex, 1))

    def test_extract_label_empty(self):
        test_str_empty: str = '{}{A}'
        self.assertEquals(('{}', 2), Parser.extract_label(test_str_empty, 1))

    def test_extract_label_complex_file(self):
        line1 = ["{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{B}}{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{"
                 "A}}{1 \\times G}",
                 "{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{A}}{1 \\times G}",
                 "{1 \\times G}"]
        self.assertEquals("{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{B}}", Parser.extract_label(line1[0], 1)[0])


class TestToLatex(unittest.TestCase):
    def test_exfig(self):
        parser = Parser()
        parser.graph = nx.DiGraph([("A", "B", {"name": "f"}),
                                   ("A", "C", {"name": "g"}),
                                   ("B", "C", {"name": "h"}),
                                   ("D", "B", {"name": "i"}),
                                   ("D", "C", {"name": "j"})
                                   ])
        print(parser.to_latex())


class TestToDiagramRepresentation(unittest.TestCase):
    def test_exfig(self):
        parser = Parser()
        parser.graph = nx.DiGraph([("A", "B", {"name": "f"}),
                                   ("A", "C", {"name": "g"}),
                                   ("B", "C", {"name": "h"}),
                                   ("D", "B", {"name": "i"}),
                                   ("D", "C", {"name": "j"})
                                   ])
        for node in parser.graph:
            parser.graph.nodes[node]["label"] = node

        lines = []
        with open("testfiles/graph_txt/exfig.txt", "r") as f:
            for line in f:
                if line[0] == "%":
                    break
                lines.append(line)
        expected_output = "".join(lines)

        self.assertEquals(parser.to_diagram_representation() + "\n", expected_output)

    def test_exfig_endos(self):
        parser = Parser()
        parser.graph = nx.DiGraph([("A", "B", {"name": "f"}),
                                   ("A", "C", {"name": "g"}),
                                   ("B", "C", {"name": "h"}),
                                   ("D", "B", {"name": "i"}),
                                   ("D", "C", {"name": "j"})
                                   ])
        for node in parser.graph:
            parser.graph.nodes[node]["label"] = "X"

        lines = []
        with open("testfiles/graph_txt/exfig_all_endo.txt", "r") as f:
            for line in f:
                if line[0] == "%":
                    break
                lines.append(line)
        expected_output = "".join(lines)

        self.assertEquals(parser.to_diagram_representation(), expected_output)


class TestToMorphisms(unittest.TestCase):
    def test_bubble(self):
        parser = Parser()
        # https://q.uiver.app/#q=WzAsOCxbMCwyLCIwIl0sWzEsMiwiMSJdLFsyLDEsIjIiXSxbMywyLCIzIl0sWzQsMiwiNCJdLFsyLDMsIjUiXSxbMSwwLCI2Il0sWzMsMCwiNyJdLFswLDEsImYiLDJdLFsxLDIsImciXSxbMiwzLCJoIl0sWzMsNCwiaSJdLFsxLDUsImoiLDJdLFs1LDMsImsiLDJdLFswLDYsImwiXSxbNiw3LCJtIl0sWzcsNCwibiJdXQ==
        parser.graph = nx.DiGraph([
            (0, 1, {"name": "{f}"}),
            (1, 2, {"name": "{g}"}),
            (2, 3, {"name": "{h}"}),
            (3, 4, {"name": "{i}"}),
            (1, 5, {"name": "{j}"}),
            (5, 3, {"name": "{k}"}),
            (0, 6, {"name": "{l}"}),
            (6, 7, {"name": "{m}"}),
            (7, 4, {"name": "{n}"})
        ])

        print(parser.to_morphism_representation())
        # TODO fix this test
        pattern = re.compile(
            r"\A({h}{g} ?= ?{k}{j}\n{i}({h}{g}|{k}{j}){f} ?= ?{n}{m}{l}|{i}({h}{g}|{k}{j}){f} ?= ?{n}{m}{l}\n{h}{g} ?= ?{k}{j})\Z")
        self.assertRegex(parser.to_morphism_representation(), pattern)

    def test_non_comp_morphs(self):
        parser = Parser()
        parser.graph = nx.DiGraph([
            (0, 1, {"name": "{f}"}),
            (1, 2, {"name": "{g}"})
        ])
        self.assertEquals(parser.to_morphism_representation(), "{g}{f}")

    def test_limit(self):
        parser = Parser()
        parser.graph = LIMIT_DEF
        print(parser.to_morphism_representation())

    def test_cone(self):
        parser = Parser()
        parser.graph = CONE
        print(parser.to_morphism_representation())


# class TestSearchForEquivCompMorphs(unittest.TestCase):
#     @staticmethod
#     def assertEquivalent(dict1, dict2) -> bool:
#         if dict1.keys() != dict2.keys():
#             return False
#         for domain in dict1:
#             if dict1[domain].keys() != dict2[domain].keys():
#                 return False
#             for codomain in dict1[domain]:
#                 if len(dict1[domain][codomain]) != len(dict2[domain][codomain]):
#                     return False
#                 for chain in dict1[domain][codomain]:
#                     if chain not in dict2[domain][codomain]:
#                         return False
#         return True
#
#     def test_staggered_diag(self):
#         graph = STAGGERED
#
#         expected_dict = {
#             0: {3: [[0, 1, 3],
#                     [0, 2, 3]],
#                 4: [[0, 1, 3, 4]]},
#             1: {3: [[1, 3]],
#                 4: [[1, 3, 4],
#                     [1, 5, 4]]},
#             2: {4: [[2, 3, 4]]}
#         }
#
#         prsr = Parser()
#         prsr.graph = graph
#         prsr.unvisited_nodes = set(prsr.graph.nodes)
#         prsr.search_for_eq_comp_morphs(0, [], [], set())
#
#         print(prsr.comp_morph_chains)
#         self.assertTrue(self.assertEquivalent(expected_dict, prsr.comp_morph_chains))
#
#     def test_limit_diag(self):
#         graph = LIMIT_DEF
#
#         expected_dict = {
#             0: {2: [[0, 1, 2], [0, 2]],
#                 3: [[0, 1, 3], [0, 3]]},
#             1: {2: [[1, 2]],
#                 3: [[1, 3]]}
#         }
#
#         prsr = Parser()
#         prsr.graph = graph
#         prsr.unvisited_nodes = set(prsr.graph.nodes)
#         prsr.search_for_eq_comp_morphs(0, [], [], set())
#
#         self.assertTrue(self.assertEquivalent(expected_dict, prsr.comp_morph_chains))
#
#     def test_bridges(self):
#         graph = BRIDGE
#
#         expected_dict = {
#             0: {5: [[0, 3, 5]],
#                 2: [[0, 1, 2], [0, 3, 5, 2]]},
#             3: {5: [[3, 5], [3, 4, 5]],
#                 2: [[3, 5, 2]]}
#         }
#
#         prsr = Parser()
#         prsr.graph = graph
#         prsr.unvisited_nodes = set(prsr.graph.nodes)
#         prsr.search_for_eq_comp_morphs(0, [], [], set())
#
#         print(prsr.comp_morph_chains)
#         self.assertTrue(self.assertEquivalent(expected_dict, prsr.comp_morph_chains))
#
#     def test_doubly_staggered_diag(self):
#         graph = DOUBLY_STAGGERED
#
#         expected_dict = {
#             0: {3: [[0, 1, 3],
#                     [0, 2, 3]],
#                 4: [[0, 1, 3, 4]],
#                 7: [[0, 1, 3, 4, 7]]},
#             1: {3: [[1, 3]],
#                 4: [[1, 3, 4],
#                     [1, 5, 4]],
#                 7: [[1, 3, 4, 7]]},
#             3: {4: [[3, 4]],
#                 7: [[3, 4, 7], [3, 6, 7]]},
#             5: {7: [[5, 4, 7]]},
#             2: {4: [[2, 3, 4]],
#                 7: [[2, 3, 4, 7]]}
#         }
#
#         prsr = Parser()
#         prsr.graph = graph
#         prsr.unvisited_nodes = set(prsr.graph.nodes)
#         prsr.search_for_eq_comp_morphs(0, [], [], set())
#
#         print(prsr.comp_morph_chains)
#         self.assertTrue(self.assertEquivalent(expected_dict, prsr.comp_morph_chains))
#
#     def test_complicated_graph(self):
#         graph = INTRO_EXFIG
#
#         expected_dict = {}
#
#         prsr = Parser()
#         prsr.graph = graph
#         prsr.unvisited_nodes = set(prsr.graph.nodes)
#         prsr.search_for_eq_comp_morphs(0, [], [], set())
#         prsr.search_for_eq_comp_morphs(6, [], [], set())
#
#         print(prsr.comp_morph_chains)
#         self.assertTrue(self.assertEquivalent(expected_dict, prsr.comp_morph_chains))
#
#     def test_two_domains(self):
#         graph = BIG_CYCLE_TRIANGLES
#
#         expected_dict = {}
#
#         prsr = Parser()
#         prsr.graph = graph
#         prsr.unvisited_nodes = set(prsr.graph.nodes)
#         prsr.search_for_eq_comp_morphs(0, [], [], set())
#         # prsr.search_for_eq_comp_morphs(4, [], [], set())
#
#         print(prsr.comp_morph_chains)
#         self.assertTrue(self.assertEquivalent(expected_dict, prsr.comp_morph_chains))


class TestCycleBasis(unittest.TestCase):

    @staticmethod
    def do_cycles_match(expected_cycles, actual_cycles):
        if len(expected_cycles) != len(actual_cycles):
            return False
        for cycle in actual_cycles:
            if set(cycle) not in expected_cycles:
                return False
        return True

    def test_staggered(self):
        prsr = Parser()
        prsr.graph = STAGGERED
        expected_cycles = [
            {0, 1, 3, 2},
            {1, 3, 4, 5}
        ]

        cycles_match = self.do_cycles_match(expected_cycles, prsr.find_undirected_cycle_basis())
        self.assertTrue(cycles_match)

    def test_big_cycle_triangles(self):
        prsr = Parser()
        prsr.graph = BIG_CYCLE_TRIANGLES
        expected_cycles = [
            {0, 1, 2},
            {0, 2, 3}
        ]

        cycles_match = self.do_cycles_match(expected_cycles, prsr.find_undirected_cycle_basis())
        self.assertTrue(cycles_match)

    def test_bridge(self):
        prsr = Parser()
        prsr.graph = BRIDGE
        expected_cycles = [
            {0, 1, 2, 5, 3},
            {3, 4, 5}
        ]

        cycles_match = self.do_cycles_match(expected_cycles, prsr.find_undirected_cycle_basis())
        self.assertTrue(cycles_match)

    def test_double_stagger(self):
        prsr = Parser()
        prsr.graph = DOUBLY_STAGGERED
        expected_cycles = [
            {0, 1, 3, 2},
            {1, 3, 4, 5},
            {3, 4, 7, 6}
        ]

        cycles_match = self.do_cycles_match(expected_cycles, prsr.find_undirected_cycle_basis())
        self.assertTrue(cycles_match)

    def test_intro_exfig(self):
        prsr = Parser()
        prsr.graph = INTRO_EXFIG
        expected_cycles = [
            {0, 4, 3},
            {3, 5, 2},
            {6, 4, 3, 5},
            {0, 1, 2, 3}
        ]

        cycles_match = self.do_cycles_match(expected_cycles, prsr.find_undirected_cycle_basis())
        self.assertTrue(cycles_match)
