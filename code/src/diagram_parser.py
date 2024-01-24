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
            labels = [""] * 3
            num_labels = 3
            for line in f:
                if line[0] == "%":  # lets us comment
                    continue
                if num_labels < 3:
                    raise Exception("Invalid number of labels")
                num_labels = 0
                labels[2] = ""  # clearing the maps name
                j = 0
                for i in range(len(line)):
                    if i < j:
                        continue
                    c: str = line[i]  # iterate through each character
                    if c == "{":
                        if num_labels <= 3 and line[i + 1] == "}":
                            raise Exception("Object labels cannot be empty")
                        labels[num_labels], j = self.extract_label(line, i + 1)
                        num_labels += 1
                        if num_labels >= 3:
                            break
                    # TODO: add error handling for unexpected characters
                self.graph.add_edge(labels[1], labels[2], name=labels[0])
                self.graph.nodes[labels[1]]['label'] = labels[1]
                self.graph.nodes[labels[2]]['label'] = labels[2]
