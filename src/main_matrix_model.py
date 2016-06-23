#!/usr/bin/env python

import math
import networkx as nx
import matplotlib.pyplot as plt
import func_network_operations as nop

"""
Objective:
o Calculate shortest path from one node in space to another using a robust
  model that can be later expanded upon for real-world problems.
"""

#--Configuration--
#TODO: loadFromFile = False (Allow parameters for file I/O rather than manual entry)
#      fileDir = ".xlsl"
#TODO: obstructedEdges = [('A','B'),...]
#nodeAttr: Key should be node name and the first two attributes must represent X and Y positions in the graph
#nodeNeighbors: Must be list of 2D tuples that are made of two node names in nodeAttr
#pathDesired: Must be a 2D tuple made of two node names in nodeAttr
nodeAttr = {'A': (0,0), 'B': (2,0), 'C': (2,1), 'E': (0,1)}
nodeNeighbors = [('A','B'),('B','C'),('A','E')]
pathDesired = ('A','C')

#--End of Configuration--

#--Model Initialization--
#Before doing anything else, check user input for errors
netProceed = nop.check_user_input(nodeAttr,nodeNeighbors,pathDesired)
if netProceed == False: print("Please reconfigure the model to fix the issue(s) and try again.")
#If there are no issues, proceed
else:
    #Create a position dictionary from first two attributes of user-defined dictionary
    #Acts as input for NetworkX draw functions
    nodePos = nodeAttr.fromkeys(nodeAttr.keys(),(0,0))
    for key in nodeAttr: nodePos[key] = (nodeAttr[key][0],nodeAttr[key][1]);
    #Set up the NetworkX graph object for output
    outGraph = nx.Graph()
    #The nodes are identified based on keys/node names by user
    outGraph.add_nodes_from(nodePos.keys())
    #Add all connecting neighbors as NetworkX edges
    outGraph.add_edges_from(nodeNeighbors)
    #Add NetworkX attributes for nodes and edges
    for i, p in nodePos.items(): 
        outGraph.node[i]['pos'] = p;
    for node1,node2 in outGraph.edges():
        dist = math.sqrt(math.pow(nodePos[node2][0]-nodePos[node1][0],2) + math.pow(nodePos[node2][1]-nodePos[node1][1],2));
        outGraph[node1][node2]['weight'] = dist;
        #TODO: NetworkX uses a universal 'weight' attribute for edges for its algorithms
        #Later on, a function to calculate a total 'weight' based on distance and other attributes
        #needs to be made and performed before performing any NetworkX shortest_path algorithms
    #Create a path matrix for the network
    pathMatrix = nop.matrix_create(outGraph,nodeAttr);
    
#--Main Operating Block--
    
    #EXAMPLE: removing node 'C' then adding node 'D' and re-routing to there
    try: pathMatrix = nop.network_remove_node('C',outGraph,nodeAttr,nodePos,pathMatrix)    
    except: print("ERROR: Failed to remove node (input error)")    
    try: pathMatrix = nop.network_add_node('D',(1,2),['B','E'],outGraph,nodeAttr,nodePos,pathMatrix)
    except: print("ERROR: Failed to add node (input error)")    
    pathDesired = ('B','E')
    
    #Print out the nodes and edges for debugging purposes
    #print("\nNodes\n{0}\n\nEdges\n{1}\n".format(outGraph.nodes(data=True),outGraph.edges(data=True)))
    #print("Path Matrix\n{0}\n".format(pathMatrix))
    try:
        print("Best path to destination from {0} to {1} is to take {2}".format(pathDesired[0],pathDesired[1],pathMatrix[pathDesired][1]))
        #Define a list of colors that each edge will have based on route desired
        edge_colors = ['black' if not i in pathMatrix[pathDesired][1] else 'blue' for i in outGraph.edges()]
        #Draw the graph and labels, then display it
    except:
        print("WARNING: Graph cannot display best path due to previous error(s).")
        nx.draw(outGraph,nodePos)
    else:
        nx.draw(outGraph,nodePos,edge_color=edge_colors)
    nx.draw_networkx_labels(outGraph,nodePos,font_size=12,font_family='sans-serif')
    plt.show()