import os.path

from src.parser import Parser


class DiagramParser(Parser):

    def __init__(self, filepath: str):
        """
        Parses a file containing a representation of a commutative diagram.

        Each line of the representation should represent a morphism in the diagram, and be of
        the form::

            {Function}{Domain}{Codomian}

        For example; the function ``f: A -> B`` should be represented by::

            {f}{A}{B}

        An object in the diagram can have labels attached to them by including the line::

            L{Object}{Label}

        at the beginning of the file. These labels will be displayed in the diagram in place of the object.

        ``Domain``, ``Codomain`` and ``Function`` cannot be the empty string, but they may contain \"{\" and \"}\".
        :param filepath: Location of the text representation of the commutative diagram.
        """
        super().__init__()
        if not os.path.exists(filepath):
            raise FileNotFoundError("No such file or directory: " + filepath)
        with open(filepath, 'r') as f:
            line = f.readline()
            self.labelled_objs = set()
            while line[0] == 'L':
                self.__parse_label_line(line)
                line = f.readline()
            self.__parse_morph_line(line)
            for line in f:
                if line[0] == "%":  # lets us comment
                    continue
                self.__parse_morph_line(line)

    def __parse_morph_line(self, line: str):
        """
        Parses a line of the form::

            {Function}{Domain}{Codomian}


        :param line: the line to be parsed
        """
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
                    self.__label_node(obj)
            if num_objs == 3:
                break
        self.graph.add_edge(objs[1], objs[2], label=objs[0])

    def __label_node(self, obj):
        """
        Labels a node in the graph with either the assigned label or the name of the node if no label has been
        assigned. Will do nothing if the object has already been labelled.

        :param obj: the object/node to be labelled
        :return:
        """
        # if object is not labelled, must not have a label assigned so the label becomes an object.
        if obj not in self.labelled_objs:
            self.graph.add_node(obj, label=obj)
            self.labelled_objs.add(obj)

    def __parse_label_line(self, line: str):
        """
        Parses a line of the form::

            L{Object}{Label}

        :param line: the line to be parsed
        :return:
        """
        self.verify_char_is_open_bracket(1, line)
        obj, i = self.extract_label(line, 2)
        self.verify_char_is_open_bracket(i, line)
        label, _ = self.extract_label(line, i + 1)
        self.labelled_objs.add(obj)
        self.graph.add_node(obj, label=label)

