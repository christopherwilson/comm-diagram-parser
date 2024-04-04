import unittest

import networkx as nx

from morphism_parser import MorphismParser
from src.converter import Converter

# https://q.uiver.app/#q=WzAsOCxbMCwyLCIwIl0sWzEsMiwiMSJdLFsyLDEsIjIiXSxbMywyLCIzIl0sWzQsMiwiNCJdLFsyLDMsIjUiXSxbMSwwLCI2Il0sWzMsMCwiNyJdLFswLDEsImYiLDJdLFsxLDIsImciXSxbMiwzLCJoIl0sWzMsNCwiaSJdLFsxLDUsImoiLDJdLFs1LDMsImsiLDJdLFswLDYsImwiXSxbNiw3LCJtIl0sWzcsNCwibiJdXQ
BRIDGE = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (2, 3, {"label": "{h}"}),
    (3, 4, {"label": "{i}"}),
    (1, 5, {"label": "{j}"}),
    (5, 3, {"label": "{k}"}),
    (0, 6, {"label": "{l}"}),
    (6, 7, {"label": "{m}"}),
    (7, 4, {"label": "{n}"})
])

# https://q.uiver.app/#q=WzAsOCxbMCwyLCIwIl0sWzEsMiwiMSJdLFsyLDEsIjIiXSxbMywyLCIzIl0sWzQsMiwiNCJdLFsyLDMsIjUiXSxbMSwwLCI2Il0sWzMsMCwiNyJdLFswLDEsImYiLDJdLFsxLDIsImciXSxbMiwzLCJoIl0sWzMsNCwiaSJdLFsxLDUsImoiLDJdLFs1LDMsImsiLDJdLFswLDYsImwiXSxbNiw3LCJtIl0sWzcsNCwibiJdXQ
GOGGLES = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (2, 3, {"label": "{h}"}),
    (3, 4, {"label": "{i}"}),
    (4, 8, {"label": "{p}"}),
    (8, 9, {"label": "{s}"}),
    (3, 10, {"label": "{q}"}),
    (10, 8, {"label": "{r}"}),
    (1, 5, {"label": "{j}"}),
    (5, 3, {"label": "{k}"}),
    (0, 6, {"label": "{l}"}),
    (6, 7, {"label": "{m}"}),
    (7, 9, {"label": "{n}"}),
])

# https://q.uiver.app/#q=WzAsNixbMCwxLCIwIl0sWzEsMSwiMSJdLFsyLDEsIjMiXSxbMywxLCI0Il0sWzEsMCwiMiJdLFsyLDIsIjUiXSxbMCwxLCJmIl0sWzEsMiwiZyJdLFsyLDMsImgiXSxbMCw0LCJpIl0sWzQsMiwiaiJdLFsxLDUsImsiLDJdLFs1LDMsImwiLDJdXQ==
STAGGERED = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 3, {"label": "{g}"}),
    (3, 4, {"label": "{h}"}),
    (0, 2, {"label": "{i}"}),
    (2, 3, {"label": "{j}"}),
    (1, 5, {"label": "{k}"}),
    (5, 4, {"label": "{l}"})
])

# https://q.uiver.app/#q=WzAsNCxbMCwxLCIwIl0sWzEsMCwiMSJdLFsxLDEsIjIiXSxbMSwyLCIzIl0sWzAsMSwiZiJdLFswLDIsImciLDJdLFswLDMsImgiLDJdLFsyLDEsImkiLDJdLFsyLDMsImoiXV0=
LIMIT_DEF = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (0, 2, {"label": "{g}"}),
    (0, 3, {"label": "{h}"}),
    (2, 1, {"label": "{i}"}),
    (2, 3, {"label": "{j}"})
])

# https://q.uiver.app/#q=WzAsNCxbMCwxLCIwIl0sWzEsMCwiMSJdLFsxLDEsIjIiXSxbMSwyLCIzIl0sWzEsMCwiZiIsMl0sWzIsMCwiZyJdLFszLDAsImgiXSxbMSwyLCJpIl0sWzMsMiwiaiIsMl1d
EXAMPLE_FIG = nx.DiGraph([
    (1, 0, {"label": "{f}"}),
    (2, 0, {"label": "{g}"}),
    (3, 0, {"label": "{h}"}),
    (1, 2, {"label": "{i}"}),
    (3, 2, {"label": "{j}"})
])

# https://q.uiver.app/#q=WzAsNixbMCwyLCIwIl0sWzEsMiwiMSJdLFsyLDIsIjIiXSxbMCwxLCIzIl0sWzEsMCwiNCJdLFsyLDEsIjUiXSxbMCwxLCJmIiwyXSxbMSwyLCJnIiwyXSxbMCwzLCJoIl0sWzMsNCwiaiJdLFs0LDUsImsiXSxbNSwyLCJsIl0sWzMsNSwiaSIsMl1d
HOUSE = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (0, 3, {"label": "{h}"}),
    (3, 5, {"label": "{i}"}),
    (3, 4, {"label": "{j}"}),
    (4, 5, {"label": "{k}"}),
    (5, 2, {"label": "{l}"})
])

# https://q.uiver.app/#q=WzAsOCxbMCwxLCIwIl0sWzEsMSwiMSJdLFsyLDEsIjMiXSxbMywxLCI0Il0sWzEsMiwiMiJdLFsyLDAsIjUiXSxbNCwxLCI3Il0sWzMsMiwiNiJdLFswLDEsImYiXSxbMSwyLCJnIl0sWzIsMywiaCJdLFswLDQsImkiLDJdLFs0LDIsImoiLDJdLFsxLDUsImsiXSxbNSwzLCJsIl0sWzMsNiwibSJdLFsyLDcsIm4iLDJdLFs3LDYsIm8iLDJdXQ==
DOUBLY_STAGGERED = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 3, {"label": "{g}"}),
    (3, 4, {"label": "{h}"}),
    (0, 2, {"label": "{i}"}),
    (2, 3, {"label": "{j}"}),
    (1, 5, {"label": "{k}"}),
    (5, 4, {"label": "{l}"}),
    (4, 7, {"label": "{m}"}),
    (3, 6, {"label": "{n}"}),
    (6, 7, {"label": "{o}"})
])

# https://q.uiver.app/#q=WzAsNyxbMCwwLCIwIl0sWzEsMiwiMiJdLFswLDEsIjEiXSxbMSwxLCIzIl0sWzEsMCwiNCJdLFsyLDEsIjUiXSxbMiwwLCI2Il0sWzAsMiwiZiIsMl0sWzIsMSwiZyIsMl0sWzAsMywiaCJdLFszLDEsImkiXSxbMCw0LCJqIl0sWzQsMywiayJdLFszLDUsImwiXSxbNSwxLCJtIl0sWzYsNCwibiIsMl0sWzYsNSwicCJdXQ==
INTRO_EXFIG = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (0, 3, {"label": "{h}"}),
    (3, 2, {"label": "{i}"}),
    (0, 4, {"label": "{j}"}),
    (4, 3, {"label": "{k}"}),
    (3, 5, {"label": "{l}"}),
    (5, 2, {"label": "{m}"}),
    (6, 4, {"label": "{n}"}),
    (6, 5, {"label": "{p}"}),
])

# https://q.uiver.app/#q=WzAsNCxbMCwxLCIwIl0sWzEsMCwiMSJdLFsxLDEsIjIiXSxbMSwyLCIzIl0sWzAsMSwiZiJdLFswLDIsImciLDJdLFswLDMsImgiLDJdLFsxLDIsImkiXSxbMiwzLCJqIl1d
BIG_CYCLE_TRIANGLES = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (0, 2, {"label": "{g}"}),
    (0, 3, {"label": "{h}"}),
    (1, 2, {"label": "{i}"}),
    (2, 3, {"label": "{j}"})
])

# https://q.uiver.app/#q=WzAsNyxbMSwwLCIwIl0sWzAsMSwiMSJdLFswLDIsIjIiXSxbMSwxLCIzIl0sWzEsMywiNCJdLFsyLDEsIjUiXSxbMiwyLCI2Il0sWzEsMiwiZyIsMl0sWzIsMywiaCIsMl0sWzIsNCwiaSIsMl0sWzAsNSwiaiJdLFs1LDYsImsiXSxbNiwzLCJsIl0sWzYsNCwibSJdLFswLDEsImYiLDJdXQ==
BULKY_DIAMOND = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (2, 3, {"label": "{h}"}),
    (2, 4, {"label": "{i}"}),
    (0, 5, {"label": "{j}"}),
    (5, 6, {"label": "{k}"}),
    (6, 3, {"label": "{l}"}),
    (6, 4, {"label": "{m}"})
])

# https://q.uiver.app/#q=WzAsOCxbMSwwLCIwIl0sWzAsMSwiMSJdLFswLDIsIjIiXSxbMSwxLCIzIl0sWzEsMywiNCJdLFsyLDEsIjUiXSxbMiwyLCI2Il0sWzEsNCwiNyJdLFsxLDIsImciLDJdLFsyLDMsImgiLDJdLFsyLDQsImkiXSxbMCw1LCJqIl0sWzUsNiwiayJdLFs2LDMsImwiXSxbNiw0LCJtIiwyXSxbMCwxLCJmIiwyXSxbMiw3LCJuIiwyXSxbNiw3LCJwIl1d
BULKIER_DIAMOND = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (2, 3, {"label": "{h}"}),
    (2, 4, {"label": "{i}"}),
    (0, 5, {"label": "{j}"}),
    (5, 6, {"label": "{k}"}),
    (6, 3, {"label": "{l}"}),
    (6, 4, {"label": "{m}"}),
    (2, 7, {"label": "{n}"}),
    (6, 7, {"label": "{p}"})
])

CYCLE = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (2, 0, {"label": "{h}"})
])

# https://q.uiver.app/#q=WzAsNSxbMCwxLCIwIl0sWzEsMCwiMSJdLFsyLDEsIjIiXSxbMSwxLCIzIl0sWzEsMiwiNCJdLFswLDEsImYiXSxbMSwyLCJnIl0sWzAsMywiaCIsMl0sWzMsMiwiaSIsMl0sWzAsNCwiaiIsMl0sWzQsMiwiayIsMl1d
THREE_BRANCHES = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (0, 3, {"label": "{h}"}),
    (3, 2, {"label": "{i}"}),
    (0, 4, {"label": "{j}"}),
    (4, 2, {"label": "{k}"})
])

# https://q.uiver.app/#q=WzAsNyxbMCwwLCIwIl0sWzEsMCwiMSJdLFsxLDEsIjIiXSxbMCwxLCIzIl0sWzIsMSwiNCJdLFsyLDIsIjUiXSxbMSwyLCI2Il0sWzAsMSwiZiJdLFsxLDIsImciXSxbMCwzLCJoIiwyXSxbMywyLCJpIiwyXSxbMiw0LCJqIiwyXSxbNCw1LCJrIiwyXSxbMiw2LCJsIiwyXSxbNiw1LCJtIiwyXV0=
FIG_8 = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (0, 3, {"label": "{h}"}),
    (3, 2, {"label": "{i}"}),
    (2, 4, {"label": "{j}"}),
    (4, 5, {"label": "{k}"}),
    (2, 6, {"label": "{l}"}),
    (6, 5, {"label": "{m}"})
])
# https://q.uiver.app/#q=WzAsNSxbMSwwLCIwIl0sWzAsMCwiMSJdLFswLDEsIjIiXSxbMSwxLCIzIl0sWzIsMSwiNCJdLFswLDEsImYiLDJdLFsxLDIsImciLDJdLFsyLDMsImgiLDJdLFszLDAsImkiLDJdLFszLDQsImoiLDJdLFs0LDAsImwiLDJdXQ==
WEDGE = nx.DiGraph([
    (0, 1, {"label": "{f}"}),
    (1, 2, {"label": "{g}"}),
    (2, 3, {"label": "{h}"}),
    (3, 0, {"label": "{i}"}),
    (3, 4, {"label": "{j}"}),
    (4, 0, {"label": "{k}"})
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
        self.assertEquals(txt, Converter.lists_to_latex_matrix(lst))

    def test_two_three(self):
        lst = [
            ["A", "B", "C"],
            ["D", "E", "F"]
        ]
        txt = "A & B & C \\\\ D & E & F"
        self.assertEquals(txt, Converter.lists_to_latex_matrix(lst))

    def test_three_two(self):
        lst = [
            ["A", "B"],
            ["C", "D"],
            ["E", "F"]
        ]
        txt = "A & B \\\\ C & D \\\\ E & F"
        self.assertEquals(txt, Converter.lists_to_latex_matrix(lst))

    def test_uncompleted(self):
        lst = [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G"]
        ]
        txt = "A & B & C \\\\ D & E & F \\\\ G"
        self.assertEquals(txt, Converter.lists_to_latex_matrix(lst))


class TestExtractLabel(unittest.TestCase):
    def test_extract_label_basic(self):
        test_str_basic: str = '{A}'
        self.assertEquals(('{A}', 3), Converter.extract_label(test_str_basic, 1))

    def test_extract_label_repeat(self):
        test_str_repeat: str = '{A}{B}'
        self.assertEquals(('{A}', 3), Converter.extract_label(test_str_repeat, 1))

    def test_extract_label_brackets(self):
        test_str_interior_brackets: str = '{\\mathbf{I}^{\\mathscal{A}}_{X,Y}}'
        self.assertEquals(('{\\mathbf{I}^{\\mathscal{A}}_{X,Y}}', 33),
                          Converter.extract_label(test_str_interior_brackets, 1))

    def test_extract_label_complex(self):
        test_str_complex: str = '{[\\mathscal{A}^{\\op},X](-,-)}{H_{A}}'
        self.assertEquals(('{[\\mathscal{A}^{\\op},X](-,-)}', 29), Converter.extract_label(test_str_complex, 1))

    def test_extract_label_empty(self):
        test_str_empty: str = '{}{A}'
        self.assertEquals(('{}', 2), Converter.extract_label(test_str_empty, 1))

    def test_extract_label_complex_file(self):
        line1 = ["{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{B}}{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{"
                 "A}}{1 \\times G}",
                 "{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{A}}{1 \\times G}",
                 "{1 \\times G}"]
        self.assertEquals("{\\mathscr{A}^{\\mathrm{op}} \\times \\mathscr{B}}", Converter.extract_label(line1[0], 1)[0])


class TestToLatex(unittest.TestCase):
    def test_exfig(self):
        parser = Converter()
        parser.graph = nx.DiGraph([("A", "B", {"label": "f"}),
                                   ("A", "C", {"label": "g"}),
                                   ("B", "C", {"label": "h"}),
                                   ("D", "B", {"label": "i"}),
                                   ("D", "C", {"label": "j"})
                                   ])
        print(parser.to_tikz_diagram())


class TestToDiagramRepresentation(unittest.TestCase):
    def test_exfig(self):
        parser = Converter()
        parser.graph = nx.DiGraph([("A", "B", {"label": "f"}),
                                   ("A", "C", {"label": "g"}),
                                   ("B", "C", {"label": "h"}),
                                   ("D", "B", {"label": "i"}),
                                   ("D", "C", {"label": "j"})
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
        parser = Converter()
        parser.graph = nx.DiGraph([("A", "B", {"label": "f"}),
                                   ("A", "C", {"label": "g"}),
                                   ("B", "C", {"label": "h"}),
                                   ("D", "B", {"label": "i"}),
                                   ("D", "C", {"label": "j"})
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
    def can_graph_be_reconstructed(self, graph: nx.DiGraph):
        parser = Converter()
        parser.graph = graph
        representation = parser.to_morphism_representation()
        with open('temp.txt', 'w') as f:
            f.write(representation)
        morph_parser = MorphismParser('temp.txt')
        print(representation)
        self.assertTrue(nx.is_isomorphic(parser.graph, morph_parser.graph))

        print("\ndual:")
        parser = Converter()
        parser.graph = nx.reverse(graph)
        representation = parser.to_morphism_representation()
        with open('temp.txt', 'w') as f:
            f.write(representation)
        morph_parser = MorphismParser('temp.txt')
        print(representation)
        self.assertTrue(nx.is_isomorphic(parser.graph, morph_parser.graph))

    def test_bridge(self):
        self.can_graph_be_reconstructed(BRIDGE)

    def test_goggles(self):
        self.can_graph_be_reconstructed(GOGGLES)

    def test_stagger(self):
        self.can_graph_be_reconstructed(STAGGERED)

    def test_doubly_stagger(self):
        self.can_graph_be_reconstructed(DOUBLY_STAGGERED)

    def test_non_comp_morphs(self):
        parser = Converter()
        parser.graph = nx.DiGraph([
            (0, 1, {"label": "{f}"}),
            (1, 2, {"label": "{g}"})
        ])
        self.assertEquals(parser.to_morphism_representation(), "{g}{f}")

    def test_limit(self):
        self.can_graph_be_reconstructed(LIMIT_DEF)

    def test_bulky_diamond(self):
        parser = Converter()
        parser.graph = BULKY_DIAMOND
        representation = parser.to_morphism_representation()
        with open('temp.txt', 'w') as f:
            f.write(representation)
        print(representation)
        morph_parser = MorphismParser('temp.txt')
        self.assertTrue(nx.is_isomorphic(parser.graph, morph_parser.graph))

    def test_bulky_diamond_dual(self):
        parser = Converter()
        parser.graph = nx.reverse(BULKY_DIAMOND)
        representation = parser.to_morphism_representation()
        with open('temp.txt', 'w') as f:
            f.write(representation)
        print(representation)
        morph_parser = MorphismParser('temp.txt')
        self.assertTrue(nx.is_isomorphic(parser.graph, morph_parser.graph))

    def test_big_cycle_triangles(self):
        self.can_graph_be_reconstructed(BIG_CYCLE_TRIANGLES)

    def test_bulkier_diamond(self):
        self.can_graph_be_reconstructed(BULKIER_DIAMOND)

    def test_cycle(self):
        parser = Converter()
        parser.graph = CYCLE
        representation = parser.to_morphism_representation()
        with open('temp.txt', 'w') as f:
            f.write(representation)
        print(representation)
        morph_parser = MorphismParser('temp.txt')
        self.assertTrue(nx.is_isomorphic(parser.graph, morph_parser.graph))

    def test_three_branches(self):
        self.can_graph_be_reconstructed(THREE_BRANCHES)

    def test_fig_8(self):
        self.can_graph_be_reconstructed(FIG_8)

    def test_example_fig(self):
        self.can_graph_be_reconstructed(EXAMPLE_FIG)

    def test_house(self):
        self.can_graph_be_reconstructed(HOUSE)

    def test_intro_exfig(self):
        self.can_graph_be_reconstructed(INTRO_EXFIG)

    def test_wedge_example(self):
        self.can_graph_be_reconstructed(WEDGE)
