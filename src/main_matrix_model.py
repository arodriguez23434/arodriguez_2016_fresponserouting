#!/usr/bin/env python

from pylab import rcParams
from math import floor
from scipy.misc import imread
from numpy import random
import networkx as nx
import matplotlib.pyplot as plt
import func_network_operations as nop
from func_relationship_graphing import relationshipGraphSetup
from func_check_input import check_user_input

"""
Objective:
o Calculate shortest path from one node in space to another using a robust
  model that can be later expanded upon for real-world problems.
"""

#--Configuration--

#loadFromFile: If 1, load data from Excel spreadsheet; if 2, have inputs.txt override certain variables; if 3, load only inputs.txt and not the Excel spreadsheet; if 0, use configuration below
loadFromFile = 1
#fileDir: String pointing to file location if loading data from file; ignored if loadFromFile = False
fileDir = 'files/helloworld.xlsx'
inputDir = 'files/inputs.txt'

#imageDir: String pointing to the location of the map image; this will be loaded regardless of loadFromFile's value
imageDir = 'files/schematic_nolabels.png'

#The following can be ignored if loadFromFile =/= 0
#-
#nodeAttr: Key should be node name and the first two attributes must represent X and Y positions in the graph. Attributes should be in list format.
nodeAttr = {'Station': [10,8], 'Jay-Bergman Field': [8,8], 'Softball Field': [10,6], 'CFE Arena': [8,6], 'Lake Claire': [6,6], 'Child Center': [8,4], 'Milican Hall': [6,4]}
#pathDesired: Must be a 2D tuple made of two node names in nodeAttr
pathDesired = ('Station','Milican Hall')
#stationNode: Node that marks where the origin/recharging station is located
stationNode = 'Station'
#edgeAttr: Key should be two node names separated by a comma (no space), first value is obstruction and second is a list of times it takes to travel along the edge.
edgeAttr = {'Station,Jay-Bergman Field': [False,[1]]}
#numRuns: Integer of number of times the program should run before determining best path
numRuns = 100
#obstructChance: Global floating point chance of a road being obstructed during calculation
obstructChance = 0.1
#fuelStart: Amount of fuel that a fully charged vehicle will initially have
fuelStart = 120
#timeStart: The beginning hours of operation for the vehicle (in seconds, e.g. 12:00PM = 720s)
timeStart = 720
#pathType: Whether we should consider a time-efficient (0) or fuel-efficient (1) path
pathType = 0
#-
#Set the image size in inches; must be two floats seperated by a comma
rcParams['figure.figsize'] = 10, 10

#--End of Configuration--


#--Main Function--

#If there are no issues, proceed
def init():
    #-Initialization-
    
    #Set the amount of current fuel to the starting fuel
    fuelCurr = fuelStart
    #Set the current time to the starting operation time
    timeCurr = timeStart
    #Create a position dictionary from first two attributes of user-defined dictionary
    #Acts as input for NetworkX draw functions
    nodePos = nodeAttr.fromkeys(nodeAttr.keys(),[0,0])
    for key in nodeAttr: nodePos[key] = [nodeAttr[key][0],nodeAttr[key][1]];
    #Set up the NetworkX graph object for output
    outGraph = nx.Graph()
    #The nodes are identified based on keys/node names by user
    outGraph.add_nodes_from(nodePos.keys())
    #Add all connecting neighbors as NetworkX edges
    outGraph.add_edges_from(nodeNeighbors)
    #Add NetworkX attributes for nodes and edges
    for i, p in nodePos.items(): 
        outGraph.node[i]['pos'] = p;
    try:
        #NetworkX uses a universal 'weight' attribute for edges for its algorithms
        nop.calc_edge_weights(outGraph,nodeAttr,edgeAttr,numRuns,obstructChance)
    except KeyError:
        print("ERROR: Found node in nodeNeighbors that does not exist in nodeAttr!")
        return
    #Create two path matrices for the network: one for time efficency, the other for fuel efficiency
    nop.edge_weight_type(outGraph,edgeAttr,numRuns,0);
    timeMatrix = nop.matrix_create(outGraph,nodeAttr,numRuns);
    nop.edge_weight_type(outGraph,edgeAttr,numRuns,1);    
    fuelMatrix = nop.matrix_create(outGraph,nodeAttr,numRuns);
    #Set counter for number of times operations have occurred
    numOps = 1
    
    #Place all initialized data into a list for the main function to interpret
    mainData = [fuelCurr,timeCurr,nodePos,outGraph,timeMatrix,fuelMatrix,numOps]
    return mainData
    
def main(mainData,pathType):    
    #-Main Operating Block-    
    
    #Get data from initialization
    fuelCurr = mainData[0]
    timeCurr = mainData[1]
    nodePos = mainData[2]
    outGraph = mainData[3]
    timeMatrix = mainData[4]   
    fuelMatrix = mainData[5]
    numOps = mainData[6]
    #Set the working path based on fuel efficency versus time efficiency
    if (pathType==0): pathMatrix = timeMatrix
    elif (pathType==1): pathMatrix = fuelMatrix
    
    #Setup relationship graphs
    #TODO: Prepare more suitable correlation graphs due to new weight system
    #relationshipGraphSetup(pathMatrix,pathDesired,numRuns);
    
    #EXAMPLE: removing node 'C' then adding node 'D' and re-routing to there
#    try: pathMatrix = nop.network_remove_node('Milican Hall',outGraph,nodeAttr,edgeAttr,nodePos,pathMatrix,numRuns)    
#    except: print("ERROR: Failed to remove node (input error)")    
#    try: 
#        addNode = 'Teaching Academy'
#        pathMatrix = nop.network_add_node(addNode,[12,60,28.597363,-81.203363,-5],{addNode+',Lake Claire': [False,[100,200]],addNode+',Early Childhood Center': [False,[100,200]]},outGraph,nodeAttr,edgeAttr,nodePos,pathMatrix,numRuns,obstructChance)
#    except: print("ERROR: Failed to add node (input error)")    
#    pathDesired = ('Fire Station','Teaching Academy')
        
    #Set the edges to the iteration of the path we want
    try: nop.iter_edges(outGraph,pathMatrix[pathDesired][2])  
    except: print("ERROR: Failed to properly retrieve weights from edges!")
    
    #Calculate response time and add to current operation time
    #TODO: Find literature or statistical data on time to respond to emergency while on location; using normal as a placeholder due to Central Limit Theorem
    timeConsume = random.normal(8,1.5,50)
    timeCurr += int(timeConsume[int(random.uniform(0,49))])
    #If past 23:59, subtract 24 hours from time to reset clock
    if (timeCurr>=1440): timeCurr-=1440
    #Decrease the amount of vehicle fuel available based on travel
    fuelCurr -= abs(pathMatrix[pathDesired][0][5]/1000)
    
    #-Graph Drawing-
    try:
        #Output the best path
        print("Best path to destination from {0} to {1} is to take {2}".format(pathDesired[0],pathDesired[1],pathMatrix[pathDesired][0][1]))
        #Define a list of colors that each edge will have based on route desired
        edge_colors = ['gray' if not i in pathMatrix[pathDesired][0][1] else 'green' for i in outGraph.edges()]
        #Set sizes of edges and nodes; edges scale based on whether or not in path
        edge_width = [4 if not i in pathMatrix[pathDesired][0][1] else 5 for i in outGraph.edges()]
        node_sizes = [500 for k in outGraph.nodes()]
        #Color nodes based on whether or not in path
        #Create a list with the number of entries as the number of nodes and set it to a gray color tuple
        node_colors = [(0.7,0.7,0.7) for k in outGraph.nodes()]
        #Setup temporary iterable variable
        l = 0
        for k in outGraph.nodes():
            #If the node is node is in the path, set the color tuple to a new value
            for i,j in pathMatrix[pathDesired][0][1]:
                if i==k or j==k: node_colors[l] = (0.3,1,0.4)
            #Iterate through the next entry of the list
            l+=1
        #Calculate the average 'distance' value for edges
        edge_avg_distance = 0
        for i in outGraph.edges(data=True): edge_avg_distance+=i[2]['distance']
        edge_avg_distance/=len(outGraph.edges())
        #Set labels for edges with position based on the average weight
        for k in outGraph.nodes():
            p = False #Set p based on whether or not in best path
            for i,j in pathMatrix[pathDesired][0][1]:
                if i==k or j==k: p = True
            #If in best path, highlight text
            if p==True: plt.text(nodePos[k][0],nodePos[k][1]+(edge_avg_distance*10),s=k,fontsize=14,bbox=dict(facecolor='green', alpha=0.5),horizontalalignment='center')
            else: plt.text(nodePos[k][0],nodePos[k][1]+(edge_avg_distance*10),s=k,fontsize=14,bbox=dict(facecolor='gray',alpha=0.5),horizontalalignment='center')
        edge_labels=dict([((u,v,),str(floor(d['weight']))) for u,v,d in outGraph.edges(data=True)])
    except:
        print("WARNING: Graph cannot display best path due to an error.")
        nx.draw(outGraph,nodePos)
    else:
        #Load Map Image
        img = imread(imageDir)
        plt.imshow(img, zorder=0, extent=[0, 100, 100, 0], aspect='auto')        
        #Set the graph title
        if (pathType==0): plt.title('Quickest Route from {0} to {1}'.format(pathDesired[0],pathDesired[1]),fontsize=18)
        elif (pathType==0): plt.title('Most Fuel-Efficient Route from {0} to {1}'.format(pathDesired[0],pathDesired[1]),fontsize=18)
        #Draw the graph       
        nx.draw(outGraph,nodePos,node_color=node_colors,node_size=node_sizes,node_shape='s',linewidths=1.5,edge_color=edge_colors,width=edge_width)
        #Draw the edge labels
        nx.draw_networkx_edge_labels(outGraph,nodePos,edge_labels=edge_labels,label_pos=0.5) 
        #Draw information box
        plt.text(1,15,'Travel Time: {0} s\nTotal Distance: {1} mi\nDelta Elevation: {2} in\n# of Runs Tested: {3}\nPower Used: {4} kW'.format(round(pathMatrix[pathDesired][0][2],3),round(pathMatrix[pathDesired][0][3],3),round(pathMatrix[pathDesired][0][4],3),numRuns,round(pathMatrix[pathDesired][0][5]/1000,3)),fontsize=12,bbox=dict(facecolor='green', alpha=0.5),horizontalalignment='left')        
        #Save the graph to an image file        
        plt.savefig('files/output.png')
        #Display the graph
        plt.show()

    #Update all data inputs to allow for carryover into new iterations
    mainDataUpdate = [fuelCurr,timeCurr,nodePos,outGraph,timeMatrix,fuelMatrix,numOps]
    return mainDataUpdate        
    
#--End of Main Function--        
        
#--Program Execution--

#Setup list to associate nodes together in edges
nodeNeighbors = list();
#Check to see if we are using files rather than code for input
if loadFromFile:
    try: loadFromFile+=0
    except: print("ERROR: loadFromFile not set to a number! (Type is currently {0})".format(type(loadFromFile)))
    else:
        #Ensure the files are properly loaded and are the correct type
        #Load the excel file if we are permitting it to be loaded        
        if loadFromFile>0 and loadFromFile<3:
            fileType = nop.file_check(fileDir)
            #Ensure that the file is real and the correct type
            if type(fileType)!=bool: 
                if fileType[0]=='excel':
                    #Obtain info from excel spreadsheet
                    fileInfo = nop.file_excel_interpret(fileDir,fileType[1],nodeAttr,edgeAttr,nodeNeighbors,pathDesired,numRuns,obstructChance)
                    pathDesired = fileInfo[0]; numRuns = fileInfo[1]; obstructChance = fileInfo[2]
                    #Since we loaded from file, assume station node is the starting node in the 1st path
                    stationNode = pathDesired[0]
        #Load the inputs.txt file if we are permitting it to be loaded 
        if loadFromFile>1: 
            inputType = nop.file_check(inputDir)
            #Ensure that the file is real and the correct type
            if type(inputType)!=bool: 
                if inputType[0]=='txt':
                    #Obtain info from inputs.txt
                    fileInfo = nop.file_inputs_interpret(inputDir,fileType[1],pathDesired,numRuns,obstructChance)
                    pathDesired = fileInfo[0]; numRuns = fileInfo[1]; obstructChance = fileInfo[2]
                    #Since we loaded from file, assume station node is the starting node in the 1st path
                    stationNode = pathDesired[0]
                    
#Before doing anything else, check user input for errors
netProceed = check_user_input(nodeAttr,edgeAttr,nodeNeighbors,pathDesired,numRuns,stationNode)
#If there are critical errors in the input, end the program
if netProceed == False: print("Please reconfigure the model to fix the issue(s) and try again.")
#If there are no errors, continue
else: 
    #Perform initialization
    mainData = init(); 
    #Initialize analysis variables
    timeList = list(); fuelList = list()
    #Initialize program exit variable
    wantClose = False
    #Set default user input variable
    userResponse = 'y'
    #Perform main operations
    while wantClose == False:
        #If we have finished an operation, prompt the user to continue
        if (mainData[6]>1):
            print("\n[Input Required] Continue operations? (Y/N): ")
            userResponse = input()
        #If the user wants to continue, repeat operations
        if userResponse.lower()=='y': 
            #Before performing main operations, check if we were given a destination
            if pathType == 2:
                #If it was determined that our next path cannot be determined, warn the user that results are inaccurate
                print("WARNING: No call frequency data was provided; results will not be accurate!")
                #Ask the user for next location
                print("[Input Required] Please type the next location to travel to:")
                #Continously prompt the user until a node in the map or "exit" is given            
                while True:
                    userResponse = input("");
                    if userResponse.lower() == "exit": exit(); break;
                    for i in nodeAttr.keys():
                        if i.lower() == userResponse.lower(): destNode = i; break;
                    if destNode == i: break
                    print("Location {0} not found. Please try again.".format(userResponse))
                pathDesired = (pathDesired[0],destNode)
                #Set suggsted path type to time-based; typical default state for unpredictable emergencies
                pathType = 0
            #Perform all main operations
            mainData = main(mainData,pathType)        
            #For reporting purposes, break down operation seconds into military time
            timeHour = floor(mainData[1]/60)
            timeMinute = floor(60*((mainData[1]/60)-timeHour))
            #Calculate the average and standard deviation of time and energy for all operations so far
            if (pathType==0): timeList.append(mainData[4][pathDesired][0][2]); fuelList.append(mainData[5][pathDesired][0][5]/1000)
            elif (pathType==1): timeList.append(mainData[4][pathDesired][0][2]); fuelList.append(mainData[5][pathDesired][0][5]/1000)          
            #Print the report
            print("\n---Report---\n")
            #Print possible paths and path chosen
            print("Quickest Path: {0}s, {1}kW".format(round(mainData[4][pathDesired][0][2],5),round(mainData[4][pathDesired][0][5]/1000,5)))
            print("Fuel-Efficient Path: {0}s, {1}kW".format(round(mainData[5][pathDesired][0][2],5),round(mainData[5][pathDesired][0][5]/1000,5)))
            if (pathType==0): print("Path Chosen: Quickest ({0}% Confidence)".format(round(((mainData[4][pathDesired][3])/numRuns)*100,3)))
            elif (pathType==1): print("Path Chosen: Fuel-Efficient ({0}% Confidence)".format(round(((mainData[5][pathDesired][3])/numRuns)*100,3)))
            #Print current vehicle/operation status
            if (timeMinute<10): print("\nCurrent Time: {0}:0{1} ".format(timeHour,timeMinute))
            else: print("\nCurrent Time: {0}:{1} ".format(timeHour,timeMinute))
            print("Energy Remaining: {0} / {1} KW\nNumber of Operations Performed: {2}".format(round(mainData[0],6),fuelStart,mainData[6])) 
            print("\n------------")
            #Determine the next recommended destination (must be under report)         
            suggestInfo = nop.path_decide_destination(nodeAttr,mainData,fuelList,pathDesired,stationNode,False,"")
            pathDesired = suggestInfo[0]; pathType = suggestInfo[1] 
        #If user does not want to continue, exit program
        elif userResponse.lower()=='n' or userResponse.lower()=='exit' or userResponse.lower()=='quit': break; wantClose = True;
        #Input must be in form of y/n
        else: print("Invalid input. Please try again using Y or N.")
        #Iterate on the number of operations performed
        mainData[6]+=1;
        
#--End of Program--