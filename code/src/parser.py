from importlib.resources import path
from typing import Any

import networkx as nx
from math import ceil, sqrt


class Parser:


    def __init__(self, file_path: str):
        self.graph: nx.DiGraph = nx.DiGraph()
        with (open(file_path, 'r') as f):
            labels = [""] * 3
            num_labels = 3
            for line in f:
                if line[0] == "%":  # lets us comment
                    continue
                if num_labels < 3:
                    raise Exception("Invalid")
                num_labels = 0
                labels[2] = ""  # clearing the maps name
                j = 0
                for i in range(len(line)):
                    if i < j:
                        continue
                    c: str = line[i]  # iterate through each character
                    if c == "{":
                        if num_labels <= 3 and line[i + 1] == "}":
                            raise Exception("Object labels cannot be empty")
                        labels[num_labels], j = self.extract_label(line, i + 1)
                        num_labels += 1
                        if num_labels >= 3:
                            break
                    # TODO: add error handling for unexpected characters
                self.graph.add_edge(labels[0], labels[1], name=labels[2])

    def get_graph(self) -> nx.DiGraph:
        return self.graph

    @staticmethod
    def extract_label(line: str, start_pos: int) -> tuple[str, int]:
        unmatched_brackets: int = 1
        i: int = start_pos
        while unmatched_brackets != 0:
            if line[i] == "{":
                unmatched_brackets += 1
            elif line[i] == "}":
                unmatched_brackets -= 1
            i += 1
        return line[start_pos-1:i], i

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

    @staticmethod
    def lists_to_latex_matrix(lst: list[list[Any]]) -> str:
        matrix = [""] * (len(lst) * len(lst[0]))
        i = 0
        for line in lst:
            for col in range(len(line)):
                elem = line[col]
                if col == len(line) - 1:
                    matrix[i] = f"{elem} \\\\"
                    i += 1
                else:
                    matrix[i] = f"{elem} &"
                    i += 1
        return " ".join(matrix)

    def place_nodes(self) -> list[list[str]]:
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

    def to_func_comps(self):
        # noinspection PyCallingNonCallable
        doms = [node for node in self.graph.nodes if self.graph.out_degree(node) > 1]
        # noinspection PyCallingNonCallable
        codoms = [node for node in self.graph.nodes if self.graph.in_degree(node) > 1]

        eqs = []
        for dom in doms:
            for codom in codoms:
                funcs = []
                paths = list(nx.algorithms.all_simple_edge_paths(self.graph, dom, codom))
                if len(paths) <= 1:
                    continue
                for path in paths:
                    if not path:
                        continue
                    funcs.append(self.path_to_func_comp(path))
                eqs.append(" = ".join(funcs))
        return "\n".join(eqs)

    def path_to_func_comp(self, path: list[tuple]):
        funcs = [""]*len(path)
        i = 0
        for edge in reversed(path):
            funcs[i] = self.graph.get_edge_data(edge[0], edge[1]).get("name")
            i += 1
        return " o ".join(funcs)
