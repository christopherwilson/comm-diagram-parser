import os
from typing import Any

import networkx as nx

from src.converter import Converter


class MorphismParser(Converter):
    morphs: dict[str, tuple[Any, Any]]
    morphs_by_domain: dict[int, list[str]]
    morphs_by_codomain: dict[int, list[str]]

    def __init__(self, filepath: str):
        """
        Parses a file containing a representation of a list of morphisms.

        Each line of the file should be of the form::

            {function 1}{function 2}{function 3} = {function 4}{function 5}


        :param filepath: the path to the file containing the representation
        """
        super().__init__()
        if not os.path.isfile(filepath):
            raise FileNotFoundError("No such file: " + filepath)
        self.counter = 0
        self.morphs: dict[str, tuple[int, int]] = {}
        self.morphs_by_domain: dict[str, list[str]] = {}
        self.morphs_by_codomain: dict[str, list[str]] = {}
        with open(filepath, 'r') as file:
            for line in file:
                self.parse_line(line)

    def add_edge(self, morph, domain, codomain):
        # dealing with graph
        self.graph.add_edge(domain, codomain, label=morph)
        self.graph.nodes[domain]['label'] = "$\\bullet$"
        self.graph.nodes[codomain]['label'] = "$\\bullet$"

        # dealing with dicts
        # if morph in self.morphs it's in the relevant dicts, so don't bother adding it
        if morph not in self.morphs:
            # checking if I need to initialise the list of morphs or just add to it
            if domain in self.morphs_by_domain:
                self.morphs_by_domain[domain].append(morph)
            else:
                self.morphs_by_domain[domain] = [morph]
            if codomain in self.morphs_by_codomain:
                self.morphs_by_codomain[codomain].append(morph)
            else:
                self.morphs_by_codomain[codomain] = [morph]
            self.morphs[morph] = (domain, codomain)

    def contract_objects(self, old_obj, new_obj):
        """
        Takes every morphism going into/out of ``obj``, and makes the morphism go into/out of ``new_obj``, then
        deletes ``obj``.
        :param old_obj:
        :param new_obj:
        """
        # ensure we have a spot for the new_obj in lists
        if new_obj not in self.morphs_by_domain:
            self.morphs_by_domain[new_obj] = []
        if new_obj not in self.morphs_by_codomain:
            self.morphs_by_codomain[new_obj] = []

        # contract objects
        nx.contracted_nodes(self.graph, new_obj, old_obj, copy=False)
        self.graph.nodes[new_obj]['label'] = "$\\bullet$"
        if old_obj in self.morphs_by_domain.keys():
            for adjusted_morph in self.morphs_by_domain.pop(old_obj):
                self.morphs_by_domain[new_obj].append(adjusted_morph)
                prev_codomain = self.morphs[adjusted_morph][1]
                self.morphs[adjusted_morph] = (new_obj, prev_codomain)
        if old_obj in self.morphs_by_codomain.keys():
            for adjusted_morph in self.morphs_by_codomain.pop(old_obj):
                self.morphs_by_codomain[new_obj].append(adjusted_morph)
                prev_domain = self.morphs[adjusted_morph][0]
                self.morphs[adjusted_morph] = (prev_domain, new_obj)

    def parse_line(self, line: str):
        i = 0
        domain = self.counter
        codomain = self.counter + 1
        self.counter += 2
        while i < len(line):
            char = line[i]
            if char == "%":
                break
            if char == "{":
                i, domain, codomain = self.parse_composed_morph(line, i, domain, codomain)
            else:
                i += 1

    def parse_composed_morph(self, line: str, start_pos: int, domain: int, codomain: int):
        i = start_pos
        prev_domain = codomain
        prev_morph = ""
        is_initial = True
        # if we encounter the end of the line or an = we know chain has ended
        while i < len(line) and line[i] != "=" and line[i] != "%":
            if line[i] == "{":
                prev_domain, i, prev_morph, assigned_codomain = self.process_morph(i, line, prev_domain)
                # updating codomain if it's been contracted into a different vertex
                if is_initial and assigned_codomain != codomain:
                    codomain = assigned_codomain
                is_initial = False
            else:
                i += 1
        if prev_morph in self.morphs:
            old_domain = self.morphs[prev_morph][0]
            if old_domain != domain:
                # finding the vertex with the least amount of edges to contract
                old_domain_degree = self.graph.in_degree[old_domain] + self.graph.out_degree[old_domain]
                if domain in self.graph.nodes:
                    domain_degree = self.graph.in_degree[domain] + self.graph.out_degree[domain]
                    if old_domain_degree <= domain_degree:
                        self.contract_objects(old_domain, domain)
                    else:
                        self.contract_objects(domain, old_domain)
                        domain = old_domain
                # if domain isn't already a vertex, we just need to override it with the existing vertex
                else:
                    domain = old_domain
        return i, domain, codomain

    def process_morph(self, pos, line, prev_domain):
        morph, pos = self.extract_label(line, pos + 1)
        if morph in self.morphs:
            curr_domain, morph_codomain = self.morphs[morph]
            # if the domains already match we don't have a problem, if they don't we need to merge the nodes
            if morph_codomain != prev_domain:
                degree_morph_codomain = self.graph.in_degree[morph_codomain] + self.graph.out_degree[morph_codomain]
                if prev_domain in self.graph.nodes:
                    degree_prev_domain = self.graph.in_degree[prev_domain] + self.graph.out_degree[prev_domain]
                    if degree_prev_domain < degree_morph_codomain:
                        self.contract_objects(prev_domain, morph_codomain)
                        prev_domain = morph_codomain
                    else:
                        self.contract_objects(morph_codomain, prev_domain)
                else:
                    prev_domain = morph_codomain
        else:
            # if we haven't seen the morphism before we need to assign it a codomain
            curr_domain = self.counter
            self.counter += 1
        self.add_edge(morph, curr_domain, prev_domain)
        return curr_domain, pos, morph, prev_domain
