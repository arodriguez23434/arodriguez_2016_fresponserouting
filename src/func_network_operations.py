#!/usr/bin/env python

import math
import networkx as nx

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
            #TODO: Multiple path attributes
            pathMatrix[(i,j)] = (pathinfo[0],pathinfo[1]);
    return pathMatrix;

#Function to remove a node from all network-related items
def network_remove_node(node,graph,netNodeAttr,netNodePos,pathMatrix):
    #Delete the node from the attribute and position dictionaries
    del netNodeAttr[node]; del netNodePos[node]
    #Delete the node from the NetworkX graph
    graph.remove_node(node)
    #Remove all references to a node from path matrix
    newMatrix = {key:pathMatrix[key] for key in pathMatrix if node not in key[0] and node not in key[1]};
    #Re-calculate any paths that have previously used this node
    for key in newMatrix:
        for i in newMatrix[key][1]:
            if i[0]==node or i[1]==node:
                #Calculate the distance between every path
                pathinfo = get_shortest_path_info(graph,key[0],key[1],netNodeAttr)               
                #TODO: Multiple path attributes
                newMatrix[key] = (pathinfo[0],pathinfo[1]);
    return newMatrix;

#Function to add a node with attribute tuple addNodeAttr and list of connecting neighbors to all network-related items
def network_add_node(node,addNodeAttr,neighbors,graph,netNodeAttr,netNodePos,pathMatrix):
    #Add the node to the graph
    graph.add_node(node)
    graph.node[node]['pos'] = (addNodeAttr[0],addNodeAttr[1])
    #TODO: Add any other necessary attributes to node
    #Add attribute data from new node to full node dictionaries
    netNodeAttr[node] = addNodeAttr;
    netNodePos[node] = (netNodeAttr[node][0],netNodeAttr[node][1])
    #Add all connecting neighbors as NetworkX edges
    for connect in neighbors: 
        graph.add_edge(node,connect);
        dist = math.sqrt(math.pow(netNodePos[connect][0]-netNodePos[node][0],2) + math.pow(netNodePos[connect][1]-netNodePos[node][1],2));
        graph[node][connect]['weight'] = dist; 
    #Retrieve all possible paths and add to path matrix
    for key in netNodeAttr.keys():
        pathinfo = get_shortest_path_info(graph,node,key,netNodeAttr)
        pathMatrix[(node,key)] = (pathinfo[0],pathinfo[1]);
        pathMatrix[(key,node)] = (pathinfo[0],pathinfo[1]);
    return pathMatrix;