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
                        self.contract_domain(domain, new_domain)
                        domain = new_domain
                    if next_morph in self.morphs.keys():
                        if self.morphs[morph][1] != self.morphs[next_morph][0]:
                            new_next_domain = self.morphs[morph][1]
                            old_next_domain = self.morphs[next_morph][0]
                            self.contract_domain(old_next_domain, new_next_domain)
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
                    self.contract_domain(codomain, new_codomain)
                    codomain = new_codomain
                else:
                    continue
            else:
                self.update_dicts(morph, prev_obj, codomain)
                self.graph.add_edge(prev_obj, codomain, name=morph)

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

    def contract_domain(self, domain, new_domain):
        # ensure we have a spot for the new_domain in lists
        if new_domain not in self.morphs_by_domain:
            self.morphs_by_domain[new_domain] = []
        if new_domain not in self.morphs_by_codomain:
            self.morphs_by_codomain[new_domain] = []
        nx.contracted_nodes(self.graph, new_domain, domain, copy=False)
        if domain in self.morphs_by_domain.keys():
            for adjusted_morph in self.morphs_by_domain.pop(domain):
                self.morphs_by_domain[new_domain].append(adjusted_morph)
                prev_codomain = self.morphs[adjusted_morph][1]
                self.morphs[adjusted_morph] = (new_domain, prev_codomain)
        if domain in self.morphs_by_codomain.keys():
            for adjusted_morph in self.morphs_by_codomain.pop(domain):
                self.morphs_by_codomain[new_domain].append(adjusted_morph)
                prev_domain = self.morphs[adjusted_morph][0]
                self.morphs[adjusted_morph] = (prev_domain, new_domain)

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

# class MapsParserOld(Parser):
#     funcs: dict[str, tuple[Any, Any]]
#
#     def __init__(self, file_path: str):
#         super().__init__()
#         self.max_domain = 0
#         self.max_codomain = 1
#         self.funcs = {}
#         eq_heads, parsed_file = self.parse_file(file_path)
#         #  while eq_heads is not empty
#         while eq_heads:
#             length, line_num, composed_func_ls = heapq.heappop(eq_heads)
#             if parsed_file[line_num]:
#                 head = heapq.heappop(line_num)
#                 heapq.heappush(eq_heads, head)
#             domain = self.max_domain
#             codomain = self.max_codomain
#             for i in range(length - 1):
#                 func = composed_func_ls[i]
#
#     def parse_file(self, file_path):
#         parsed_file = []
#         eq_heads = []
#         with open(file_path, 'r') as file:
#             i = 0
#             for line in file:
#                 parsed_file.append([])
#                 parsed_comp_funcs, domain, codomain = self.parse_line(line, i)
#                 if domain == self.max_domain:
#                     self.max_domain += 2
#                 if codomain == self.max_codomain:
#                     self.max_codomain += 2
#                 for composed_func in parsed_comp_funcs:
#                     func_list = composed_func[2]
#                     if len(func_list) == 1:
#                         if func_list[0] not in self.funcs.keys():
#                             self.graph.add_edge(domain, codomain, name=func_list[0])
#                             self.funcs[func_list[0]] = (domain, codomain)
#                     elif len(func_list) == 2:
#                         if func_list[0] in self.funcs.keys():
#                             if func_list[1] not in self.funcs.keys():
#                                 temp_codomain = self.funcs[func_list[0]][0]
#                                 self.graph.add_edge(domain, temp_codomain, name=func_list[1])
#                                 self.funcs[func_list[1]] = (domain, temp_codomain)
#                         elif func_list[1] in self.funcs.keys():
#                             temp_domain = self.funcs[func_list[1]][1]
#                             self.graph.add_edge(temp_domain, codomain, name=func_list[0])
#                             self.funcs[func_list[0]] = (temp_domain, codomain)
#                         else:
#                             self.graph.add_edge(domain, self.max_codomain, name=func_list[1])
#                             self.funcs[func_list[1]] = (domain, self.max_codomain)
#
#                             self.graph.add_edge(self.max_codomain, codomain, name=func_list[0])
#                             self.funcs[func_list[0]] = (self.max_codomain, codomain)
#                             self.max_codomain += 2
#                     else:
#                         if func_list[0] not in self.funcs.keys():
#                             self.graph.add_edge(self.max_domain, codomain, name=func_list[0])
#                             self.funcs[func_list[0]] = (self.max_domain, codomain)
#                             self.max_domain += 2
#                         if func_list[-1] not in self.funcs.keys():
#                             self.graph.add_edge(domain, self.max_codomain, name=func_list[-1])
#                             self.funcs[func_list[-1]] = (domain, self.max_codomain)
#                             self.max_codomain += 2
#                         parsed_file[i].append(composed_func)
#                 if parsed_file[i]:
#                     heapq.heapify(parsed_file[i])
#                     heapq.heappush(eq_heads, heapq.heappop(parsed_file[i]))
#                 i += 1
#         return eq_heads, parsed_file
#
#     def parse_line(self, line: str, line_num: int):
#         domain = self.max_domain
#         codomain = self.max_codomain
#         i = 0
#         parsed_line = []
#         composed_funcs = []
#         is_first_func = True
#         while i < len(line):
#             if line[i] == "%":
#                 break
#             elif line[i] == "{":
#                 func, i = super().extract_label(line, i + 1)
#                 if is_first_func and func in self.funcs.keys():
#                     # TODO check if we have a contradictory (co)domains?
#                     codomain = self.funcs[func][1]
#                     is_first_func = False
#                 composed_funcs.append(func)
#                 continue  # we already have a new value for 'i' so don't need to increment
#             elif line[i] == "=":
#                 try:
#                     # noinspection PyUnboundLocalVariable
#                     func  # raises error if func is undefined, which only happens if a line reads "= some more text"
#                 except NameError:
#                     raise Exception("Error: = found before function")
#                 if func in self.funcs.keys():
#                     domain = self.funcs[func][0]
#                 parsed_line.append((len(composed_funcs), line_num, composed_funcs))
#                 composed_funcs = []
#                 is_first_func = True
#             i += 1
#         try:
#             # noinspection PyUnboundLocalVariable
#             func  # raises error if func is undefined, which only happens if a line reads "= some more text"
#         except NameError:
#             raise Exception("Error: = found before function")
#         if func in self.funcs.keys():
#             domain = self.funcs[func][0]
#         parsed_line.append((len(composed_funcs), line_num, composed_funcs))
#         return parsed_line, domain, codomain
