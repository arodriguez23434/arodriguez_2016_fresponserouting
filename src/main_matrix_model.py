#!/usr/bin/env python

from pylab import rcParams
import math
import networkx as nx
import matplotlib.pyplot as plt
from scipy.misc import imread
import func_network_operations as nop


"""
Objective:
o Calculate shortest path from one node in space to another using a robust
  model that can be later expanded upon for real-world problems.
"""

#--Configuration--
#loadFromFile: Boolean to allow parameters for file rather than manual entry
#fileDir = String pointing to file location if loading data from file; ignored if loadFromFile = False
loadFromFile = True
fileDir = 'files/helloworld.xlsx'
#The following can be ignored if loadFromFile = True
#nodeAttr: Key should be node name and the first two attributes must represent X and Y positions in the graph. Attributes should be in list format.
#nodeNeighbors: Must be list of 2D lists that are made of two node names in nodeAttr
#pathDesired: Must be a 2D tuple made of two node names in nodeAttr
nodeAttr = {'Station': [10,8], 'Jay-Bergman Field': [8,8], 'Softball Field': [10,6], 'CFE Arena': [8,6], 'Lake Claire': [6,6], 'Child Center': [8,4], 'Milican Hall': [6,4]}
pathDesired = ('Station','Milican Hall')
edgeAttr = {'Station,Jay-Bergman Field': [False,[1]]}
numRuns = 100
#edgeAttr: Key is Node1,Node2; X = Obstructed, Y = List of Times
#TODO: Get neighbors from keys
#TODO: obstructedEdges = [['A','B'],...]
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
        nop.calc_edge_weights(outGraph,nodeAttr,edgeAttr,numRuns)
    except KeyError:
        print("ERROR: Found node in nodeNeighbors that does not exist in nodeAttr!")
        return
    #Create a path matrix for the network
    pathMatrix = nop.matrix_create(outGraph,nodeAttr,numRuns);
    
    #-Main Operating Block-
    
    ##EXAMPLE: removing node 'C' then adding node 'D' and re-routing to there
    #try: pathMatrix = nop.network_remove_node('C',outGraph,nodeAttr,edgeAttr,nodePos,pathMatrix)    
    #except: print("ERROR: Failed to remove node (input error)")    
    #try: pathMatrix = nop.network_add_node('D',[1,2],['B','E'],outGraph,nodeAttr,edgeAttr,nodePos,pathMatrix)
    #except: print("ERROR: Failed to add node (input error)")    
    #pathDesired = ('B','E')
    
    #Print out the nodes and edges for debugging purposes
    #print("Dict\n---\nNodes\n{0}\n\nPos\n{1}\n".format(nodeAttr,nodePos))
    #print("Graph\n---\n\nNodes\n{0}\n\nEdges\n{1}\n".format(outGraph.nodes(data=True),outGraph.edges(data=True)))
    #print("Path Matrix\n{0}\n".format(pathMatrix))
    
    #-Graph Drawing-
    try:
        #Output the best path
        print("Best path to destination from {0} to {1} is to take {2}".format(pathDesired[0],pathDesired[1],pathMatrix[pathDesired][0][1]))
        #Set the image size in inches
        rcParams['figure.figsize'] = 10, 10
        #Define a list of colors that each edge will have based on route desired
        edge_colors = ['gray' if not i in pathMatrix[pathDesired][0][1] else 'green' for i in outGraph.edges()]
        #Set sizes of edges and nodes; edges scale based on whether or not in path
        edge_width = [4 if not i in pathMatrix[pathDesired][0][1] else 5 for i in outGraph.edges()]
        node_sizes = [500 for k in outGraph.nodes()]
        #Color nodes based on whether or not in path
        node_colors = [(0.7,0.7,0.7) for k in outGraph.nodes()]
        l = 0
        for k in outGraph.nodes():    
            for i,j in pathMatrix[pathDesired][0][1]:
                if i==k or j==k: node_colors[l] = (0.3,1,0.4)
            l+=1
        #Calculate the average 'weight' value for edges
        edge_avg_weight = 0
        for i in outGraph.edges(data=True):
            edge_avg_weight+=i[2]['distance']
        edge_avg_weight/=len(outGraph.edges())
        #Set labels for edges with position based on the average weight
        for k in outGraph.nodes():
            p = False #Set p based on whether or not in best path
            for i,j in pathMatrix[pathDesired][0][1]:
                if i==k or j==k: p = True
            #If in best path, highlight text
            if p==True: plt.text(nodePos[k][0],nodePos[k][1]+(edge_avg_weight*10),s=k,fontsize=14,bbox=dict(facecolor='green', alpha=0.5),horizontalalignment='center')
            else: plt.text(nodePos[k][0],nodePos[k][1]+(edge_avg_weight*10),s=k,fontsize=14,bbox=dict(facecolor='gray',alpha=0.5),horizontalalignment='center')
        edge_labels=dict([((u,v,),str(math.floor(d['weight']))) for u,v,d in outGraph.edges(data=True)])
    except:
        print("WARNING: Graph cannot display best path due to an error.")
        nx.draw(outGraph,nodePos)
    else:
        #Load Map Image
        img = imread('files/schematic_nolabels.png')
        plt.imshow(img, zorder=0, extent=[0, 100, 100, 0], aspect='auto')        
        #Set the graph title
        plt.title('Best Route from {0} to {1}'.format(pathDesired[0],pathDesired[1]),fontsize=18)
        #Draw the graph       
        nx.draw(outGraph,nodePos,node_color=node_colors,node_size=node_sizes,node_shape='s',linewidths=1.5,edge_color=edge_colors,width=edge_width)
        #Draw the edge labels
        nx.draw_networkx_edge_labels(outGraph,nodePos,edge_labels=edge_labels,label_pos=0.5) 
        #Draw information box
        plt.text(1,15,'Travel Time: {0} s\nTotal Distance: {1} mi\n# of Runs Tested: {2}\n'.format(round(pathMatrix[pathDesired][0][2],3),round(pathMatrix[pathDesired][0][3],3),numRuns),fontsize=12,bbox=dict(facecolor='green', alpha=0.5),horizontalalignment='left')        
        #Save the graph to an image file        
        plt.savefig('files/output.png')
        #Display the graph
        plt.show()
        #for i in range(0,numRuns): print('Run {0} - Best Path Time: {1}; Distance: {2}'.format(i,pathMatrix[pathDesired][1][i][2],pathMatrix[pathDesired][1][i][3]))
            
#--Execute Program--
nodeNeighbors = list();
#Check to see if we are using a file
if loadFromFile == True:
    fileType = nop.file_check(fileDir)
    #If the output isn't a bool, it's an excel workbook
    if type(fileType)!=bool: pathDesired = nop.file_excel_interpret(fileDir,fileType,nodeAttr,edgeAttr,nodeNeighbors,pathDesired)
#Before doing anything else, check user input for errors
netProceed = nop.check_user_input(nodeAttr,edgeAttr,nodeNeighbors,pathDesired,numRuns)
if netProceed == False: print("Please reconfigure the model to fix the issue(s) and try again.")
else: main()