import unittest
from src.diagram_parser import DiagramParser


class TestLstsToLatex(unittest.TestCase):
    def test_sqr_two(self):
        lst = [
            [1, 2],
            [3, 4]
        ]
        txt = "1 & 2 \\\\ 3 & 4 \\\\"
        self.assertEquals(txt, DiagramParser.lists_to_latex_matrix(lst))

    def test_two_three(self):
        lst = [
            ["A", "B", "C"],
            ["D", "E", "F"]
        ]
        txt = "A & B & C \\\\ D & E & F \\\\"
        self.assertEquals(txt, DiagramParser.lists_to_latex_matrix(lst))

    def test_three_two(self):
        lst = [
            ["A", "B"],
            ["C", "D"],
            ["E", "F"]
        ]
        txt = "A & B \\\\ C & D \\\\ E & F \\\\"
        self.assertEquals(txt, DiagramParser.lists_to_latex_matrix(lst))

    def test_uncompleted(self):
        lst = [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G"]
        ]
        txt = "A & B & C \\\\ D & E & F \\\\ G \\\\  "
        self.assertEquals(txt, DiagramParser.lists_to_latex_matrix(lst))


if __name__ == '__main__':
    unittest.main()
