#!/usr/bin/env python

import math
import networkx as nx
import openpyxl as xl
import statistics as stat
import numpy
import matplotlib.pyplot as plt
from numpy import random

#Function to calculate the fuel cost along an edge
def calc_fuel_cost(time,distance,elevation):
    #TODO: Calculation is currently placeholder; replace with suitable one
    activeConsume = 1; heightConsume = 2
    fuel_consumed = activeConsume*time
    angle = math.asin(elevation/(distance*5280))
    fuel_consumed += heightConsume*fuel_consumed*math.sin(angle)
    return fuel_consumed
    
#Function to get various pieces of information of shortest path from startnode to endnode and output them
def get_shortest_path_info(graph,startnode,endnode,netNodeAttr):
    #NetworkX algorithm to get list of nodes in the shortest path
    try:
        best_route = nx.dijkstra_path(graph,startnode,endnode)
    except nx.NetworkXNoPath:
        print("ERROR: Node %s is unreachable from node %s. Is the path properly configured?" % (endnode,startnode))
        return False
    else:
        #Get edges and their weights/attributes along path
        edgelist = []; prevnode = startnode; 
        #Values suffixed with _total are used for the attributes along the entire path        
        weight_total = 0; time_total = 0; dist_total = 0; elev_total = 0; fuel_total = 0
        for i in best_route:
            if (i!=startnode):
                #Ensure that both orders of the node pair are analyzed 
                #Neceessary due to user input vs. NetworkX registration in memory
                if (i,prevnode) in graph.edges():
                    #Add the edge to the list of edges along the path
                    edgelist.append((i,prevnode)) 
                    #Add the weights and attributes of the edge to the total along the path
                    weight_total+=graph[i][prevnode]['weight']
                    time_total+=graph[i][prevnode]['time']
                    dist_total+=graph[i][prevnode]['distance']
                    elev_total+=graph[i][prevnode]['elevation']
                    fuel_total+=graph[i][prevnode]['fuel']
                elif (prevnode,i) in graph.edges():
                    #Add the edge to the list of edges along the path
                    edgelist.append((prevnode,i))
                    #Add the weights and attributes of the edge to the total along the path
                    weight_total+=graph[prevnode][i]['weight']
                    time_total+=graph[prevnode][i]['time']
                    dist_total+=graph[prevnode][i]['distance']
                    elev_total+=graph[prevnode][i]['elevation']
                    fuel_total+=graph[prevnode][i]['fuel']
                else:
                    print("Could not find edge "+(prevnode,i))
            prevnode = i
        #Store and return all the information
        info = [weight_total,edgelist,time_total,dist_total,elev_total,fuel_total]
        return info;

#Iterate over generated times/weights based on Gaussian distribution
def iter_edges(graph,runIter):
    for i,j in graph.edges():
        graph[i][j]['weight']=graph[i][j]['weight_list'][runIter]
        graph[i][j]['time']=graph[i][j]['time_list'][runIter]
        graph[i][j]['fuel']=graph[i][j]['fuel_list'][runIter]
        
#Function to initialize the path matrix
def matrix_create(graph,netNodeAttr,netNumRuns):
    print('Creating path matrix...');
    #Initialize dictionary representing path matrix
    pathMatrix = dict();
    #Register all possible node paths into matrix
    for i in netNodeAttr.keys():
        for j in netNodeAttr.keys():
            pathMatrix = matrix_iter(graph,netNodeAttr,netNumRuns,pathMatrix,i,j)
    return pathMatrix;

#Iterate through node attribute list for a number of runs to create the path matrix
def matrix_iter(graph,netNodeAttr,netNumRuns,pathMatrix,i,j):
    try:
        #Create a list for each path over netNumRuns iterations and final "best of best" path 
        best_path = list(); all_paths = list(); saveIter = 0
        for runIter in range(0,netNumRuns):
            iter_edges(graph,runIter);
            #Calculate the distance between every path
            pathinfo = get_shortest_path_info(graph,i,j,netNodeAttr)
            #Only record info if path is valid                    
            if pathinfo!=False: 
                #If this is the first entry in best_path, set it to current path
                if not best_path: best_path = pathinfo
                #If the path we found is better than our best_path, set best_path to it
                elif pathinfo[0]<best_path[0]: 
                    best_path = pathinfo
                    saveIter = runIter
                #Append the path to all potential paths
                all_paths.append(pathinfo)
            #If an error occurs, raise an exception
            else: raise nx.NetworkXNoPath()
        #If the path lists are valid, set the pathMatrix entry to them
        if best_path and all_paths: 
            pathMatrix[(i,j)] = [best_path,all_paths,saveIter]
        else: raise nx.NetworkXNoPath()
    except ValueError:
        for i,j in graph.edges():
            print(i,j,graph[i][j]['weight'])
        print("ERROR: Failed to create pathing matrix. Please check your configuration and try again.");
        return False
    return pathMatrix;  
    
#Function to remove a node from all network-related items
def network_remove_node(node,graph,netNodeAttr,netEdgeAttr,netNodePos,pathMatrix,netNumRuns):
    #Delete the node from the attribute and position dictionaries
    del netNodeAttr[node]; del netNodePos[node]
    #Delete the node from the NetworkX graph
    graph.remove_node(node)
    #Remove references to node from edgeAttr
    removeEdgeKey = list(); tempEdgeAttr = dict(netEdgeAttr)
    for key in netEdgeAttr:
        if key.find(node)!=-1:
            removeEdgeKey.append(key)
    netEdgeAttr = {key: tempEdgeAttr[key] for key in tempEdgeAttr if key not in removeEdgeKey}
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
                newMatrix = matrix_iter(graph,netNodeAttr,netNumRuns,newMatrix,key[0],key[1])
    return newMatrix;

#Function to add a node with attribute list addNodeAttr and list of connecting neighbors to all network-related items
def network_add_node(node,addNodeAttr,addEdgeAttr,graph,netNodeAttr,netEdgeAttr,netNodePos,pathMatrix,netNumRuns,netTestFor,netObstructChance):
    try: type(addNodeAttr[1])
    except: print("ERROR: Invalid node attribute input! (Must be list of at least 2 values)")
    else:    
        #Add the node to the graph
        graph.add_node(node)
        graph.node[node]['pos'] = [addNodeAttr[0],addNodeAttr[1]]
        #Add attribute data from new node to full node dictionaries
        try:
            netNodeAttr[node] = addNodeAttr;
            netNodePos[node] = [netNodeAttr[node][0],netNodeAttr[node][1]]
        except TypeError: print("ERROR: Node attribute or position list was invalid"); return False
        #Add attribute data from new edge dictionary        
        try:
            neighbors = list()        
            for i in addEdgeAttr:
                netEdgeAttr[i]=addEdgeAttr[i]
                strind = i.index(',')
                if node!=i[0:strind]: neighbors.append(i[0:strind])
                if node!=i[strind+1:]: neighbors.append(i[strind+1:])      
        except: print("ERROR: Failed to obtain neighbors from edge attribute list!"); return False   
        #Add all connecting neighbors as NetworkX edges
        try:
            for connect in neighbors:      
                try: 
                    graph.add_edge(node,connect)
                except KeyError: print("ERROR: Failed to connect node to neighbors! (Attempted to connect to nonexistent neighbor)")            
            #Calculate the new edge weights
            try: calc_edge_weights(graph,netNodeAttr,netEdgeAttr,netNumRuns,netTestFor,netObstructChance)
            except: print("ERROR: Failed to calculate weights on edges!")
        except TypeError: print("ERROR: Failed to connect node to neighbors! (Node attributes were not a list of at least 2 elements)")            
        #Retrieve all possible paths and add to path matrix
        else:
            try:
                #Create a path matrix for the network
                pathMatrix = matrix_create(graph,netNodeAttr,netNumRuns);
            except TypeError:
                print("ERROR: Original pathing matrix does not exist. While node %s has been added, pathing calculations cannot be made for the network." % node);
                return False
    return pathMatrix;

def calc_edge_weights(graph,netNodeAttr,netEdgeAttr,netNumRuns,netTestFor,netObstructChance):
    for node1,node2 in graph.edges():
        #Try to get info about the edge from edgeAttr
        #Before throwing an exception, check if networkX ordered the key backwards
        try: edgeInfo=netEdgeAttr[str(node1+','+node2)]
        except KeyError: edgeInfo=netEdgeAttr[str(node2+','+node1)]
        #Get the average and standard deviation of recorded times
        timeAvg = stat.mean(edgeInfo[1]); timeStd = stat.stdev(edgeInfo[1]);
        #Create a list for time generated based on Gaussian distribution
        #Create a list for all the weights and fuel costs calculated
        timeGen = list(); weight_list = list(); fuelCost = list()
        #Calculate the distance between the nodes on the edge
        dist = math.sqrt(math.pow(netNodeAttr[node2][2]-netNodeAttr[node1][2],2) + math.pow(netNodeAttr[node2][3]-netNodeAttr[node1][3],2));
        #Calculate the difference in height between the nodes on the edge        
        heightdelta = netNodeAttr[node1][4]-netNodeAttr[node2][4]
        for i in range(0,netNumRuns): 
            #Generate a time based on Gaussian distribution of input times
            timeGen.append(abs(random.normal(timeAvg,timeStd,None)))
            #Add this time to the list of weights
            weight_list.append(timeGen[i]*netTestFor[0])
            #Obtain the fuel consumed
            fuelCost.append(calc_fuel_cost(timeGen[i]*netTestFor[0],dist*netTestFor[1],heightdelta*netTestFor[2]))
            #Add this fuel cost to the weight consideration
            weight_list[i]+= fuelCost[i]
            #Determine if the road is obstructed in this iteration
            obstructed=random.uniform(0,1)
            if obstructed <= netObstructChance: edgeInfo[0]=True
            else: edgeInfo[0]=False
            #If the road is obstructed, set weight to an invalid value
            #TODO: Currently it just sets the weight to a high value;
            #      Find suitable NetworkX substitute if possible
            if edgeInfo[0]==True: weight_list[i] += 10000;
            #If the weight is negative, set it to zero and warn the user
            if weight_list[i]<=0:
                weight_list[i]=1
                print("WARNING: Weight on edge [{0},{1}] was negative!".format(node1,node2))
        #Record time list, fuel list, weight list, and initial values as NetworkX edge attributes
        graph[node1][node2]['time_list'] = timeGen;
        graph[node1][node2]['time'] = timeGen[0];        
        graph[node1][node2]['weight_list'] = weight_list;
        graph[node1][node2]['weight'] = weight_list[0];
        graph[node1][node2]['elevation'] = heightdelta;
        graph[node1][node2]['fuel_list'] = fuelCost;
        graph[node1][node2]['fuel'] = fuelCost[0];
        #TODO: Refine distance to be based on more accurate formula
        graph[node1][node2]['distance'] = 86.121212*dist;
    return;

def file_check(netFileDir):
    #First check if the user entered an actual file name
    if len(netFileDir)<3: print("ERROR: Not a file!"); return False;
    #Next, check if the file is an excel workbook
    if netFileDir.lower().endswith(('.xlsx','.xlsm','.xltx','.xltm')):
        try:
            wb = xl.load_workbook(filename = netFileDir)
            netType = ['excel',wb]
            return netType;
        except:
            print("ERROR: Invalid file %s" % netFileDir)
            return False;
    #If it is not, check if the file is a text file
    elif netFileDir.lower().endswith(('.txt')):
        try:
            with open(netFileDir,'r') as file:
                netType = ['txt',file]
            return netType
        except:
            print("ERROR: Invalid file %s" % netFileDir)
            return False;
    #If it is neither, inform user that the file type is not supported
    else:
        print("ERROR: File type was not supported (%s instead of .xlsx, .xlsm, .xltx, or .xltm)" % netFileDir[-4:])
        return False;

def file_excel_interpret(netFileDir,wb,netNodeAttr,netEdgeAttr,netNodeNeighbors,netPathDesired,netNumRuns,netObstructChance,netTestFor):
    #Since we are no longer using the in-line config, clear inputs
    netNodeAttr.clear(); netEdgeAttr.clear(); netNodeNeighbors[:] = []
    #Load the 1st worksheet in the excel workbook  (nodeAttr)   
    ws = wb.worksheets[0]
    #Recreate the nodeAttr dictionary row-by-row
    for row in ws.rows:
        #Create a temporary list of values for a row
        row_values = list()
        #If the row is the label row, do not interpret
        if row[0].row == 1 or row[0].row == 3: continue
        elif row[0].row == 2:
            try:
                #If the row is the configuration row, set all the info to a variable to return to the main function
                netPathDesired = (row[0].value,row[1].value)
                netNumRuns = row[2].value
                netObstructChance = row[6].value
                netTestFor = [row[3].value,row[4].value,row[5].value]
                netInfo = [netPathDesired,netNumRuns,netObstructChance,netTestFor]
            except: print("ERROR: Failed to retrieve configuration data from spreadsheet 1!")
            continue
        for cell in row:
            #If the cell is in the label column, do not interpret
            #TODO: Remove 'G' as a condition when the column is filled
            if cell.column == 'A' or cell.column == 'G': continue
            if cell.value == None: print("WARNING: Cell {0}{1} in spreadsheet 1 has no value!".format(cell.row,cell.column));
            #Add each cell value to the temporary list of row values
            row_values.append(cell.value)
        #Use first column value as key and add list of row values as attributes
        netNodeAttr[row[0].value] = row_values
    #Load the 2nd worksheet in the excel workbook (nodeNeighbors)
    ws = wb.worksheets[1]
    #Recreate nodeNeighbors list row-by-row    
    for col in ws.columns: 
        #Create a temporary list of values for a column
        col_values = list(); time_values = list()
        #If the column is the label column, do not interpret
        if col[0].column == 'A': continue
        for cell in col:
            #Ensure the the cell has a value of some sort, warn user if otherwise
            if cell.value == None: print("WARNING: Cell {0}{1} in spreadsheet 2 has no value!".format(cell.row,cell.column));
            #Add the connections between nodes as defined by the 1st line        
            if cell.row == 1:
                try:
                    #Search for the seperator between the node names (,) and append each node to the neighbors list as a split string
                    strind = cell.value.index(',')
                    netNodeNeighbors.append([cell.value[0:strind],cell.value[strind+1:]])
                except: print("ERROR: Edge at Cell {0}{1} in spreadsheet 2 was improperly setup! (Must be two nodes seperated by comma)".format(cell.row,cell.column))
            #If this is the second row, register the obstructed edge value as false
            elif cell.row == 2: col_values.append(False)
            #All rows below the first is for registering time data
            if cell.row > 1: time_values.append(cell.value)
        #Append the time data to the values obtained from the column
        col_values.append(time_values)
        #Set the attributes for each edge according to what was obtained from its column
        netEdgeAttr[col[0].value] = col_values                
    return netInfo;
    
def file_inputs_interpret(netFileDir,file,netPathDesired,netNumRuns,netObstructChance,netTestFor):
    #Setup basic inputs for returning values
    netInfo = list(); lineStr = str('\n'); pathFind = False;
    #Open the file; with parameter allows file to be closed even during exceptions
    with open(netFileDir,'r') as f:
        while lineStr:
            #Read the next line
            lineStr = f.readline()
            #If the read is at EoF, do not continue
            if not lineStr: break
            #If we have reached the Pathways category, skip to the next line and search for the path desired
            if 'Pathways' in lineStr: pathFind = True; continue
            #Ensure the line is not commented out
            if pathFind and lineStr[0]!='#':
                try:
                    strind = lineStr.index(',')
                    strend = lineStr.index('\n')
                    netPathDesired = (lineStr[0:strind],lineStr[strind+1:strend])
                except: print("ERROR: Path desired was improperly setup!")
            #Check for specific parameters within the line and add to netInfo accordingly
            #If the first character is a #, skip the line
            if not lineStr[0]=='#':
                if 'NumberOfIterations' in lineStr: netNumRuns=int(lineStr[19:])
                elif 'ObstructionChance' in lineStr: netObstructChance=float(lineStr[18:])
                elif 'TimeConsideration' in lineStr: netTestFor[0]=float(lineStr[18:])
                elif 'DistanceConsideration' in lineStr: netTestFor[1]=float(lineStr[22:])
                elif 'ElevationConsideration' in lineStr: netTestFor[2]=float(lineStr[23:])
    #Return the info provided
    netInfo = [netPathDesired,netNumRuns,netObstructChance,netTestFor]
    return netInfo;

def check_user_input(netNodeAttr,netEdgeAttr,netNodeNeighbors,netPathDesired,netNumRuns):
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
    for i in netEdgeAttr:
        #Ensure the edge is properly setup with the correct syntax
        try: 
            if i.index(',')==-1: raise ValueError;
        except:
            print("ERROR: An edge was not properly setup! (Key should be in form of node1,node2; recieved {0})" % i)
        #Is the edge a list with at least two attributes?        
        try: [netEdgeAttr[i][0],netEdgeAttr[i][0]];
        except TypeError:
            print("ERROR: An edge was not properly setup! (Edge attributes were not entered as a list; entered as {0})".format(netEdgeAttr[i]))
            return False;
        except IndexError:
            print("ERROR: An edge was not properly setup! (Not enough/invaild attributes; only found {0})".format(netEdgeAttr[i]))
            return False;
    #Are the edges properly setup?
    for i in netNodeNeighbors:
        try:
            #Ensure that the neighboring nodes list contains lists of exactly two values
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
        #Go through each neighbor and ensure that all nodes in the nodeAttr dict can be found in the list
        for j,k in netNodeNeighbors:
            if i==j or i==k: node_occur=1; break
        if node_occur == 0:
            print("ERROR: Node %s is not connected to any other nodes!" % i)
            return False;
    #Is the desired path valid?
    try: 
        #Ensure that the path desired is a tuple of exactly 2 values
        if type(netPathDesired)!=tuple: raise TypeError
        if len(netPathDesired)!=2:
            print("ERROR: Path was improperly setup! (%d attribute(s) instead of exactly 2)" % len(netPathDesired))
            return False;
        #Warn the user if the starting and ending nodes are the same
        if netPathDesired[0]==netPathDesired[1]: print("WARNING: Path does not lead anywhere! (Start and end node are both %s)" %netPathDesired[0])
    except TypeError: 
        print("ERROR: Desired route was improperly setup! (Not a tuple)")
        return False;
    #Do the nodes in the path desired exist?
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
    #Check if the number of iterations is reasonable
    if netNumRuns < 1:
        print("ERROR: Number of times to run program is less than 1 (input %d)!" % netNumRuns)
        return False;
    elif netNumRuns > 1000: print("WARNING: Large number of times to run program (input %d)!" % netNumRuns)
    return True;
    
def relationshipGraphSetup(netPathMatrix,netPathDesired,netNumRuns):
    #TODO: Currently, this function uses a lot of pasted code.
    #      This is unfortunately due to the difference in data input and iterating through each figure.
    #      See if this can be placed under a loop, even if large if conditions are necessary
    #Setup variable for outputting relationship data
    relationData = list()
    #Setup graphical outputs for correlation
    #Set the matplotlib figure to a new figure and setup x and y values
    plt.figure(2); relationX = list(); relationY = list()
    for i in range(1,netNumRuns):
        #Set x and y values based on distance and weight
        if netPathMatrix[netPathDesired][1][i][0] < 10000:
            #Do not consider weight in relation if too extreme of a value
            relationX.append(netPathMatrix[netPathDesired][1][i][3])
            relationY.append(netPathMatrix[netPathDesired][1][i][0])
    #Fit the data to a best fit line and place into relationship output data
    relationData.append(numpy.polyfit(relationX, relationY, 1))
    #Display the best fit line equation
    tempData=relationData[len(relationData)-1].tolist()
    plt.text(relationX[round(len(relationX)/2)],relationY[round(len(relationY)/2)],'y = {0}x + {1}'.format(round(tempData[0],3),round(tempData[1],3)))
    #Plot the best fit line
    plt.plot(relationX, numpy.poly1d(relationData[len(relationData)-1])(relationX))
    #Plot the x and y values    
    plt.scatter(relationX,relationY)
    #Set the labels accordingly
    plt.xlabel('Path Distance'); plt.ylabel('Path Weight');
    #Move onto the next new figure, reset the X and Y lists and repeat
    plt.figure(3); relationX.clear(); relationY.clear()
    for i in range(1,netNumRuns):
        #Set x and y values based on elevation and weight
        if netPathMatrix[netPathDesired][1][i][0] < 10000:
            #Do not consider weight in relation if too extreme of a value
            relationX.append(netPathMatrix[netPathDesired][1][i][4])
            relationY.append(netPathMatrix[netPathDesired][1][i][0])
    relationData.append(numpy.polyfit(relationX, relationY, 1))
    #Display the best fit line equation
    tempData=relationData[len(relationData)-1].tolist()
    plt.text(relationX[round(len(relationX)/2)],relationY[round(len(relationY)/2)],'y = {0}x + {1}'.format(round(tempData[0],3),round(tempData[1],3)))
    plt.plot(relationX, numpy.poly1d(relationData[len(relationData)-1])(relationX))
    plt.scatter(relationX,relationY)
    plt.xlabel('Path Elevation'); plt.ylabel('Path Weight');
    #Move onto the next new figure, reset the X and Y lists and repeat
    plt.figure(4); relationX.clear(); relationY.clear()
    for i in range(1,netNumRuns):
        #Set x and y values based on time and weight
        if netPathMatrix[netPathDesired][1][i][0] < 10000:
            #Do not consider weight in relation if too extreme of a value
            relationX.append(netPathMatrix[netPathDesired][1][i][2])
            relationY.append(netPathMatrix[netPathDesired][1][i][0])
    relationData.append(numpy.polyfit(relationX, relationY, 1))
    #Display the best fit line equation
    tempData=relationData[len(relationData)-1].tolist()
    plt.text(relationX[round(len(relationX)/2)],relationY[round(len(relationY)/2)],'y = {0}x + {1}'.format(round(tempData[0],3),round(tempData[1],3)))
    plt.plot(relationX, numpy.poly1d(relationData[len(relationData)-1])(relationX))
    plt.scatter(relationX,relationY)
    plt.xlabel('Path Time'); plt.ylabel('Path Weight');
    #Move onto the next new figure, reset the X and Y lists and repeat
    plt.figure(5); relationX.clear(); relationY.clear()
    for i in range(1,netNumRuns):
        #Set x and y values based on fuel consumed and weight
        if netPathMatrix[netPathDesired][1][i][0] < 10000:
            #Do not consider weight in relation if too extreme of a value
            relationX.append(netPathMatrix[netPathDesired][1][i][5])
            relationY.append(netPathMatrix[netPathDesired][1][i][0])
    relationData.append(numpy.polyfit(relationX, relationY, 1))
    #Display the best fit line equation
    tempData=relationData[len(relationData)-1].tolist()
    plt.text(relationX[round(len(relationX)/2)],relationY[round(len(relationY)/2)],'y = {0}x + {1}'.format(round(tempData[0],3),round(tempData[1],3)))
    plt.plot(relationX, numpy.poly1d(relationData[len(relationData)-1])(relationX))
    plt.scatter(relationX,relationY)
    plt.xlabel('Fuel Consumed while traversing Path'); plt.ylabel('Path Weight');
    #Move onto the next new figure, reset the X and Y lists and repeat
    plt.figure(6); relationX.clear(); relationY.clear()
    for i in range(1,netNumRuns):
        #Set x and y values based on time and fuel consumed
        relationX.append(netPathMatrix[netPathDesired][1][i][2])
        relationY.append(netPathMatrix[netPathDesired][1][i][5])
    relationData.append(numpy.polyfit(relationX, relationY, 1))
    #Display the best fit line equation
    tempData=relationData[len(relationData)-1].tolist()
    plt.text(relationX[round(len(relationX)/2)],relationY[round(len(relationY)/2)],'y = {0}x + {1}'.format(round(tempData[0],3),round(tempData[1],3)))
    plt.plot(relationX, numpy.poly1d(relationData[len(relationData)-1])(relationX))
    plt.scatter(relationX,relationY)
    plt.xlabel('Path Time'); plt.ylabel('Fuel Consumed while traversing Path');
    #Finally, set the figure to a new entry for the model itself
    plt.figure(1)
    #Convert relationship output entries from numpy arrays to python lists
    for i in range(0,len(relationData)): relationData[i]=relationData[i].tolist()
    #Return the relationship data    
    return relationData