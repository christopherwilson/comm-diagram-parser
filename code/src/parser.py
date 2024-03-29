import heapq
from collections import deque
from math import ceil, sqrt
from typing import Any

import networkx as nx


class Parser:
    def __init__(self):
        self.cycles: dict[int, tuple[nx.DiGraph, set, set]] = {}  # (graph, sources, sinks)
        self.comp_morph_eqs: dict[tuple[Any, Any], set[str]] = {}
        self.graph: nx.DiGraph = nx.DiGraph()
        self.branches: dict[Any: list[tuple[Any, tuple[Any, str], tuple[Any, str]]]] = {}

    @staticmethod
    def extract_label(line: str, start_pos: int) -> tuple[str, int]:
        """
        Extracts the label attached to a domain, codomain, or function in the commutative diagram text representation.
        :param line: line of text containing the label, should be of the form ``"some text{Label}some more text"``.
        :param start_pos: the position of the first character of the Label.
        :return: tuple of the form ``({Label},`` the position of the closing "``}``"+1``)``
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

    def store_eq(self, domain, codomain, eq: str):
        key = (domain, codomain)
        if key in self.comp_morph_eqs:
            self.comp_morph_eqs[key].add(eq)
        else:
            self.comp_morph_eqs[key] = {eq}

    def to_morphism_representation(self) -> str:
        self.comp_morph_eqs = {}
        graph = self.graph.reverse()

        rep = []

        sources = set()
        sinks = set()
        sorted_sources = []
        for node in graph.nodes:
            # all possible domains/codomains of our equations will have more than one in or out edge
            # noinspection PyCallingNonCallable
            if graph.in_degree(node) > 1:
                sinks.add(node)
            # noinspection PyCallingNonCallable
            if graph.out_degree(node) > 1:
                sources.add(node)
                sorted_sources.append((graph.out_degree(node), node))

        sorted_sources.sort()

        while sorted_sources:
            _, source = sorted_sources.pop()
            if "visited" in self.graph.nodes(source):
                continue
            self.modified_bfs(graph, source)

        return "\n".join(rep)

    def modified_bfs(self, graph: nx.DiGraph, source):
        q = deque([source])
        graph.nodes(source)["path_to"] = [source]
        graph.nodes(source)["path_pos"] = 0
        while q:
            node = q.popleft()
            path_to = graph.nodes(node)["path_to"]
            for neighbour in graph.neighbors(node):
                if "visited" in graph.nodes(neighbour):
                    continue
                else:
                    graph.nodes(neighbour)["visited"] = True
                    q.append(neighbour)

    def all_paths_method(self, graph, rep, sinks, sources):
        sorted_paths = []
        paths = {}
        path_id = 0
        num_paths_between = {}
        for source in sources:
            for sink in sinks:
                # we deal with cycles later
                if source == sink:
                    continue
                for path in nx.algorithms.all_simple_edge_paths(graph, source, sink):
                    # we only care about sorting the first value, but if we leave the path in heapq will try to sort
                    # the tuple based off the entire path if the length is the same, which will involve traversing the
                    # path so to stop this we use an id.
                    if not path or len(path) == 0:
                        continue
                    heapq.heappush(sorted_paths, (len(path), path_id))
                    paths[path_id] = path
                    path_id += 1
                    if (source, sink) in num_paths_between:
                        num_paths_between[(source, sink)] += 1
                    else:
                        num_paths_between[(source, sink)] = 1
        redundant_keys = set()
        good_comp_morphs = {}
        while sorted_paths:  # is not empty
            morphs = []
            _, path_id = heapq.heappop(sorted_paths)
            path = paths[path_id]
            start_node = path[0][0]
            end_node = path[-1][1]
            if (start_node, end_node) in redundant_keys or num_paths_between[(start_node, end_node)] == 1:
                continue
            curr_non_cannon_paths = {}
            is_redundant = False
            for edge in path:
                morphs.append(graph.edges[edge]["name"])
                if "non-cannon_paths" in graph.edges[edge]:
                    for (key, pos, is_end) in graph.edges[edge]["non-cannon_paths"]:
                        # ensure this is the next in chain
                        if key in curr_non_cannon_paths:
                            prev_pos = curr_non_cannon_paths[key]
                            if prev_pos + 1 != pos:
                                curr_non_cannon_paths.pop(key, None)
                                continue
                        elif pos == 0:
                            curr_non_cannon_paths[key] = pos
                        else:
                            continue
                        # can only reach this point if we've seen every edge in a non-cannon path
                        if is_end:
                            is_redundant = True
                            curr_non_cannon_paths.pop(key, None)
                            path_start, path_end = key
                            if path_start == start_node or path_end == end_node:
                                if num_paths_between[(start_node, end_node)] == num_paths_between[key]:
                                    redundant_keys.add((start_node, end_node))
                                    good_comp_morphs.pop((start_node, end_node), None)
                            if num_paths_between[key] == 1:
                                good_comp_morphs.pop(key, None)
                            break
                if is_redundant:
                    break
            if is_redundant:
                continue
            comp_morph = "".join(morphs)
            if (start_node, end_node) in good_comp_morphs:
                # then this is not the cannon edge
                good_comp_morphs[(start_node, end_node)].append(comp_morph)
                i = 0
                for edge in path:
                    entry = ((start_node, end_node), i, i == len(path) - 1)
                    if "non-cannon_paths" in graph.edges[edge]:
                        graph.edges[edge]["non-cannon_paths"].add(entry)
                    else:
                        graph.edges[edge]["non-cannon_paths"] = {entry}
                    i += 1
            else:
                good_comp_morphs[(start_node, end_node)] = [comp_morph]
        for key in good_comp_morphs:
            rep.append(" = ".join(good_comp_morphs[key]))
        cycles = nx.simple_cycles(graph)
        for cycle in cycles:
            morph = []
            for i in range(len(cycle)):
                domain = cycle[i - 1]
                codomain = cycle[i]
                morph.append(graph.edges[domain, codomain]["name"])
            morph = "".join(morph)
            rep.append(f"{morph} = {morph}{morph}")

    @staticmethod
    def path_to_morph_comp(graph: nx.DiGraph, path: list[tuple]):
        """
        Converts a list of function domain and codomains to the equivalent composition of functions.
        :param graph: the graph storing the morphisms
        :param path: a list of 2-tuples, containing the domain then codomain of a function in the diagram.
        :return: the function composition equivalent to the path.
        """
        funcs = [""] * len(path)
        i = 0
        for edge in reversed(path):
            funcs[i] = graph.get_edge_data(edge[0], edge[1]).get("name")
            i += 1
        return "".join(funcs)

    def condense_graph(self, graph: nx.DiGraph):
        for node in list(graph.nodes):
            # noinspection PyCallingNonCallable
            is_removable = graph.in_degree(node) == 1 and graph.out_degree(node) == 1
            if is_removable:
                domain = list(graph.in_edges(node))[0][0]
                codomain = list(graph.out_edges(node))[0][1]
                # stops the removal of cycles or the creation of self-loops
                if domain == codomain or (codomain, domain) in graph.edges:
                    continue
                concatenated_morph = graph[node][codomain]["name"] + graph[domain][node]["name"]
                if (domain, codomain) in graph.edges:
                    self.store_eq(domain, codomain, concatenated_morph)
                    self.store_eq(domain, codomain, graph[domain][codomain]["name"])
                else:
                    graph.add_edge(domain, codomain, name=concatenated_morph)
                graph.remove_node(node)

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
                        label_lines.append(f"L{{{str(obj)}}}{{{str(label)}}}")

            name = self.graph[edge[0]][edge[1]]['name']
            morph_lines.append(f"{{{str(name)}}}{{{edge[0]}}}{{{edge[1]}}}")

        return "\n".join(label_lines + morph_lines)
