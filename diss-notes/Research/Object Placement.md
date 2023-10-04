This basically means minimising the intersections of edges in a graph (a Graph Theory graph). For non-planar graphs this is NP-hard ~~Why didn't I save the source for this???~~.        

[The wikipedia page for "Graph Drawing", may contain useful things to reference.](https://en.wikipedia.org/wiki/Graph_drawing)

[This is a linear-time algorithm for embedding a planar graph on a grid with no intersections.](https://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=3A013A211737A56256D8A895B937DBDF?doi=10.1.1.51.6677&rep=rep1&type=pdf) Can I cut a graph into two or three planar graphs? Then I can offset the embeddings and create a "3d" diagram. Embedding on a grid is good, most "professional looking" commutative diagrams are on some kind of grid and most latex packages use a matrix for positioning - also can be a grid. I already know [Kuratowski's theorem](https://www.math.cmu.edu/~mradclif/teaching/228F16/Kuratowski.pdf), so theoretically can determine if a graph is planar.     


https://www.mdpi.com/books/book/5135 could have some stuff, read if have time.       

https://www.oreilly.com/library/view/advanced-algorithms-and/9781617295485/OEBPS/Text/ch15.htm Covers 
- Embedding graphs on a 2-D plane
- Discussing algorithms to find out if a graph is planar
- Defining minimum crossing number for non-planar graphs
- Implementing algorithms to detect crossing edges
All useful, need account to access though. :(

# **GOOD PAPER** 
https://cs.brown.edu/people/rtamassi/papers/gdbiblio.pdf     
Contains citations for graph drawing algorithm papers for multiple types of graphs :D
Are commutative diagrams often cyclic?
