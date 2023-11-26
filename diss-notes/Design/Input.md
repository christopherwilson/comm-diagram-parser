A path to a `.txt` file. The `.txt` should follow the following language.
# Language
## Base
```
S -> MNS | M
N -> \n
M -> {L}{L}{L} | {L}{L}
L -> LaTeX
```

Key:
- M = Map, first `{L}` is the Domain, second is the Codomain, and the final is the label of the map. This is optional.
- N = newline, probably could just throw this in N but ¯\\\_(ツ)\_/¯ 
- L = Name of the object/map in LaTeX. I'm going to just treat this as a string, and hope it works, may add checks if there's a good semi-easy way of doing this.

## Extended
May add option to alter arrow types and others. 

# Parsing
Given a file-path of a `.txt` file containing our input language we want to produce a graph. Iterate through each line, extract labels, store in graph.