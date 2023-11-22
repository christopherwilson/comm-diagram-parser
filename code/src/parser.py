from typing import Any

from networkx import DiGraph
from math import ceil, sqrt


class Parser:

    def __init__(self, file_path: str):
        self.graph: DiGraph = DiGraph()
        with (open(file_path, 'r') as f):
            labels = [""] * 3
            for line in f:
                num_labels: int = 0
                labels[2] = ""  # clearing the maps name
                for i in range(len(line)):
                    c: str = line[i]  # iterate through each character
                    if c == " ":
                        continue
                    elif c == "{":
                        if num_labels <= 2 and line[i + 1] == "}":
                            raise Exception("Object labels cannot be empty")
                        labels[num_labels], i = self.extract_label(line, i + 1)
                        num_labels += 1
                        if num_labels > 3:
                            break
                    # TODO: add error handling for unexpected characters
                self.graph.add_edge(labels[0], labels[1], name=labels[2])

    def get_graph(self) -> DiGraph:
        return self.graph

    @staticmethod
    def extract_label(line: str, start_pos: int) -> tuple[str, int]:
        unmatched_brackets: int = 0
        i: int = start_pos
        while not (unmatched_brackets == 0 and line[i] == "}"):
            if line[i] == "{":
                unmatched_brackets += 1
            elif line[i] == "}":
                unmatched_brackets -= 1
            i += 1
        return line[start_pos:i], i

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
