from math import ceil, sqrt
from typing import Any, Set
from collections import deque

import networkx as nx


class Parser:
    def __init__(self):
        self.unvisited_nodes = set()
        self.comp_morph_chains: dict[Any, dict[Any, list[list[Any]]]] = {}
        self.comp_morph_eqs: dict[tuple[Any, Any], list[str]] = {}
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

    def to_tikz_diagram(self):
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
    def old_to_morphism_representation(self) -> str:
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
                self.search_for_eq_comp_morphs(node, [], [], set())

        return self.convert_comp_morphs()

    def convert_comp_morphs(self) -> str:
        data = []
        for start_node in self.comp_morph_chains:
            for end_node in self.comp_morph_chains[start_node]:
                line = []
                composed_morphs = self.comp_morph_chains[start_node][end_node]
                if len(composed_morphs) > 1:
                    for composed_morph in composed_morphs:
                        # traversing array backwards
                        str_composed_morph = ""
                        for i in range(-1, -len(composed_morph), -1):
                            domain = composed_morph[i - 1]
                            codomain = composed_morph[i]
                            morphism = self.graph.edges[domain, codomain]['name']
                            str_composed_morph += morphism
                        line.append(str_composed_morph)
                data.append(" = ".join(line))
        return "\n".join(data)

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
                self.store_path(domain, curr_node, path[domain_pos:])
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
                for i in range(len(prev_domains) - 1, -1, -1):
                    prev_domain = prev_domains[i][0]
                    found_existing_path = (prev_domain in self.comp_morph_chains
                                           and adj_node in self.comp_morph_chains[prev_domain])
                    prev_domain_pos = prev_domains[i][1]
                    path_to = path[prev_domain_pos:]
                    path_to.append(adj_node)
                    self.store_path(prev_domain, adj_node, path_to)
                    if found_existing_path:
                        break

                if "codomain_children" not in self.graph.nodes[curr_node]:
                    self.graph.nodes[curr_node]['codomain_children'] = {}

                for codomain in self.graph.nodes[adj_node]['codomain_children']:
                    if codomain not in self.graph.nodes[curr_node]['codomain_children']:
                        future_path = self.graph.nodes[adj_node]['codomain_children'][codomain]
                        new_path = [curr_node] + future_path
                        self.store_path(curr_node, codomain, new_path)
                        self.graph.nodes[curr_node]['codomain_children'][codomain] = new_path

    def store_path(self, domain, codomain, path):
        if domain in self.comp_morph_chains.keys():
            domain_dict = self.comp_morph_chains[domain]
            if codomain in domain_dict.keys():
                domain_dict[codomain].append(path)
            else:
                domain_dict[codomain] = [path]
        else:
            self.comp_morph_chains[domain] = {codomain: [path]}

    def store_eq(self, domain, codomain, eq: str):
        key = (domain, codomain)
        if key in self.comp_morph_eqs:
            self.comp_morph_eqs[key].append(eq)
        else:
            self.comp_morph_eqs[key] = [eq]

    def to_morphism_representation(self) -> str:
        nx.set_edge_attributes(self.graph, False, "is_added")
        cycle_basis = self.find_undirected_cycle_basis()
        if isinstance(cycle_basis[0], list):
            for cycle in cycle_basis:
                cycle_graph = nx.subgraph(self.graph, cycle)
                self.parse_cycle(cycle_graph)
        else:
            cycle_graph = nx.subgraph(self.graph, cycle_basis)
            self.parse_cycle(cycle_graph)

        data = []
        for key in self.comp_morph_eqs:
            line = " = ".join(self.comp_morph_eqs[key])
            data.append(line)
        return "\n".join(data)

    def find_undirected_cycle_basis(self) -> list[list] | list:
        undirected_graph = nx.Graph(self.graph)
        return nx.minimum_cycle_basis(undirected_graph)

    def parse_cycle(self, cycle_graph: nx.DiGraph) -> None:
        source = self.find_source(cycle_graph)
        if source is not None:
            self.split_cycle(cycle_graph, source)
        else:  # if we don't find a source the cycle is a cycle in the digraph
            edges = list(cycle_graph.edges())
            inv_edge = edges[0]
            domain = inv_edge[1]
            codomain = inv_edge[0]
            self.store_eq(domain, codomain, f"-{self.graph.edges[inv_edge]['name']}")
            curr_domain = codomain
            curr_codomain = next(cycle_graph.neighbors(curr_domain))
            path = [self.graph.edges[curr_domain, curr_codomain]['name']]
            while curr_codomain != codomain:
                curr_domain = curr_codomain
                curr_codomain = next(cycle_graph.neighbors(curr_domain))
                path.append(self.graph.edges[curr_domain, curr_codomain]['name'])
            eq = "".join(reversed(path))
            self.store_eq(domain, codomain, eq)

    @staticmethod
    def find_source(cycle: nx.DiGraph):
        for node in cycle.nodes:
            if cycle.out_degree[node] == 2:
                return node

    def split_cycle(self, subgraph: nx.DiGraph, domain):
        # first branch
        neighbors = list(subgraph.neighbors(domain))
        assert len(neighbors) == 2
        path = [self.graph.edges[domain, neighbors[0]]["name"]]
        curr_codomain = neighbors[0]
        while subgraph.in_degree[curr_codomain] != 2:
            curr_domain = curr_codomain
            curr_codomain = next(subgraph.neighbors(curr_domain))
            path.append(self.graph.edges[curr_domain, curr_codomain]["name"])
        codomain = curr_codomain
        self.store_eq(domain, codomain, "".join(reversed(path)))

        # second branch
        curr_domain = domain
        curr_codomain = neighbors[1]
        path = [self.graph.edges[curr_domain, curr_codomain]["name"]]
        inverted = False
        graphs: list[nx.DiGraph] = [subgraph, None]
        curr_graph = 0
        while curr_codomain != codomain:
            if graphs[curr_graph].in_degree[curr_codomain] == 2:
                inverted = not inverted
                curr_graph = (curr_graph + 1) % 2
                # we avoid reversing the graph unless required
                if graphs[curr_graph] is None:
                    graphs[curr_graph] = nx.reverse(subgraph)
                prev_domain = curr_domain
                curr_domain = curr_codomain
                for node in graphs[curr_graph].neighbors(curr_domain):
                    if node != prev_domain:
                        curr_codomain = node
                        break

            else:
                curr_domain = curr_codomain
                curr_codomain = next(graphs[curr_graph].neighbors(curr_domain))
            if inverted:
                path.append(f"-{graphs[curr_graph].edges[curr_domain, curr_codomain]['name']}")
            else:
                path.append(graphs[curr_graph].edges[curr_domain, curr_codomain]['name'])
        self.store_eq(domain, codomain, "".join(reversed(path)))

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
