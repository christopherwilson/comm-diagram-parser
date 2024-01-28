from src.parser import Parser


class DiagramParser(Parser):

    def __init__(self, file_path: str):
        """
        Parses a representation of a commutative diagram.

        Each line of the commutative diagram representation should represent a function in the diagram, and be of
        the form::

            {Function}{Domain}{Codomian}

        For example; the function ``f: A -> B`` should be represented by::

            {f}{A}{B}

        ``Domain``, ``Codomain`` and ``Function`` cannot be the empty string, but they may contain \"{\" and \"}\".
        :param file_path: Location of the text representation of the commutative diagram.
        """
        super().__init__()
        with open(file_path, 'r') as f:
            line = f.readline()
            self.labels: dict[str, str] = {}
            self.seen_objs = set()
            while line[0] == 'L':
                self.parse_label_line(line)
                line = f.readline()
            self.parse_map_line(line)
            for line in f:
                if line[0] == "%":  # lets us comment
                    continue
                self.parse_map_line(line)

    def parse_map_line(self, line: str):
        objs = [""] * 3
        num_objs = 0
        i = 0
        while i < len(line):
            c: str = line[i]  # iterate through each character
            if c == "{":
                if num_objs <= 3 and line[i + 1] == "}":
                    raise Exception("Object labels cannot be empty")
                obj, i = self.extract_label(line, i + 1)
                objs[num_objs] = obj
                num_objs += 1
                # if obj is an object and not a map label
                if num_objs > 1:
                    self.add_node(obj)
            if num_objs == 3:
                break
        self.graph.add_edge(objs[1], objs[2], name=objs[0])

    def add_node(self, obj):
        # applying labels to objects (if they aren't already in the graph)
        if obj not in self.seen_objs:
            # is there a label assigned to this object
            if obj in self.labels:
                label = self.labels[obj]
            else:
                label = obj
            self.graph.add_node(obj, label=label)
            self.seen_objs.add(obj)

    def parse_label_line(self, line: str):
        self.verify_char_is_open_bracket(1, line)
        obj, i = self.extract_label(line, 2)
        self.verify_char_is_open_bracket(i, line)
        label, _ = self.extract_label(line, i + 1)
        self.labels[obj] = label

    @staticmethod
    def verify_char_is_open_bracket(i, line):
        if line[i] != "{":
            raise Exception("Unexpected Character\n" + line + '-' * i + '^')
