from typing import Any

import networkx as nx

from src.parser import Parser


class MorphismParser(Parser):
    morphs: dict[str, tuple[Any, Any]]
    morphs_by_domain: dict[int, list[str]]
    morphs_by_codomain: dict[int, list[str]]

    def __init__(self, filepath):
        super().__init__()
        self.counter = 0
        self.morphs = {}
        self.morphs_by_domain = {}
        self.morphs_by_codomain = {}
        with open(filepath, 'r') as file:
            for line in file:
                parsed_line = self.parse_line(line)
                self.process_line(parsed_line)

    def process_line(self, line: list[list[str]]):
        if line == [[]]:
            return
        domain = self.counter
        self.graph.add_node(domain)
        codomain = self.counter + 1
        self.graph.add_node(codomain)
        self.counter += 2
        for composed_morphs in line:
            if not composed_morphs:
                continue
            prev_obj = domain
            for i in range(1, len(composed_morphs)):
                # note we are traversing the array backwards
                morph = composed_morphs[-i]
                next_morph = composed_morphs[-(i + 1)]
                # if current morphism is known
                if morph in self.morphs.keys():
                    # if this is the first morphism in the chain
                    if i == 1 and self.morphs[morph][0] != domain:
                        new_domain = self.morphs[morph][0]
                        self.contract_objects(domain, new_domain)
                        domain = new_domain
                    if next_morph in self.morphs.keys():
                        if self.morphs[morph][1] != self.morphs[next_morph][0]:
                            new_next_domain = self.morphs[morph][1]
                            old_next_domain = self.morphs[next_morph][0]
                            self.contract_objects(old_next_domain, new_next_domain)
                            prev_obj = new_next_domain
                            continue
                    else:
                        prev_obj = self.morphs[morph][1]
                        continue
                # if this is a new morphism
                else:
                    if next_morph in self.morphs.keys():
                        # if the next morph is known, set the codomain of this morph to be the domain of the next
                        morph_codomain = self.morphs[next_morph][0]
                        self.graph.add_edge(prev_obj, morph_codomain, name=morph)
                        # filling in my dicts
                        self.update_dicts(morph, prev_obj, morph_codomain)
                        prev_obj = morph_codomain
                        continue
                    else:
                        self.update_dicts(morph, prev_obj, self.counter)
                        self.graph.add_edge(prev_obj, self.counter, name=morph)
                        prev_obj = self.counter
                        self.counter += 1
            # dealing with the final morphism
            morph = composed_morphs[0]
            if morph in self.morphs.keys():
                if self.morphs[morph][1] != codomain:
                    new_codomain = self.morphs[morph][1]
                    self.contract_objects(codomain, new_codomain)
                    codomain = new_codomain
                else:
                    continue
            else:
                self.update_dicts(morph, prev_obj, codomain)
                self.graph.add_edge(prev_obj, codomain, name=morph)

    @staticmethod
    def generate_label(node_index: int, min_num_chars: int) -> str:
        """
        Generates a label for a node based on its index. The label will be a string of capital letters representing a
        base-26 number, where each letter represents the number corresponding to the position of the letter in the
        English alphabet indexed from 0.

        For example: A == 0, Z == 25, BA == 26. (where the numbers on the right are base 10).

        If the number of characters needed to represent the string is less than ``min_num_chars`` then the returned
        label will be padded with ``A``s on the left of the number. As ``A`` represents zero this is equivalent to
        adding 0 to the left of the number, so AAAB = 0001.
        :param node_index: the index of the node we want a label for
        :param min_num_chars: the minimum number of characters we use to represent ``node_index``
        :return: a string of capital letters representing ``node_index`` in base 26.
        """
        label = chr(ord('A') + (node_index % 26))

        # using min_num_chars <= 1 instead of == 1 means we don't have to deal with cases where min_num_chars < 1,
        # which shouldn't occur in use anyway, but also probably won't be a problem if they do.
        if node_index < 26 and min_num_chars <= 1:
            return label
        else:
            return MorphismParser.generate_label(node_index // 26, min_num_chars - 1) + label

    def update_dicts(self, morph, domain, codomain):
        self.morphs[morph] = (domain, codomain)
        if domain in self.morphs_by_domain.keys():
            self.morphs_by_domain[domain].append(morph)
        else:
            self.morphs_by_domain[domain] = [morph]
        if codomain in self.morphs_by_codomain.keys():
            self.morphs_by_codomain[codomain].append(morph)
        else:
            self.morphs_by_codomain[codomain] = [morph]

    def contract_objects(self, obj, new_obj):
        """
        Takes every morphism going into/out of ``obj``, and makes the morphism go into/out of ``new_obj``, then
        deletes ``obj``.
        :param obj:
        :param new_obj:
        """
        # ensure we have a spot for the new_obj in lists
        if new_obj not in self.morphs_by_domain:
            self.morphs_by_domain[new_obj] = []
        if new_obj not in self.morphs_by_codomain:
            self.morphs_by_codomain[new_obj] = []

        # contract objects
        nx.contracted_nodes(self.graph, new_obj, obj, copy=False)
        if obj in self.morphs_by_domain.keys():
            for adjusted_morph in self.morphs_by_domain.pop(obj):
                self.morphs_by_domain[new_obj].append(adjusted_morph)
                prev_codomain = self.morphs[adjusted_morph][1]
                self.morphs[adjusted_morph] = (new_obj, prev_codomain)
        if obj in self.morphs_by_codomain.keys():
            for adjusted_morph in self.morphs_by_codomain.pop(obj):
                self.morphs_by_codomain[new_obj].append(adjusted_morph)
                prev_domain = self.morphs[adjusted_morph][0]
                self.morphs[adjusted_morph] = (prev_domain, new_obj)

    def parse_line(self, line: str):
        i = 0
        parsed_line = [[]]
        while i < len(line):
            char = line[i]
            if char == "%":
                break
            elif char == "{":
                morph, i = super().extract_label(line, i + 1)
                parsed_line[-1].append(morph)
                continue
            elif char == "=":
                parsed_line.append([])
            i += 1
        return parsed_line
