#!/usr/bin/env python

import numpy
import pylab
import matplotlib.pyplot as plt
from statistics import mean

def lineAndLabel(netPathMatrix,netNodeAttr,yparam,netNumRuns,xlabelparam,ylabelparam,figureiter):
    #Set the matplotlib figure to a new figure and setup x and y values
    canvas = plt.figure(figureiter,figsize=(10,10)); 
    #Define the matrix of 1x1 to place subplots
    #Place the subplot on 1x1 matrix, at pos 1
    sp = canvas.add_subplot(1,1,1, axisbg='w')
    pylab.xlim([0,netNumRuns+(netNumRuns/4)])
    #Iterate through every possible combination of paths
    keyList = list(); keyMap = list(); keyRepeat = False; numElements = 0; largestVal = 0; keyVals = list()
    for i in netNodeAttr.keys():
        keyList.append(i); keyRepeat = False
        for j in netNodeAttr.keys():
            #Do not map paths that have already been mapped in reverse
            for k in keyList: 
                if j == k: keyRepeat = True; break
            #Do not map paths that have the same destinaton and source
            if i == j or keyRepeat == True: keyRepeat = False; continue
            #Iterate through every entry for every run to plot out points        
            relationX = list(); relationY = list()
            numElements += 1; keySum = 0
            #print("Determining averages for {0} to {1}...".format(i,j))
            for runIter in range(0,netNumRuns):
                #Determine the average for the number of iterations so far
                val = netPathMatrix[(i,j)][1][runIter][yparam]
                keySum += val
                #Map the average to the y value and the run to the x value
                relationY.append(keySum/(runIter+1))
                relationX.append(runIter)
                #Record the largest value among all paths for display text sorting
                if keySum/(runIter+1) > largestVal: largestVal = keySum/(runIter+1)
            #Generate a random color and convert to a hex string
            colorRand = (255*numpy.random.uniform(0,1),255*numpy.random.uniform(0,1),255*numpy.random.uniform(0,1))
            colorRandStr = '#'+colorRand[0].hex()[4:6]+colorRand[1].hex()[4:6]+colorRand[2].hex()[4:6]
            #Record the path, color generated and last value for display purposes
            keyMap.append([i,j,colorRandStr,relationY[netNumRuns-1]])    
            #Plot the specific graph on the subplot
            sp.plot(relationX, relationY, colorRandStr, linewidth=2)
    #Sort out all text labels from top to bottom
    i_iter = 0; keyMapSorted = list(); iterable = 0
    print("Sorting out text labels...")    
    while len(keyMap)>0:
        largestKey = [0,0,0,0]; iterable+=1
        for i in keyMap:
            if i[3] > largestKey[3]: largestKey = i
        keyMapSorted.append(largestKey)
        keyMap.remove(largestKey)
        if iterable>50: raise(IndexError)
    for i in keyMapSorted:
        #Display the text labels; ordered from top to bottom and uniformly distributed
        i_iter+=1
        sp.text(netNumRuns-1,largestVal-((i_iter-1)*25),'{0} to {1}'.format(i[0],i[1]),bbox={'facecolor':i[2], 'alpha':0.5, 'pad':10}, color = 'black',horizontalalignment='left')
    # Put the title and labels
    sp.set_xlabel(xlabelparam)
    sp.set_ylabel(ylabelparam)
    # Show the plot/image
    plt.tight_layout()
    plt.grid(alpha=0.8)
    print("Saving figure...")
    #Save the figure to an image file
    plt.savefig("files/sensitivity{0}.png".format(figureiter-1))
    #Output the relationship data
    relationData = [relationX,relationY]
    return relationData
    
def relationshipGraphSetup(netPathMatrix,netNodeAttr,netNumRuns):
    #Setup variable for outputting relationship data
    relationData = list()
    #Iterate through each figure for its own graph output type  
    #TODO: Currently causes program to hang when performed for fuel consumed; fix issue without losing modularity
    for figureiter in range(2,3):
        #Set the parameters each graph will use and their respective labeling
        if (figureiter==2): 
            yparam = 2; xlabel = 'Monte-Carlo Runs'; ylabel = 'Destination Time'
        elif (figureiter==3): 
            yparam = 5; xlabel = 'Monte-Carlo Runs'; ylabel = 'Fuel Consumed on Path'
        #Plot out the points, make a best-fit line, and save the relationship data
        relationData = lineAndLabel(netPathMatrix,netNodeAttr,yparam,netNumRuns,xlabel,ylabel,figureiter)
    #Finally, set the figure to a new entry for the model itself
    plt.figure(1)
    #Return the relationship data    
    return relationData