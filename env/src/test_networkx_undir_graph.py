#!/usr/bin/env python

import math
import networkx as nx
import matplotlib.pyplot as plt

myGraph = nx.Graph();
pos = {'A': (0,0), 'B': (1,0), 'C': (2,0.5), 'D': (2,-1), 'E': (2.5,-0.5), 'F': (3.1,-0.75)};
myGraph.add_nodes_from(pos.keys());
myGraph.add_edges_from([('A','B'),('B','C'),('B','D'),('D','E'),('C','E'),('E','F'),('C','F')]);
for i, p in pos.items():
    myGraph.node[i]['pos'] = p;
for node1,node2 in myGraph.edges():
    dist = math.sqrt(math.pow(pos[node2][0]-pos[node1][0],2) + math.pow(pos[node2][1]-pos[node1][1],2));
    myGraph[node1][node2]['weight'] = dist;
print("\nNodes");
print(myGraph.nodes(data=True));
print("\nEdges");
print(myGraph.edges(data=True));

startnode = 'A'; endnode = 'F'
best_route = nx.dijkstra_path(myGraph,startnode,endnode)
best_route_edges = []; prevnode = startnode;
for i in best_route:
    if (i!=startnode):
        if (i,prevnode) in myGraph.edges():
            best_route_edges.append((i,prevnode)) 
        elif (prevnode,i) in myGraph.edges():
            best_route_edges.append((prevnode,i))
        else:
            print("Could not find edge "+(prevnode,i))
    prevnode = i;

edge_colors = ['black' if not i in best_route_edges else 'red' for i in myGraph.edges()]
nx.draw(myGraph,pos,edge_color=edge_colors);
nx.draw_networkx_labels(myGraph,pos,font_size=12,font_family='sans-serif')
plt.show();