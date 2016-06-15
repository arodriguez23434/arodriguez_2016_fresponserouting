#!/usr/bin/env python

import math
import networkx as nx

#--Non-Specific--
#Function to get various pieces of information of shortest path from startnode to endnode and output them
#Currently obtains total path distance and all edges along path
def get_shortest_path_info(graph,startnode,endnode,nodeAttr):
    #NetworkX algorithm to get list of nodes in the shortest path
    best_route = nx.dijkstra_path(graph,startnode,endnode)
    #Sum distances between each node in list and return that sum
    dist = 0; prevnode = startnode;
    for currnode in best_route:
        dist += math.sqrt(math.pow(nodeAttr[currnode][0]-nodeAttr[prevnode][0],2) + math.pow(nodeAttr[currnode][1]-nodeAttr[prevnode][1],2))
        prevnode = currnode
    #Get edges along path
    edgelist = []; prevnode = startnode
    for i in best_route:
        if (i!=startnode):
            if (i,prevnode) in graph.edges():
                edgelist.append((i,prevnode)) 
            elif (prevnode,i) in graph.edges():
                edgelist.append((prevnode,i))
            else:
                print("Could not find edge "+(prevnode,i))
        prevnode = i
    #Store and return all the information
    info = [dist,edgelist]
    return info;
    
#--Path Matrix--
#Function to initialize the path matrix
def matrix_create(graph,nodeAttr):
    print('Creating path matrix...');
    #Initialize dictionary representing path matrix
    pathMatrix = dict();
    #Register all possible node paths into matrix
    for i in nodeAttr.keys():
        for j in nodeAttr.keys():
            #Calculate the distance between every path
            pathinfo = get_shortest_path_info(graph,i,j,nodeAttr)
            #This function can be expanded later to for multiple path attributes
            pathMatrix[(i,j)] = (pathinfo[0],pathinfo[1]);
    return pathMatrix;

#Function to remove all references to a node from a matrix
def matrix_remove_node(pathMatrix,node):
    newMatrix = {key:pathMatrix[key] for key in pathMatrix if node not in key[0] and node not in key[1]};
    pathMatrix = newMatrix;
    return pathMatrix;

#--Network--
#Function to remove a node from all network-related items
def network_remove_node(node,graph,netNodeAttr,netNodePos,pathMatrix):
    pathMatrix = matrix_remove_node(pathMatrix,node)
    del netNodeAttr[node]; del netNodePos[node]
    graph.remove_node(node)
    return pathMatrix;

#Function to add a node with attribute tuple addNodeAttr and list of connecting neighbors to all network-related items
def network_add_node(node,addNodeAttr,neighbors,graph,netNodeAttr,netNodePos,pathMatrix):
    #Add the node to the graph
    graph.add_node(node)
    graph.node[node]['pos'] = (addNodeAttr[0],addNodeAttr[1])
    #TODO: Add any other necessary attributes to node
    #Add all connecting neighbors as NetworkX edges
    for connect in neighbors: graph.add_edge(node,connect);
    netNodeAttr[node] = addNodeAttr;
    netNodePos[node] = (netNodeAttr[node][0],netNodeAttr[node][1])
    for key in netNodeAttr.keys():
        pathinfo = get_shortest_path_info(graph,node,key,netNodeAttr)
        pathMatrix[(node,key)] = (pathinfo[0],pathinfo[1]);
        pathMatrix[(key,node)] = (pathinfo[0],pathinfo[1]);
    return pathMatrix;