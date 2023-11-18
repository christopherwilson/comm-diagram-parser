from networkx import DiGraph


class Parser:

    def __init__(self, file_path: str):
        self.graph: DiGraph = DiGraph()
        with (open(file_path, 'r') as f):
            labels = [""] * 3
            for line in f:
                num_labels: int = 0
                labels[2] = ""  # clearing the maps name
                for i in range(len(line)):
                    c: str = line[i]
                    if c == " ":
                        continue
                    elif c == "{":
                        if num_labels <= 2 and line[i+1] == "}":
                            raise Exception("Object labels cannot be empty")
                        labels[num_labels] = self.extract_label(line, i + 1)
                        i += len(labels[num_labels])
                        num_labels += 1
                        if num_labels > 3:
                            break
                self.graph.add_edge(labels[0], labels[1], name=labels[2])

    def get_graph(self) -> DiGraph:
        return self.graph

    @staticmethod
    def extract_label(line: str, start_pos: int):
        unmatched_bracks: int = 0  # the number of unmatched opening brackets we've found
        i: int = start_pos
        while unmatched_bracks != 0 or line[i] != "}":
            if line[i] == "{":
                unmatched_bracks += 1
            elif line[i] == "}":
                unmatched_bracks -= 1
            i += 1
        return line[start_pos:i]
