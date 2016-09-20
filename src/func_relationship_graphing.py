#!/usr/bin/env python

import numpy
import matplotlib.pyplot as plt

def lineAndLabel(relationX,relationY,relationData,xlabelparam,ylabelparam,figureiter):
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
    plt.xlabel(xlabelparam); plt.ylabel(ylabelparam);
    #Move onto the next new figure, reset the X and Y lists and repeat
    plt.figure(figureiter+1); relationX.clear(); relationY.clear()
    return relationData

def relationshipGraphSetup(netPathMatrix,netPathDesired,netNumRuns):
    #Setup variable for outputting relationship data
    relationData = list()
    #Setup graphical outputs for correlation
    #Set the matplotlib figure to a new figure and setup x and y values
    plt.figure(2); relationX = list(); relationY = list(); figureiter = 2
    #Iterate through each figure for its own graph output type    
    for figureiter in range(2,7):
        #Set the parameters each graph will use and their respective labeling
        if (figureiter==2): 
            xparam = 3; yparam = 0; xlabel = 'Path Distance'; ylabel = 'Path Weight'
        elif (figureiter==3): 
            xparam = 4; yparam = 0; xlabel = 'Path Elevation'; ylabel = 'Path Weight'
        elif (figureiter==4): 
            xparam = 2; yparam = 0; xlabel = 'Path Time'; ylabel = 'Path Weight'
        elif (figureiter==5): 
            xparam = 5; yparam = 0; xlabel = 'Fuel Consumed while traversing Path'; ylabel = 'Path Weight'
        elif (figureiter==6): 
            xparam = 2; yparam = 5; xlabel = 'Path Time'; ylabel = 'Fuel Consumed while traversing Path'
        else: print("ERROR: Attempted to graph figure out of range"); break
        #Iterate through every entry for every run to plot out points        
        for i in range(1,netNumRuns):
            #Set x and y values based on distance and weight
            if netPathMatrix[netPathDesired][1][i][0] < 10000:
                #Do not consider weight in relation if too extreme of a value
                relationX.append(netPathMatrix[netPathDesired][1][i][xparam])
                relationY.append(netPathMatrix[netPathDesired][1][i][yparam])
        #Plot out the points, make a best-fit line, and save the relationship data
        relationData = lineAndLabel(relationX,relationY,relationData,xlabel,ylabel,figureiter)
    #Finally, set the figure to a new entry for the model itself
    plt.figure(1)
    #Convert relationship output entries from numpy arrays to python lists
    for i in range(0,len(relationData)): relationData[i]=relationData[i].tolist()
    #Return the relationship data    
    return relationData