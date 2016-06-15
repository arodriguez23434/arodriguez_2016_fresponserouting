#!/usr/bin/env python

import networkx as nx
import matplotlib.pyplot as plt
import func_network_operations as nop

#--Configuration--
#nodeAttr: Key should be node name and the first two attributes must represent X and Y positions in the graph
#nodeNeighbors: Must be list of 2D tuples that are made of two node names in nodeAttr
#pathDesired: Must be a 2D tuple made of two node names in nodeAttr
nodeAttr = {'A': (0,0), 'B': (1,0), 'C': (2,0), 'E': (0,1)}
nodeNeighbors = [('A','B'),('B','C'),('A','E'),('C','E')]
pathDesired = ('A','C')
#TODO: Allow parameters for file I/O rather than manual entry
#TODO: Add check that nodeNeighbors are in nodeAttr for user error
#TODO: Add check that pathDesired is in nodeAttr for user error

#--Initialization--
#Create a position dictionary from first two attributes of user-defined dictionary
#Acts as input for NetworkX draw functions
nodePos = nodeAttr.fromkeys(nodeAttr.keys(),(0,0))
for key in nodeAttr: nodePos[key] = (nodeAttr[key][0],nodeAttr[key][1]);
#Set up the NetworkX graph object for output
outGraph = nx.Graph()
#The nodes are identified based on keys and have attributes added
outGraph.add_nodes_from(nodePos.keys())
for i, p in nodePos.items(): outGraph.node[i]['pos'] = p;
#Add all connecting neighbors as NetworkX edges
outGraph.add_edges_from(nodeNeighbors);
#Create a path matrix for the network
pathMatrix = nop.matrix_create(outGraph,nodeAttr);

#--Main Operating Block--

#Example for debugging: removing node 'C' then adding node 'D' and re-routing to there
pathMatrix = nop.network_remove_node('C',outGraph,nodeAttr,nodePos,pathMatrix)
pathMatrix = nop.network_add_node('D',(1,0.5),['B','E'],outGraph,nodeAttr,nodePos,pathMatrix)
pathDesired = ('A','D')

#Print out the nodes and edges for debugging purposes
print("\nNodes\n{0}\n\nEdges\n{1}\n".format(outGraph.nodes(data=True),outGraph.edges(data=True)))
print("Path Matrix\n{0}\n".format(pathMatrix))
print("Best path to destination from {0} to {1} is to take {2}".format(pathDesired[0],pathDesired[1],pathMatrix[pathDesired][1]))
#Define a list of colors that each edge will have based on route desired
edge_colors = ['black' if not i in pathMatrix[pathDesired][1] else 'red' for i in outGraph.edges()]
#Draw the graph and labels, then display it
nx.draw(outGraph,nodePos,edge_color=edge_colors)
nx.draw_networkx_labels(outGraph,nodePos,font_size=12,font_family='sans-serif')
plt.show()