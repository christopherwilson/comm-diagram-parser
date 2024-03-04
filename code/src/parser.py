from math import ceil, sqrt
from typing import Any, Set
from collections import deque

import networkx as nx


class Parser:
    def __init__(self):
        self.unvisited_nodes = set()
        self.comp_func_chains: dict[Any, dict[Any, list[list[Any]]]] = {}
        self.links: list[list[Any]] = []
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

    def to_node_matrix(self) -> list[list[str]]:
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
            col += 1
            if col == matrix_size:
                col = 0
                line += 1
        return ob_matrix

    def to_latex(self):
        self.position_nodes()
        return nx.to_latex_raw(self.graph, edge_label="name", edge_label_options="opt", node_label="label")

    def position_nodes(self):
        # TODO better algo
        num_cols = ceil(sqrt(len(self.graph.nodes)))
        x = 0
        y = 0
        for node in self.graph.nodes:
            self.graph.nodes[node]["pos"] = (x * 2, y * 2)
            x += 1
            if x == num_cols:
                x = 0
                y -= 1
        for edge in self.graph.edges:
            self.graph.edges[edge]["opt"] = "[auto]"

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

    # noinspection PyCallingNonCallable
    def to_morphism_representation(self) -> str:
        """
        :return: a representation of the composed functions that are equal to each other
        """
        domains = []
        codomains = set()
        # preparing nodes
        for node in self.graph.nodes:
            self.graph.nodes[node]['visited_from']: set = set()
            self.unvisited_nodes.add(node)
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            if out_degree > 1:
                domains.append((in_degree, node))
            if in_degree > 1:
                codomains.add(node)
        domains = sorted(domains)
        for _, node in domains:
            if node in self.unvisited_nodes:
                self.search_for_eq_comp_morphs(node, [], [])

    def search_for_eq_comp_morphs(self, curr_node: Any, path: list[Any], prev_domains: list[tuple[Any, int]],
                                  prev_codomains: set[tuple[Any, int]]):
        node_pos = len(path)
        path.append(curr_node)
        self.unvisited_nodes.remove(curr_node)
        is_domain = self.graph.out_degree[curr_node] > 1
        is_codomain = self.graph.in_degree[curr_node] > 1

        if is_codomain:
            self.graph.nodes[curr_node]['codomain_children']: dict[Any, list[Any]] = {}
            for domain, domain_pos in prev_domains:
                self.store_chain(domain, curr_node, path[domain_pos:])
            for codomain, codomain_pos in prev_codomains:
                self.graph.nodes[codomain]['codomain_children'][curr_node] = path[codomain_pos:]
            prev_codomains = prev_codomains.copy()
            prev_codomains.add((curr_node, node_pos))

        if is_domain:
            prev_domains.append((curr_node, node_pos))

        for adj_node in self.graph.adj[curr_node]:
            if adj_node in self.unvisited_nodes:
                branch_path = path.copy()
                self.search_for_eq_comp_morphs(adj_node, branch_path, prev_domains.copy(), prev_codomains)

            else:
                for i in range(len(prev_domains)-1, -1, -1):
                    prev_domain = prev_domains[i][0]
                    found_existing_path = (prev_domain in self.comp_func_chains
                                           and adj_node in self.comp_func_chains[prev_domain])
                    prev_domain_pos = prev_domains[i][1]
                    path_to = path[prev_domain_pos:]
                    path_to.append(adj_node)
                    self.store_chain(prev_domain, adj_node, path_to)
                    if found_existing_path:
                        break

                if "codomain_children" not in self.graph.nodes[curr_node]:
                    print(curr_node)
                    self.graph.nodes[curr_node]['codomain_children'] = {}

                for codomain in self.graph.nodes[adj_node]['codomain_children']:
                    if codomain not in self.graph.nodes[curr_node]['codomain_children']:
                        future_path = self.graph.nodes[adj_node]['codomain_children'][codomain]
                        new_path = [curr_node] + future_path
                        self.store_chain(curr_node, codomain, new_path)
                        self.graph.nodes[curr_node]['codomain_children'][codomain] = new_path

    def store_chain(self, domain, codomain, path):
        if domain in self.comp_func_chains.keys():
            domain_dict = self.comp_func_chains[domain]
            if codomain in domain_dict.keys():
                domain_dict[codomain].append(path)
            else:
                domain_dict[codomain] = [path]
        else:
            self.comp_func_chains[domain] = {codomain: [path]}

    @staticmethod
    def verify_char_is_open_bracket(i, line):
        """
        Checks that the character at position i in the line is "{", raises an error if it is not
        :param i: the index of the character to be checked
        :param line: the line to be checked
        :return:
        """
        if line[i] != "{":
            raise Exception("Unexpected Character\n" + line + '-' * i + '^')

    def to_diagram_representation(self) -> str:
        label_lines = []
        morph_lines = []
        seen_objs = set()
        for edge in self.graph.edges():
            for obj in edge:
                if obj not in seen_objs:
                    seen_objs.add(obj)
                    if self.graph.nodes[obj]["label"] != obj:
                        label = self.graph.nodes[obj]["label"]
                        label_lines.append("L{" + str(obj) + "}{" + str(label) + "}")

            name = self.graph[edge[0]][edge[1]]['name']
            morph_lines.append("{" + str(name) + "}{" + edge[0] + "}{" + edge[1] + "}")

        return "\n".join(label_lines + morph_lines)
