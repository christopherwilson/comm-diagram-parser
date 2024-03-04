```
to_compositions():
    domains = [all nodes with > 1 out degree]
    codomains = [all nodes with > 1 in degree]
    unvisited nodes = [all nodes]
    sort domains by ascending in degree
    for domain not in unvisited nodes:
	    search_from(domain)

search_from(curr_node):
	for node adjacent to curr_node:
		if node not in unvisted nodes:
			branched = False
			if node in codomains:
				
```