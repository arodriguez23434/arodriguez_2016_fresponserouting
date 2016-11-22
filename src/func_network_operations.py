#!/usr/bin/env python

import math
import networkx as nx
import openpyxl as xl
from statistics import stdev
from statistics import mean
from numpy import random

#Function to calculate the fuel cost along an edge
def calc_fuel_cost(time,distance,elevation):
    #TODO: Calculation is currently placeholder; replace with suitable one
    #0.8 kwH/km; must be in units of kWS/mi
    #alternative formula: Fuel Consumption = 0.82 x (0.89/FTP + 0.11/US06) + 0.18/FTP + 0.133*1.083(1/SC03 - 1/FTP)
    # units in kWh/mile, where FTP, US06, HFET, and SC03 represent fuel consumption in kWh/mile for the related drive cycle
    # however, data for this is not available, so 0.8 kwH/km for large transit vehicles in Kyoto is preferred for this model
    activeConsume = 0.8*(0.621371/360); heightConsume = 2
    fuel_consumed = activeConsume*time
    #Could not find data on elevation as a factor for energy consumption!
    angle = math.asin(elevation/(distance*5280))
    fuel_consumed += abs(heightConsume*fuel_consumed*math.sin(angle))
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

#Iterate over generated times/weights based on normal distribution
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
        #Count the number of times the best path is repeated
        pathRepeats = 0
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
                if best_path[1]==pathinfo[1]: pathRepeats+=1;
                #Append the path to all potential paths
                all_paths.append(pathinfo)
            #If an error occurs, raise an exception
            else: raise nx.NetworkXNoPath()
        #If the path lists are valid, set the pathMatrix entry to them
        if best_path and all_paths: 
            pathMatrix[(i,j)] = [best_path,all_paths,saveIter,pathRepeats]
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
def network_add_node(node,addNodeAttr,addEdgeAttr,graph,netNodeAttr,netEdgeAttr,netNodePos,pathMatrix,netNumRuns,netObstructChance):
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
            try: calc_edge_weights(graph,netNodeAttr,netEdgeAttr,netNumRuns,netObstructChance)
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

def calc_edge_weights(graph,netNodeAttr,netEdgeAttr,netNumRuns,netObstructChance):
    for node1,node2 in graph.edges():
        #Try to get info about the edge from edgeAttr
        #Before throwing an exception, check if networkX ordered the key backwards
        try: edgeInfo=netEdgeAttr[str(node1+','+node2)]
        except KeyError: edgeInfo=netEdgeAttr[str(node2+','+node1)]
        #Get the average and standard deviation of recorded times
        timeAvg = mean(edgeInfo[1]); timeStd = stdev(edgeInfo[1]);
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
            weight_list.append(timeGen[i])
            #Obtain the fuel consumed
            fuelCost.append(calc_fuel_cost(timeGen[i],dist,heightdelta))
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

def edge_weight_type(graph,netEdgeAttr,netNumRuns,edgeType):
    for node1,node2 in graph.edges():
        #Try to get info about the edge from edgeAttr
        #Before throwing an exception, check if networkX ordered the key backwards
        try: edgeInfo=netEdgeAttr[str(node1+','+node2)]
        except KeyError: edgeInfo=netEdgeAttr[str(node2+','+node1)]
        #Scale the edge weights based on user input    
        for i in range(0,netNumRuns): 
            if (edgeType == 0):
                #Weigh based on time
                graph[node1][node2]['weight_list'][i] = graph[node1][node2]['time_list'][i]
            elif (edgeType == 1):
                #Weigh based on fuel
                #Using *1000 to scale display from W to kW
                graph[node1][node2]['weight_list'][i] = graph[node1][node2]['fuel_list'][i]*1000
            #If the road is obstructed, set weight to an invalid value
            #TODO: Currently it just sets the weight to a high value;
            #      Find suitable NetworkX substitute if possible
            if edgeInfo[0]==True: graph[node1][node2]['weight_list'][i] += 10000;
    return;

def path_decide_destination(netNodeAttr,mainData,timeList,fuelList,netPathDesired,netStationNode,netFreqExists,netFreqTimes,netFuelStart):
    #Initialize starting/destination nodes and path type recommendation
    startNode = netPathDesired[1]; destNode = netPathDesired[0]; pathTypeSuggest = 0; fuelAdd = 0
    #First, check if the vehicle has enough fuel to afford to go to another location
    if len(fuelList)>1: fuelCompare = mean(fuelList)+(3*stdev(fuelList));
    else: fuelCompare = fuelList[0]*2;
    #If we do not have frequency data
    if netFreqExists==False:
        #Set the suggested path type to 2 and handle the rest in the main function, as user input is required
        pathTypeSuggest = 2
    #If we do have frequency data
    elif netFreqExists==True:
        #Obtain the next hour
        timeHour = int(math.floor(mainData[1]/60))+1
        #If the next hour is midnight, reset the clock
        if timeHour>=24: timeHour-=24
        #Set a temporary variable to obtain whether an emergency event will likely occur
        eventOccur = 0; i = 0; prevChance = 0
        #Notify the user of the chance an emergency event will occur within the next 2 hours
        if timeHour>=23: c=netFreqTimes[timeHour]+netFreqTimes[0]
        else: c=netFreqTimes[timeHour]+netFreqTimes[timeHour+1]
        print("\nChance of emergency event: {0}%".format(round(c*100,5)))
        #Check if at station and not first time running
        if startNode == netStationNode and mainData[6]>1:
            #If at station, perform a while loop and get a random binomial distribution based on i trials
            while True:
                #Set an iterating variable i and a variable to track the "real" hour
                i+=1; j = timeHour+i; 
                #Until an emergency occurs, remain at the station and continously count the number of hours passed
                if j > 23:
                    j = math.floor(j/24)
                    j = (timeHour+i)-(j*24)
                    prevChance += netFreqTimes[j]
                    eventOccur = random.binomial(1,prevChance)
                else: 
                    prevChance += netFreqTimes[j]; 
                    eventOccur = random.binomial(1,prevChance)
                #If an emergency occurs, exit the loop
                if eventOccur >= 1: break
            #Notify user how much time has passed since previous emergency
            print("Predicted Time Elapsed until next emergency: {0} hours".format(i))
            mainData[1] = j*60
            #Add the amount of fuel restored in elapsed time
            #TODO: Replace placeholder fuel added with fuel added per hour based on time elapsed
            fuelAdd = i*0.1
            #Ensure fuel added does not exceed maximum capacity
            if mainData[0]+fuelAdd>netFuelStart: fuelAdd=(netFuelStart-mainData[0])
            print("Predicted Energy after Recharge: {0} / {1} kW (+{2} KW)".format(round(mainData[0]+fuelAdd,6),netFuelStart,round(fuelAdd,6)))
        else:
            #If not at station, just perform a binomial distribution sample for both the next hour and hour after
            eventOccur = random.binomial(1,netFreqTimes[timeHour])
            if timeHour>=23: eventOccur += random.binomial(1,netFreqTimes[timeHour]+netFreqTimes[0])
            else: eventOccur += random.binomial(1,netFreqTimes[timeHour]+netFreqTimes[timeHour+1])
        #If an emergency occurs, predict which location
        if eventOccur >= 1: 
            #Make a list of nodes and their probablities
            node_list = list(); node_eventChance = list()
            for key in netNodeAttr: node_list.append(key)
            for k in netNodeAttr.values(): node_eventChance.append(k[5])
            #Use weighted probability node attribute to determine where the emergency will occur
            destNode = random.choice(node_list,p = node_eventChance)
            print("Next emergency likely to occur at: {0}".format(destNode))
            #Determine which path type to use
            #If the vehicle does not have fuel within 3 standard deviations of all trips taken so far, bring back to station
            if fuelCompare>mainData[0]: 
                startNode = netPathDesired[1]; destNode = netStationNode; pathTypeSuggest = 3
                print("\nNOTE: FUEL IS LOW!\nDirecting to {0} on Fuel-Efficient path.".format(netStationNode))
            #If the vehicle has enough fuel, continue
            else:
                #If there is more than one emergency likely, then use the fastest route available
                if eventOccur > 1: pathTypeSuggest = 0
                #If there is only one emergency, test time difference
                else:
                    #If the amount of time it would take to use the fuel-efficient path is greater than average time+0.5 sigma, it's better to use the fastest route
                    if len(timeList)>1: timeCompare = mean(timeList)+(0.5*stdev(timeList));
                    else: timeCompare = fuelList[0]*2;
                    if (mainData[5][(startNode,destNode)][0][2] > timeCompare): 
                        pathTypeSuggest = 0
                        print("Recommended Path Type: Quickest")
                    else: 
                        pathTypeSuggest = 1
                        print("Recommended Path Type: Fuel-Efficient")
        #If an emergency does not occur, go to station and refuel
        else:
            startNode = netPathDesired[1]; destNode = netStationNode; pathTypeSuggest = 3
            print("No emergencies predicted to occur within the next hour.\nDirecting to {0} on Fuel-Efficient path.".format(netStationNode))
            #If the vehicle does not have fuel within 3 standard deviations of all trips taken so far, note fuel is low
            if fuelCompare>mainData[0]: print("NOTE: FUEL IS LOW!\n")
    #Set the location and path type suggested
    suggestInfo = [(startNode,destNode),pathTypeSuggest,fuelAdd]
    return suggestInfo

def file_check(netFileDir):
    #First check if the user entered an actual file name
    if len(netFileDir)<3: print("ERROR: Not a file!"); return False;
    #Next, check if the file is an excel workbook
    if netFileDir.lower().endswith(('.xlsx','.xlsm','.xltx','.xltm')):
        try:
            wb = xl.load_workbook(filename = netFileDir, data_only = True)
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

def file_excel_interpret(netFileDir,wb,netNodeAttr,netEdgeAttr,netNodeNeighbors,netPathDesired,netNumRuns,netObstructChance,netFuelStart,netTimeStart,netFreqTimes):
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
                netStationNode = (row[0].value)
                netNumRuns = row[2].value
                netObstructChance = row[3].value
                netFuelStart = row[4].value
                netTimeStart = row[5].value
                netInfo = [netPathDesired,netNumRuns,netObstructChance,netFuelStart,netTimeStart,netStationNode]
            except: print("ERROR: Failed to retrieve configuration data from spreadsheet 1!")
            continue
        for cell in row:
            #If the cell is in the label column, do not interpret
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
    #Load the 3rd worksheet in the excel workbook (FrequencyData)
    ws = wb.worksheets[2]  
    #Clear the old frequency list
    netFreqTimes = list()
    for row in ws.rows:
        #Create a temporary list of values for a row
        freq_values = list()
        #If the row is the label row, do not interpret
        if row[0].row == 1 or row[0].row > 25: continue   
        for cell in row:
            #If the cell is in the label column, do not interpret
            if cell.column == 'A': continue    
            if cell.value == None: print("WARNING: Cell {0}{1} in spreadsheet 3 has no value!".format(cell.row,cell.column));
            freq_values.append(cell.value)
        #Add the probabilities for each hour to the frequency list
        try: netFreqTimes.append(freq_values[2])
        except: print("ERROR: Failed to retrieve configuration data from spreadsheet 3!")
    #Add the frequency data to the output
    if (len(netFreqTimes)<24): print("WARNING: Less than 24 hours of frequency data was found!")
    netInfo.append(netFreqTimes)
    return netInfo;
    
def file_inputs_interpret(netFileDir,file,netPathDesired,netNumRuns,netObstructChance,netFuelStart,netTimeStart,netFreqTimes):
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
                elif 'fuelStart' in lineStr: netFuelStart=float(lineStr[12:])
                elif 'timeStart' in lineStr: netTimeStart=float(lineStr[12:])
    #Return the info provided
    netInfo = [netPathDesired,netNumRuns,netObstructChance,netFuelStart,netTimeStart]
    return netInfo;