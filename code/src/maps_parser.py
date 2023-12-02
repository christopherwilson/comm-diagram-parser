import networkx as nx

from src.parser import Parser


class MapsParser(Parser):
    def __init__(self, file_path: str):
        super().__init__()
        self.funcs = {}
