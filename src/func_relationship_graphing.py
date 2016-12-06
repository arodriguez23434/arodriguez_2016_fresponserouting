#!/usr/bin/env python

import numpy
import pylab
import matplotlib.pyplot as plt

def lineAndLabel(labelType,netPathMatrix,netNodeAttr,yparam,netNumRuns,xlabelparam,ylabelparam,figureiter):
    #Set the matplotlib figure to a new figure and setup x and y values
    canvas = plt.figure(figureiter,figsize=(10,10)); 
    #Define the matrix of 1x1 to place subplots
    #Place the subplot on 1x1 matrix, at pos 1
    sp = canvas.add_subplot(1,1,1, axisbg='w')
    pylab.xlim([0,netNumRuns+(netNumRuns/4)])
    #Iterate through every possible combination of paths
    keyList = list(); keyMap = list(); keyRepeat = False; numElements = 0; largestVal = 0; smallestVal = False
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
            numElements += 1; keySum = 0; keySumSqr = 0; keyVar = 0
            for runIter in range(0,netNumRuns):
                #Graph Type 0: Raw values
                if labelType == 0:
                    #Determine the value for the iteration
                    val = netPathMatrix[(i,j)][1][runIter][yparam]
                    #Map the iteration value to the y value and the run to the x value
                    relationY.append(val)
                    relationX.append(runIter)
                    #If on the final run, label the graph with the type
                    if runIter == netNumRuns-1: sp.set_title("Sensitivity Analysis: Values")
                #Graph type 1: Averages
                elif labelType == 1:
                    #Determine the average for the number of iterations so far
                    val = netPathMatrix[(i,j)][1][runIter][yparam]
                    keySum += val
                    #Map the average to the y value and the run to the x value
                    relationY.append(keySum/(runIter+1))
                    relationX.append(runIter)
                    #If on the final run, label the graph with the type
                    if runIter == netNumRuns-1: sp.set_title("Sensitivity Analysis: Averages")
                #Graph type 2: Range
                elif labelType == 2:
                    #Determine the value for the iteration
                    val = netPathMatrix[(i,j)][1][runIter][yparam]
                    #Record the largest and smallest value among all paths
                    if val > largestVal: largestVal = val
                    if type(smallestVal)!=type(1): smallestVal = val
                    elif val < smallestVal: smallestVal = val
                    #Determine the range
                    keyRange = largestVal-smallestVal
                    #If this is the second iteration, set the first value to the be the same for consistency
                    if runIter==1: relationY[0] = keyRange
                    #Map the range to the y value and the run to the x value
                    relationY.append(keyRange)
                    relationX.append(runIter)
                    #If on the final run, label the graph with the type
                    if runIter == netNumRuns-1: sp.set_title("Sensitivity Analysis: Range")
                #Graph type 3: Largest Value
                elif labelType == 3:
                    #Determine the value for the iteration
                    val = netPathMatrix[(i,j)][1][runIter][yparam]
                    #Record the largest value among all paths for display text sorting
                    if val > largestVal: largestVal = val
                    #Map the largest value to the y value and the run to the x value
                    relationY.append(largestVal)
                    relationX.append(runIter)
                    #If on the final run, label the graph with the type
                    if runIter == netNumRuns-1: sp.set_title("Sensitivity Analysis: Largest Value")
                #Graph type 4: Smallest Value
                elif labelType == 4:
                    #Determine the value for the iteration
                    val = netPathMatrix[(i,j)][1][runIter][yparam]
                    #Record the smallest value among all paths for display text sorting
                    if type(smallestVal)!=type(1): smallestVal = val
                    elif val < smallestVal: smallestVal = val                    
                    #Map the smallest value to the y value and the run to the x value
                    relationY.append(smallestVal)
                    relationX.append(runIter)
                    #If on the final run, label the graph with the type
                    if runIter == netNumRuns-1: sp.set_title("Sensitivity Analysis: Smallest Value")
                #Graph type 5: Variances
                elif labelType == 5:
                    #Determine the average for the number of iterations so far
                    val = netPathMatrix[(i,j)][1][runIter][yparam]
                    keySum += val; keySumSqr += pow(val,2)
                    keyVar = (keySumSqr - (pow(keySum,2)/(runIter+1)))
                    if runIter!=0:                    
                        #Map the average to the y value and the run to the x value
                        relationY.append(keyVar/(runIter))
                    else: relationY.append(keyVar/(runIter+1))
                    relationX.append(runIter)
                    #If on the final run, label the graph with the type
                    if runIter == netNumRuns-1: sp.set_title("Sensitivity Analysis: Variances")
            #Generate a random color and convert to a hex string
            colorRand = (255*numpy.random.uniform(0,1),255*numpy.random.uniform(0,1),255*numpy.random.uniform(0,1))
            colorRandStr = '#'+colorRand[0].hex()[4:6]+colorRand[1].hex()[4:6]+colorRand[2].hex()[4:6]
            #Record the path, color generated and last value for display purposes
            keyMap.append([i,j,colorRandStr,relationY[netNumRuns-1]])    
            #Plot the specific graph on the subplot
            sp.plot(relationX, relationY, colorRandStr, linewidth=2)
    #Sort out all text labels from top to bottom
    i_iter = 0; keyMapSorted = list()
    print("Sorting out text labels for figure {0}...".format(figureiter)) 
    while len(keyMap)>0:
        largestKey = [0,0,0,0]; smallestKey = [0,0,0,0]; i_iter +=1
        for i in keyMap:
            if i[3] > largestKey[3]: largestKey = i
        keyMapSorted.append(largestKey)
        try: keyMap.remove(largestKey)
        except: print("ERROR: Could not remove largestKey {0}".format(largestKey))
        if i_iter>50: raise(IndexError)
    #Find the largest and smaller keys in the sorted map
    largestKey = [0,0,0,0]; smallestKey = [0,0,0,0];
    for i in keyMapSorted:
        if i[3] > largestKey[3]: largestKey = i
        elif i[3] < smallestKey[3]: smallestKey = i        
    i_iter = 0;
    for i in keyMapSorted:
        #Display the text labels; ordered from top to bottom and uniformly distributed
        i_iter+=1
        if len(keyMapSorted)>0:
            if labelType!=3: sp.text((netNumRuns-1)+((netNumRuns-1)/5),largestKey[3]-((i_iter-1)*((largestKey[3]-smallestKey[3])/(len(keyMapSorted)+1))),'{0} to {1}'.format(i[0],i[1]),bbox={'facecolor':i[2], 'alpha':0.5, 'pad':10}, color = 'black',horizontalalignment='right')
            else: sp.text((netNumRuns-1)+((netNumRuns-1)/5),largestKey[3]-((i_iter-1)*((largestKey[3]-smallestKey[3])/(len(keyMapSorted)+2))),'{0} to {1}'.format(i[0],i[1]),bbox={'facecolor':i[2], 'alpha':0.5, 'pad':10}, color = 'black',horizontalalignment='right')
    # Put the title and labels
    sp.set_xlabel(xlabelparam)
    sp.set_ylabel(ylabelparam)
    # Show the plot/image
    plt.tight_layout()
    plt.grid(alpha=0.8)
    print("Saving figure {0}...".format(figureiter))
    #Save the figure to an image file
    plt.savefig("files/sensitivity{0}.png".format(figureiter-1))
    #Output the relationship data
    relationData = [relationX,relationY]
    return relationData
    
def relationshipGraphSetup(netPathMatrix,netNodeAttr,netNumRuns):
    #Setup variable for outputting relationship data
    relationData = list()
    #Iterate through each figure for its own graph output type  
    figureiter = 1
    for graphiter in range(2,4):
        #Set the parameters each graph will use and their respective labeling
        for typeiter in range(0,6):
            figureiter+=1
            if (graphiter==2): 
                labelType = typeiter; yparam = 2; xlabel = 'Monte-Carlo Runs'; ylabel = 'Expected Path Time'
            elif (graphiter==3): 
                labelType = typeiter; yparam = 5; xlabel = 'Monte-Carlo Runs'; ylabel = 'Expected Fuel Consumed on Path'
            #Plot out the points, make a best-fit line, and save the relationship data
            #print(graphiter,typeiter,graphiter*(typeiter+1))
            relationData = lineAndLabel(labelType,netPathMatrix,netNodeAttr,yparam,netNumRuns,xlabel,ylabel,figureiter)
    #Finally, set the figure to a new entry for the model itself
    plt.figure(1)
    #Return the relationship data    
    keyList = list(); 
    for i in netNodeAttr.keys():
        keyList.append(i); keyRepeat = False
        for j in netNodeAttr.keys():
            #Do not map paths that have already been mapped in reverse
            for k in keyList: 
                if j == k: keyRepeat = True; break
            #Do not map paths that have the same destinaton and source
            if i == j or keyRepeat == True: keyRepeat = False; continue
    return relationData