#!/usr/bin/env python

import math
import networkx as nx
import openpyxl as xl

#Function to get various pieces of information of shortest path from startnode to endnode and output them
#Currently obtains total path distance and all edges along path
def get_shortest_path_info(graph,startnode,endnode,netNodeAttr):
    #NetworkX algorithm to get list of nodes in the shortest path
    try:
        best_route = nx.dijkstra_path(graph,startnode,endnode)
    except nx.NetworkXNoPath:
        print("ERROR: Node %s is unreachable from node %s. Is the path properly configured?" % (endnode,startnode))
        return False
    else:
        #Sum distances between each node in list and return that sum
        dist = 0; prevnode = startnode;
        for currnode in best_route:
            dist += math.sqrt(math.pow(netNodeAttr[currnode][0]-netNodeAttr[prevnode][0],2) + math.pow(netNodeAttr[currnode][1]-netNodeAttr[prevnode][1],2))
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
def matrix_create(graph,netNodeAttr):
    print('Creating path matrix...');
    #Initialize dictionary representing path matrix
    pathMatrix = dict();
    #Register all possible node paths into matrix
    for i in netNodeAttr.keys():
        for j in netNodeAttr.keys():
            try:
                #Calculate the distance between every path
                pathinfo = get_shortest_path_info(graph,i,j,netNodeAttr)
                if pathinfo!=False: pathMatrix[(i,j)] = pathinfo
                else: raise nx.NetworkXNoPath()
            except:
                print("ERROR: Failed to create pathing matrix. Please check your configuration and try again.");
                return False
    return pathMatrix;

#Function to remove a node from all network-related items
def network_remove_node(node,graph,netNodeAttr,netNodePos,pathMatrix):
    #Delete the node from the attribute and position dictionaries
    del netNodeAttr[node]; del netNodePos[node]
    #Delete the node from the NetworkX graph
    graph.remove_node(node)
    #Remove all references to a node from path matrix
    try:
        newMatrix = {key:pathMatrix[key] for key in pathMatrix if node not in key[0] and node not in key[1]};
    except TypeError:
        print("ERROR: Original pathing matrix does not exist. While node %s has been removed, pathing calculations cannot be made for the network." % node);
        return False
    #Re-calculate any paths that have previously used this node
    for key in newMatrix:
        for i in newMatrix[key][1]:
            if i[0]==node or i[1]==node:
                #Calculate the distance between every path
                pathinfo = get_shortest_path_info(graph,key[0],key[1],netNodeAttr)               
                #TODO: Multiple path attributes
                newMatrix[key] = pathinfo;
    return newMatrix;

#Function to add a node with attribute list addNodeAttr and list of connecting neighbors to all network-related items
def network_add_node(node,addNodeAttr,neighbors,graph,netNodeAttr,netNodePos,pathMatrix):
    try: type(addNodeAttr[1])
    except: print("ERROR: Invalid node attribute input! (Must be list of at least 2 values)")
    else:    
        #Add the node to the graph
        graph.add_node(node)
        graph.node[node]['pos'] = [addNodeAttr[0],addNodeAttr[1]]
        #TODO: Add any other necessary attributes to node
        #Add attribute data from new node to full node dictionaries
        try:
            netNodeAttr[node] = addNodeAttr;
            netNodePos[node] = [netNodeAttr[node][0],netNodeAttr[node][1]]
        except TypeError: print("ERROR: Node attribute or position list was invalid"); return False
        #Add all connecting neighbors as NetworkX edges
        try:
            for connect in neighbors:           
                try: 
                    dist = math.sqrt(math.pow(netNodePos[connect][0]-netNodePos[node][0],2) + math.pow(netNodePos[connect][1]-netNodePos[node][1],2))
                    graph.add_edge(node,connect)
                    graph[node][connect]['weight'] = dist
                except KeyError: print("ERROR: Failed to connect node to neighbors! (Attempted to connect to nonexistent neighbor)")            
                except TypeError: print("ERROR: Failed to connect node to neighbors! (Node attributes were not a list of at least 2 elements)")            
        except TypeError: print("ERROR: Failed to connect node to neighbors! (Input type was not a list)")
        #Retrieve all possible paths and add to path matrix
        try:
            for key in netNodeAttr.keys():
                pathinfo = get_shortest_path_info(graph,node,key,netNodeAttr)
                pathMatrix[(node,key)] = pathinfo;
                pathMatrix[(key,node)] = pathinfo;
        except TypeError:
            print("ERROR: Original pathing matrix does not exist. While node %s has been added, pathing calculations cannot be made for the network." % node);
            return False
    return pathMatrix;

#TODO: Create edgeAttr dict for further weight calculations
#TODO: Consider other nodeAttr attributes
def calc_edge_weights(graph,netNodeAttr):
    for node1,node2 in graph.edges():
        dist = math.sqrt(math.pow(netNodeAttr[node2][0]-netNodeAttr[node1][0],2) + math.pow(netNodeAttr[node2][1]-netNodeAttr[node1][1],2));
        result = dist
        graph[node1][node2]['weight'] = result;
    return;

def file_check(netFileDir):
    #First check if the user entered an actual file name
    if len(netFileDir)<3: print("ERROR: Not a file!"); return False;
    #Next, check if the file is an excel workbook
    if netFileDir.lower().endswith(('.xlsx','.xlsm','.xltx','.xltm')):
        try:
            wb = xl.load_workbook(filename = netFileDir)
            return wb;
        except:
            print("ERROR: Invalid file %s" % netFileDir)
            return False;
    else:
        print("ERROR: File type was not supported (%s instead of .xlsx, .xlsm, .xltx, or .xltm)" % netFileDir[-4:])
        return False;

def file_excel_interpret(netFileDir,wb,netNodeAttr,netNodeNeighbors,netPathDesired):
    #Since we are no longer using the in-line config, clear inputs
    netNodeAttr.clear(); netNodeNeighbors[:] = []
    #Load the 1st worksheet in the excel workbook  (nodeAttr)   
    ws = wb.worksheets[0]
    #Recreate the nodeAttr dictionary row-by-row
    for row in ws.rows:
        #TODO: Put under try method
        #Create a temporary list of values for a row
        row_values = list()
        #If the row is the label row, do not interpret
        if row[0].row == 1 or row[0].row == 3: continue
        if row[0].row == 2:
            netPathDesired = (row[0].value,row[1].value)
            continue
        for cell in row:
            #If the cell is in the label column, do not interpret
            if  cell.column == 'A': continue
            #Add each cell value to the temporary list of row values
            row_values.append(cell.value*100)
        #Use first column value as key and add list of row values as attributes
        netNodeAttr[row[0].value] = row_values
    #Load the 2nd worksheet in the excel workbook (nodeNeighbors)
    ws = wb.worksheets[1]
    #Recreate nodeNeighbors list row-by-row    
    for row in ws.rows: netNodeNeighbors.append([row[0].value,row[1].value])
    return netPathDesired;
    
def check_user_input(netNodeAttr,netNodeNeighbors,netPathDesired):
    #Are the nodes properly setup?
    for i in netNodeAttr.values():
        #Is the node a list with at least two attributes?        
        try: [i[0],i[1]];
        except TypeError:
            print("ERROR: A node was not properly setup! (Node attributes were not entered as a list; entered as {0})".format(i))
            return False;
        except IndexError:
            print("ERROR: A node was not properly setup! (Not enough/invaild attributes; only found {0})".format(i))
            return False;
        #Does the same node appear more than once?
        node_occur = 0
        for j in netNodeAttr.values():
            if i == j: node_occur+=1
            if node_occur > 1:
                print("ERROR: Found two nodes in the exact same position! ({0} and {1})".format(i,j))
                return False;
        #TODO: Make temporary list of distances between positions and warn user
        #      if distances between a single pair are unreasonably large or zero
    #Are the edges properly setup?
    for i in netNodeNeighbors:
        try:
            if type(i)!=list: raise TypeError
            if len(i)!=2:
                print("ERROR: Edge {0} was improperly setup! ({1} attribute(s) instead of exactly 2)".format(i,len(i)))
                return False;
        except TypeError:
            print("ERROR: Edge {0} was improperly setup! (Not a list)".format(i))
            return False;            
    #Is every node connected to an edge?
    for i in netNodeAttr.keys():
        node_occur = 0
        for j,k in netNodeNeighbors:
            if i==j or i==k: node_occur=1; break
        if node_occur == 0:
            #TODO: Should we throw this as an error or a warning?
            print("ERROR: Node %s is not connected to any other nodes!" % i)
            return False;
    #Is the desired path valid?
    try: 
        if type(netPathDesired)!=tuple: raise TypeError
        if len(netPathDesired)!=2:
            print("ERROR: Path was improperly setup! (%d attribute(s) instead of exactly 2)" % len(netPathDesired))
            return False;
        if netPathDesired[0]==netPathDesired[1]: print("WARNING: Path does not lead anywhere! (Start and end node are both %s)" %netPathDesired[0])
    except TypeError: 
        print("ERROR: Desired route was improperly setup! (Not a tuple)")
        return False;
    #Do the nodes in the path desired exist?
    #TODO: Could merge this to 'Is every node connected to an edge?' loop, but
    #      this would disorganize code
    node_occur_a = 0; node_occur_b = 0
    for i in netNodeAttr.keys():
        if i == netPathDesired[0]: node_occur_a+=1
        elif i == netPathDesired[1]: node_occur_b+=1
    if node_occur_a<=0:
        print("ERROR: Start node %s on desired route does not exist!" % netPathDesired[0])
        return False;
    elif node_occur_b<=0:
        print("ERROR: End node %s on desired route does not exist!" % netPathDesired[1])
        return False;
    return True;