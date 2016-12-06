#!/usr/bin/env python

from math import pow
from math import sqrt

def check_user_nodes(netNodeAttr):
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
    return True
    
def check_user_edges(netNodeAttr,netEdgeAttr,netNodeNeighbors):
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
    return True
    
def check_user_distances(netNodeAttr,netNodeNeighbors):
    #Set the number of standard deviations permitted
    #One to error out and the other to warn the user
    std_allowed = 3; std_warn = 1.5
    #Make a list of all the distances between connected nodes
    temp_dist = list(); temp_dist_ref = list(); i_iter = 0;
    node1 = [0,0]; node2 = [0,0]; temp_avg = 0; temp_std = 0
    #Iterate through each connected neighbor and store the nodes
    for i,j in netNodeNeighbors:
        for k in netNodeAttr.items():
            if i==k[0]: node1=[k[1][0],k[1][1],k[0]];
            elif j==k[0]: node2=[k[1][0],k[1][1],k[0]];
        #Calculate the distance between the two nodes
        dist = sqrt(pow(node2[1]-node1[1],2)+pow(node2[0]-node1[0],2))
        #Store the difference and the nodes' references
        temp_dist.append(dist)
        temp_dist_ref.append([node1[2],node2[2]])
        #Sum the distances
        temp_avg+=dist
    #Calculate the average distance
    temp_avg = temp_avg/len(temp_dist)
    #Calculate the variance of the distances
    for i in temp_dist: temp_std+=pow((i-temp_avg),2)
    #Calculate the standard deviation of the distances
    temp_std = sqrt(temp_std/(len(temp_dist)-1))
    #Check the distances to see if they fall within control limits
    for i in temp_dist:
        if i > (temp_avg+(std_warn*temp_std)):
            #If the value is outside the number of allowed standard deviations, it will take too many resources to render
            if i > (temp_avg+(std_allowed*temp_std)):  print("ERROR: Distance between nodes {0} and {1} is too large! ({2} >> {3})".format(temp_dist_ref[i_iter][0],temp_dist_ref[i_iter][1],i,temp_avg)); return False        
            #If it is outside warning standard deviation, warn the user but do not stop the process
            else: print("WARNING: Distance between nodes {0} and {1} is large! ({2} is >{3} sigma from {4})".format(temp_dist_ref[i_iter][0],temp_dist_ref[i_iter][1],i,std_warn,temp_avg))        
        elif i < (temp_avg-(std_warn*temp_std)):
            #If the value is outside the number of allowed standard deviations, it will take too many resources to render
            if i < (temp_avg-(std_allowed*temp_std)):  print("ERROR: Distance between nodes {0} and {1} is too large! ({2} >> {3})".format(temp_dist_ref[i_iter][0],temp_dist_ref[i_iter][1],i,temp_avg)); return False  
            #If it is outside warning standard deviation, warn the user but do not stop the process
            else: print("WARNING: Distance between nodes {0} and {1} is large! ({2} is >{3} sigma from {4})".format(temp_dist_ref[i_iter][0],temp_dist_ref[i_iter][1],i,std_warn,temp_avg))        
        #Iterate through each set of nodes
        i_iter+=1
    #If no issues appear, proceed
    return True

def check_user_path(netNodeAttr,netPathDesired,netStationNode,netFreqExists,netFreqTimes):
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
    #Are the frequency times valid?
    try:
        if type(netFreqExists)!=bool: 
            print("ERROR: Frequency list confirmation was improperly setup! (Not a boolean)")
            raise TypeError
        elif (netFreqExists==True):
            if type(netFreqTimes)!=list:
                print("ERROR: Frequency list was improperly setup! (Not a list)")
                raise TypeError          
            elif len(netFreqTimes)!=24:
                print("ERROR: Frequency list was improperly setup! ({0} values instead of 24)".format(len(netFreqTimes)))
                raise IndexError                 
    except: return False;
    #Do the nodes in the path desired exist?
    node_occur_a = 0; node_occur_b = 0; node_occur_station = 0
    for i in netNodeAttr.keys():
        if i == netPathDesired[0]: node_occur_a+=1
        elif i == netPathDesired[1]: node_occur_b+=1
        if i == netStationNode: node_occur_station+=1
    if node_occur_a<=0:
        print("ERROR: Start node %s on desired route does not exist!" % netPathDesired[0])
        return False;
    elif node_occur_b<=0:
        print("ERROR: End node %s on desired route does not exist!" % netPathDesired[1])
        return False;
    elif node_occur_station<=0:
        print("ERROR: Station node %s on desired route does not exist!" % netPathDesired[1])
        return False;
    #If no issues appear, proceed
    return True
        
#Check numerical configuration inputs
def check_user_config(netNumRuns,netObstructChance,netFuelStart,netTimeStart,netPathType):
    errorvar = ""  
    try:
        #Are the configurable inputs the correct type?     
        if type(netNumRuns)!=int: errorvar = "netNumRuns"; raise TypeError
        if type(netObstructChance)!=float and type(netObstructChance)!=int: errorvar = "netObstructChance"; raise TypeError
        if type(netFuelStart)!=float and type(netFuelStart)!=int: errorvar = "netFuelStart"; raise TypeError
        if type(netTimeStart)!=float and type(netTimeStart)!=int: errorvar = "netTimeStart"; raise TypeError
        #If the input is the correct type, is the value valid?        
        elif (netTimeStart>=1440): 
            errorvar = "netTimeStart";
            print("ERROR: Start time is invalid! ({0} >= 1440)".format(netTimeStart))            
            raise IndexError
        #Are the configurable inputs the correct type?
        if type(netPathType)!=int: errorvar = "netPathType"; raise TypeError
        #If the input is the correct type, is the value valid?         
        elif (netPathType>=2): 
            errorvar = "netPathType";
            print("ERROR: Invalid path type! (Must be 0 or 1; user entered {0})".format(netPathType))
            raise IndexError
    #If not, print an error message
    except TypeError: 
        print("ERROR: Numerical value {0} was improperly setup! (Not an integer/float)".format(errorvar))
        return False;
    except IndexError:
        print("ERROR: Numerical value {0} was improperly setup! (Not an acceptable value)".format(errorvar))
        return False;        
    #If no issues appear, proceed
    return True

def check_user_input(netNodeAttr,netEdgeAttr,netNodeNeighbors,netPathDesired,netNumRuns,netStationNode,netObstructChance,netFuelStart,netTimeStart,netPathType,netFreqExists,netFreqTimes):
    #Check every portion of the user input for validity and reasonability
    if (check_user_nodes(netNodeAttr)==False): return False
    if (check_user_edges(netNodeAttr,netEdgeAttr,netNodeNeighbors)==False): return False
    if (check_user_distances(netNodeAttr,netNodeNeighbors)==False): return False
    if (check_user_path(netNodeAttr,netPathDesired,netStationNode,netFreqExists,netFreqTimes)==False): return False
    if (check_user_config(netNumRuns,netObstructChance,netFuelStart,netTimeStart,netPathType)==False): return False
    #Check if the number of iterations is reasonable
    if netNumRuns < 1:
        print("ERROR: Number of times to run program is less than 1 (input %d)!" % netNumRuns)
        return False;
    elif netNumRuns > 1000: print("WARNING: Large number of times to run program (input %d)!" % netNumRuns)
    return True;
