import unittest

from src.maps_parser import MapsParser


class TestParseLine(unittest.TestCase):
    def test_basic(self):
        line = "{h}{f} = {g}"
        expected = [
            (1, 1, ["{g}"]),
            (2, 1, ["{h}", "{f}"])
        ]
        parser = MapsParser("testfiles/blank.txt")
        result = parser.parse_line(line, 1, 0, 1)
        self.assertEquals(expected, result[0])
        self.assertEquals(0, result[1])
        self.assertEquals(1, result[2])

    def test_domain_change(self):
        line = "{h}{f} = {g}"
        parser = MapsParser("testfiles/blank.txt")
        parser.funcs["{f}"] = (2, 3)
        result = parser.parse_line(line, 1, 0, 1)[1]
        self.assertEquals(2, result)

    def test_codomain_change(self):
        line = "{h}{f} = {g}"
        parser = MapsParser("testfiles/blank.txt")
        parser.funcs["{h}"] = (2, 3)
        result = parser.parse_line(line, 1, 0, 1)[2]
        self.assertEquals(3, result)


if __name__ == '__main__':
    unittest.main()
