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
        self.comp_morph_paths: dict[Any, dict[Any, list[list[Any]]]] = {}

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
        """
        Positions nodes of graph naively in a grid structure.
        """
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

    def __store_comp_morph(self, domain, codomain, comp_morph: str):
        """
        Stores a composed morphism going from domain to codomain is self.comp_morph_eqs
        :param domain: the vertex representing the domain of the composed morphism
        :param codomain: the vertex representing the codomain of the composed morphism
        :param comp_morph: the composed morphism
        """
        key = (domain, codomain)
        if key in self.comp_morph_eqs:
            self.comp_morph_eqs[key].add(comp_morph)
        else:
            self.comp_morph_eqs[key] = {comp_morph}

    def to_morphism_representation(self) -> str:
        self.comp_morph_eqs = {}
        graph = self.graph.reverse()

        rep = set()

        possible_starts = []
        for node in graph.nodes:
            if graph.out_degree[node] > 1 or graph.in_degree[node] == 0:
                possible_starts.append((graph.in_degree[node], node))
            graph.nodes[node]["visited_from"] = set()

        possible_starts.sort()

        for _, source in possible_starts:
            if "visited" in graph.nodes[source]:
                continue
            self.__search_for_eq_comp_morphs(graph, source, [], [], set())

        composition_lines = []
        self.__parse_paths(composition_lines, graph, rep)

        self.__find_links(composition_lines, graph, rep)

        return "\n".join(rep)

    def __search_for_eq_comp_morphs(self, graph: nx.DiGraph, curr_node: Any, path: list[Any],
                                    prev_sources: list[tuple[Any, int]], prev_sinks: set[tuple[Any, int]]):
        node_pos = len(path)
        path.append(curr_node)
        graph.nodes[curr_node]["visited"] = True
        is_source = graph.out_degree[curr_node] > 1 or graph.in_degree[curr_node] == 0
        is_sink = graph.in_degree[curr_node] > 1 or graph.out_degree[curr_node] == 0

        if is_sink:
            graph.nodes[curr_node]['codomain_children']: dict[Any, list[Any]] = {}
            for domain, domain_pos in prev_sources:
                self.__store_path(domain, curr_node, path[domain_pos:], graph)
            for codomain, codomain_pos in prev_sinks:
                graph.nodes[codomain]['codomain_children'][curr_node] = path[codomain_pos:]
            prev_sinks = prev_sinks.copy()
            prev_sinks.add((curr_node, node_pos))

        if is_source:
            prev_sources.append((curr_node, node_pos))

        for adj_node in graph.adj[curr_node]:
            if "visited" not in graph.nodes[adj_node]:
                branch_path = path.copy()
                self.__search_for_eq_comp_morphs(graph, adj_node, branch_path, prev_sources.copy(), prev_sinks)
            else:
                for prev_domain, prev_domain_pos in reversed(prev_sources):
                    found_existing_path = (prev_domain in self.comp_morph_paths
                                           and adj_node in self.comp_morph_paths[prev_domain])
                    path_to = path[prev_domain_pos:]
                    path_to.append(adj_node)
                    self.__store_path(prev_domain, adj_node, path_to, graph)
                    if found_existing_path:
                        break

                if "codomain_children" not in graph.nodes[curr_node]:
                    graph.nodes[curr_node]['codomain_children'] = {}

                for prev_codomain, prev_codomain_pos in prev_sinks:
                    if adj_node in graph.nodes[prev_codomain]["codomain_children"]:
                        continue
                    path_to = path[prev_codomain_pos:]
                    path_to.append(adj_node)
                    graph.nodes[prev_codomain]["codomain_children"][adj_node] = path_to

                for codomain in graph.nodes[adj_node]['codomain_children']:
                    future_path = graph.nodes[adj_node]['codomain_children'][codomain]
                    new_path = [curr_node] + future_path
                    self.__store_path(curr_node, codomain, new_path, graph)
                    graph.nodes[curr_node]['codomain_children'][codomain] = new_path

    def __parse_paths(self, composition_lines, graph, rep):
        for source in self.comp_morph_paths:
            for sink in self.comp_morph_paths[source]:
                eqs: set[str] = self.comp_morph_eqs[(source, sink)]
                paths = self.comp_morph_paths[source][sink]
                if len(eqs) > 1:
                    rep.add(" = ".join(self.comp_morph_eqs[(source, sink)]))
                    for path in paths:
                        for i in range(len(path) - 1):
                            domain = path[i]
                            codomain = path[i + 1]
                            edge_data = graph.edges[domain, codomain]
                            if "line_keys" in edge_data:
                                edge_data["line_keys"].add((source, sink))
                            else:
                                edge_data["line_keys"]: set = {(source, sink)}
                elif len(eqs) == 1:
                    composition_lines.append((source, sink))

    def __find_links(self, composition_lines, graph, rep):
        for source, sink in composition_lines:
            path = self.comp_morph_paths[source][sink][0]
            prev_edge = (path[0], path[1])
            if "line_keys" not in graph.edges[prev_edge]:
                graph.edges[prev_edge]["line_keys"] = set()
            prev_line_keys: set = graph.edges[prev_edge]["line_keys"]
            links = []
            prev_was_link = False
            for i in range(1, len(path) - 1):
                curr_edge = (path[i], path[i + 1])
                if "line_keys" not in graph.edges[curr_edge]:
                    graph.edges[curr_edge]["line_keys"] = set()
                curr_line_keys: set = graph.edges[curr_edge]["line_keys"]
                if prev_line_keys.isdisjoint(curr_line_keys):
                    if prev_was_link:
                        links.append(curr_edge)
                    else:
                        links.append([prev_edge, curr_edge])
                        graph.edges[prev_edge]["line_keys"].add((source, sink))
                    graph.edges[curr_edge]["line_keys"].add((source, sink))
                    prev_was_link = True
                else:
                    prev_was_link = False
                prev_edge = curr_edge
                prev_line_keys = curr_line_keys
            for link_path in links:
                morphs = []
                for edge in link_path:
                    morphs.append(graph.edges[edge]["name"])
                rep.add("".join(morphs))

    def __find_paths_from_source(self, graph: nx.DiGraph, source):
        q = deque([source])
        graph.nodes[source]["path_to"] = [source]
        graph.nodes[source]["prev_sources"] = []
        while q:
            node = q.popleft()
            path_to = graph.nodes[node]["path_to"]
            prev_sources = graph.nodes[node]["prev_sources"].copy()
            if graph.out_degree[node] >= 2:
                prev_sources.append(len(path_to) - 1)
            for neighbour in graph.neighbors(node):
                if "visited" in graph.nodes[neighbour] and source in graph.nodes[neighbour]["visited"]:
                    is_sink = True
                else:
                    if "visited" in graph.nodes[neighbour]:
                        graph.nodes[neighbour]["visited"].add(source)
                    else:
                        graph.nodes[neighbour]["visited"] = {source}
                    is_sink = graph.in_degree[neighbour] >= 2 or graph.out_degree[neighbour] == 0
                    graph.nodes[neighbour]["path_to"] = path_to.copy()
                    graph.nodes[neighbour]["path_to"].append(neighbour)
                    graph.nodes[neighbour]["prev_sources"] = prev_sources
                    q.append(neighbour)
                if is_sink:
                    for prev_source_pos in reversed(prev_sources):
                        prev_source = path_to[prev_source_pos]
                        alt_path_exists = (prev_source in self.comp_morph_paths
                                           and neighbour in self.comp_morph_paths[prev_source])
                        self.__store_path(prev_source, neighbour, path_to[prev_source_pos:] + [neighbour], graph)
                        if alt_path_exists:
                            break

    def __store_path(self, domain, codomain, path, graph):
        if domain in self.comp_morph_paths.keys():
            domain_dict = self.comp_morph_paths[domain]
            if codomain in domain_dict.keys():
                domain_dict[codomain].append(path)
            else:
                domain_dict[codomain] = [path]
        else:
            self.comp_morph_paths[domain] = {codomain: [path]}
        morphs = []
        for i in range(len(path)-1):
            edge = [path[i], path[i+1]]
            morphs.append(graph.edges[edge]["name"])
        comp_morph = "".join(morphs)
        if (domain, codomain) not in self.comp_morph_eqs:
            self.comp_morph_eqs[(domain, codomain)] = {comp_morph}
        else:
            self.comp_morph_eqs[(domain, codomain)].add(comp_morph)

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
                # if this edge is part of a non-cannon path
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
            rep.append(f"{morph}")

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

    def __condense_graph(self, graph: nx.DiGraph):
        """
        Contracts any in_degree == 1, out_degree == 1 edge of the graph into a single edge
        :param graph: graph to contract
        """
        for node in list(graph.nodes):
            is_removable = graph.in_degree[node] == 1 and graph.out_degree[node] == 1
            if is_removable:
                domain = list(graph.in_edges(node))[0][0]
                codomain = list(graph.out_edges(node))[0][1]
                # stops the removal of cycles or the creation of self-loops
                if domain == codomain or (codomain, domain) in graph.edges:
                    continue
                concatenated_morph = graph[node][codomain]["name"] + graph[domain][node]["name"]
                if (domain, codomain) in graph.edges:
                    self.__store_comp_morph(domain, codomain, concatenated_morph)
                    self.__store_comp_morph(domain, codomain, graph[domain][codomain]["name"])
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
        """
        Converts stored graph into the diagram representation
        :return: the diagram representation as a string
        """
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
