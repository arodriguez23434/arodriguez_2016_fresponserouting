#!/usr/bin/env python

from pylab import rcParams
from math import floor
from scipy.misc import imread
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
#edgeAttr: Key should be two node names separated by a comma (no space), first value is obstruction and second is a list of times it takes to travel along the edge.
edgeAttr = {'Station,Jay-Bergman Field': [False,[1]]}
#numRuns: Integer of number of times the program should run before determining best path
numRuns = 100
#obstructChance: Global floating point chance of a road being obstructed during calculation
obstructChance = 0.1
#-
#Set the image size in inches; must be two floats seperated by a comma
rcParams['figure.figsize'] = 10, 10

#--End of Configuration--


#--Main Function--

#If there are no issues, proceed
def main():
    #-Initialization-
    
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
    #Create a path matrix for the network
    pathMatrix = nop.matrix_create(outGraph,nodeAttr,numRuns);
    #Setup relationship graphs
    relationshipGraphSetup(pathMatrix,pathDesired,numRuns);
    
    #-Main Operating Block-
    
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
        plt.title('Best Route from {0} to {1}'.format(pathDesired[0],pathDesired[1]),fontsize=18)
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
        
#--End of Main Function--        
        
#--Initial Program Execution--

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
        #Load the inputs.txt file if we are permitting it to be loaded 
        if loadFromFile>1: 
            inputType = nop.file_check(inputDir)
            #Ensure that the file is real and the correct type
            if type(inputType)!=bool: 
                if inputType[0]=='txt':
                    #Obtain info from inputs.txt
                    fileInfo = nop.file_inputs_interpret(inputDir,fileType[1],pathDesired,numRuns,obstructChance)
                    pathDesired = fileInfo[0]; numRuns = fileInfo[1]; obstructChance = fileInfo[2]

#Before doing anything else, check user input for errors
netProceed = check_user_input(nodeAttr,edgeAttr,nodeNeighbors,pathDesired,numRuns)
#If there are critical errors in the input, end the program
if netProceed == False: print("Please reconfigure the model to fix the issue(s) and try again.")
#If there are no errors, continue into the main function
else: main()

#--End of Initial Exceution--