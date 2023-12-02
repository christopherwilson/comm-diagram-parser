import heapq
from typing import Dict, Any

import networkx as nx

from src.parser import Parser


class MapsParser(Parser):
    funcs: dict[str, tuple[Any, Any]]

    def __init__(self, file_path: str):
        super().__init__()
        self.funcs = {}

    def parse_line(self, line: str, line_num: int, domain, codomain):
        i = 0
        parsed_line = []
        composed_funcs = []
        is_first_func = True
        while i < len(line):
            if line[i] == "%":
                break
            elif line[i] == "{":
                func, i = super().extract_label(line, i+1)
                if is_first_func and func in self.funcs.keys():
                    # TODO check if we have a contradictory domain
                    codomain = self.funcs[func][1]
                    is_first_func = False
                composed_funcs.append(func)
                continue  # we already have a new value for 'i' so don't need to increment
            elif line[i] == "=":
                try:
                    # noinspection PyUnboundLocalVariable
                    func  # raises error if func is undefined, which only happens if a line reads "= some more text"
                except NameError:
                    raise Exception("Error: = found before function")
                if func in self.funcs.keys():
                    domain = self.funcs[func][0]
                parsed_line.append((len(composed_funcs), line_num, composed_funcs))
                composed_funcs = []
                is_first_func = True
            i += 1
        try:
            # noinspection PyUnboundLocalVariable
            func  # raises error if func is undefined, which only happens if a line reads "= some more text"
        except NameError:
            raise Exception("Error: = found before function")
        if func in self.funcs.keys():
            domain = self.funcs[func][0]
        parsed_line.append((len(composed_funcs), line_num, composed_funcs))
        heapq.heapify(parsed_line)
        return parsed_line, domain, codomain
