from math import ceil, sqrt
from typing import Any

import networkx as nx


class Parser:
    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()

    def get_graph(self) -> nx.DiGraph:
        return self.graph

    @staticmethod
    def extract_label(line: str, start_pos: int) -> tuple[str, int]:
        """
        Extracts the label attached to a domain, codomain, or function in the commutative diagram text representation.
        :param line: line of text containing the label, should be of the form ``"some text{Label}some more text"``.
        :param start_pos: the position of the first character of the Label.
        :return: ``({Label},`` the position of the closing "``}``"``)``
        """
        unmatched_brackets: int = 1  # we should always start with an unmatched bracket
        i: int = start_pos
        while unmatched_brackets != 0:
            if line[i] == "{":
                unmatched_brackets += 1
            elif line[i] == "}":
                unmatched_brackets -= 1
            i += 1
        return line[start_pos - 1:i], i  # the start position is just after the opening {, so we need to decrement

    @staticmethod
    def lists_to_latex_matrix(lst: list[list[Any]]) -> str:
        """
        Converts a matrix represented by a list of lists to the LaTeX representation of a matrix.
        :param lst: a list of lists representing a matrix. Each sub-list should be of equal length.
        :return: A string representing ``lst`` as a latex matrix
        """
        rows = [""] * len(lst)
        i = 0
        for line in lst:
            rows[i] = " & ".join(list(map(str, line)))
            i += 1
        return " \\\\ ".join(rows)

    def place_nodes(self) -> list[list[str]]:
        """
        Positions all the nodes of the graph stored in ``self.graph`` in a matrix.
        :return: a list of lists containing all the labels of the nodes, and potentially some empty strings
        """
        # TODO: better algo
        nodes = self.graph.nodes
        matrix_size: int = ceil(sqrt(len(nodes)))
        ob_matrix: list[list[str]] = [[""] * matrix_size for _ in range(matrix_size)]
        line: int = 0
        col: int = 0
        for node in nodes:
            ob_matrix[line][col] = node
            col = (col + 1) % matrix_size
            if col == 0:
                line += 1
        return ob_matrix

    def to_codi(self) -> str:
        node_matrix = self.place_nodes()
        num_latex_lines = 1 + len(self.graph.edges)
        latex = [""] * num_latex_lines  # each element is a line in LaTeX
        latex_matrix = self.lists_to_latex_matrix(node_matrix)
        latex[0] = "\\obj {" + latex_matrix + "};"
        i = 1
        for edge in self.graph.edges.data():
            latex[i] = f"\\mor {edge[0]} %s:-> {edge[1]};" % edge[2]["name"]
            i += 1
        return "\n".join(latex)

    def path_to_func_comp(self, path: list[tuple]):
        """
        Converts a list of function domain and codomains to the equivalent composition of functions.
        :param path: a list of 2-tuples, containing the domain then codomain of a function in the diagram.
        :return: the function composition equivalent to the path.
        """
        funcs = [""] * len(path)
        i = 0
        for edge in reversed(path):
            funcs[i] = self.graph.get_edge_data(edge[0], edge[1]).get("name")
            i += 1
        return "".join(funcs)

    def to_func_comps(self) -> str:
        """
        :return: a representation of the composed functions that are equal to each other
        """
        # The do
        # noinspection PyCallingNonCallable
        domains = [node for node in self.graph.nodes if self.graph.out_degree(node) > 1]
        # noinspection PyCallingNonCallable
        codomains = [node for node in self.graph.nodes if self.graph.in_degree(node) > 1]

        eqs = []
        for domain in domains:
            for codomain in codomains:
                funcs = []
                paths: list[list[tuple]] = list(nx.algorithms.all_simple_edge_paths(self.graph, domain, codomain))
                if len(paths) <= 1:
                    continue
                for path in paths:
                    if not path:
                        continue
                    funcs.append(self.path_to_func_comp(path))
                eqs.append(" = ".join(funcs))
        return "\n".join(eqs)
