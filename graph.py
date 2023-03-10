import random
import json
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# import scraped data
f = open('scraped_data.json')
data = json.load(f)
f.close()

# create adjacency matrix from data -- businesses that have the same owners/reg. agents/comm. reg. agents will be considered adjacent
for j, company_rows in enumerate(data.values()):
    row = np.array([])
    for i, company_columns in enumerate(data.values()):
        # make sure nodes are not adjacent to themselves
        if(i==j):
            row = np.append(row,[0])
        else:
            if (np.in1d(company_rows["Name"],company_columns["Name"]).any()):
                row = np.append(row,[1])
            else:
                row = np.append(row,[0])
    if(j==0):
        adjacency_matrix = np.array([row])
    else:
        adjacency_matrix = np.vstack([adjacency_matrix, row])

# create graph from adjacency matrix
g = nx.from_numpy_array(adjacency_matrix)

# layout graphs with positions using graphviz neato
pos = nx.nx_agraph.graphviz_layout(g, prog="neato")

# color nodes the same in each connected subgraph, except for subgraphs consisting of a single node -- they will all have the same color
for subg_set in nx.connected_components(g):
    subg = g.subgraph(subg_set)
    if(nx.number_of_nodes(subg)==1):
        c = .1
    else:
        # generate random number between ..6 and 1 so colors will not be similar to subgraphs with just 1 node
        c = [((random.random()*.6)+.4)] * nx.number_of_nodes(subg)  # random color...
    nx.draw(subg, pos, node_size=40, node_color=c, vmin=0.0, vmax=1.0, with_labels=False)
    
plt.show()
