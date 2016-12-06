Basic Usage
=====
Requirements
---
The usage of this model requires that Python 3.4 with Anaconda 3 is installed onto the system. If you do not have these installed already, please view https://www.continuum.io/downloads for more information.
---
Environment Setup
---
To set up the exact Python environment required for the model, open a command prompt/command line. Point to where the 'env' folder is located (the folder should contain a file called "environment.yml"). In the terminal, type (without the beginning >):
> conda env create -f environment.yml

If there are no errors, the environment will be created successfully and you can move onto the "Model Setup" section. 
    However, if an issue does occur, an alternative method of creating the environment can be used:
    > conda create --name test_networkx --file explicit-spec-file.txt
    This method explicitly links each package/dependency for Anaconda to install the environment.
---
Running the Model
---
After the model is properly configured, open a command prompt/command line and point to the location where main_matrix_model.py is located (src folder). Type (without the beginning >):
> activate test_networkx
> python main_matrix_model.py

This will activate the Python environment necessary for the model (loading all necessary packages/dependencies) and run the main python file responsible for running the program. If the model was properly configured, the program will print the best route from the starting location to the desired destination as well as visually display it.
=====

Configuring the Model
=====
From Excel Workbook
---
(An example of a finished workbook can be viewed at src\files\helloworld.xlsx)

To setup a model for analysis via Excel, create a blank workbook with two worksheets.

On the first worksheet, the A2 and B2 represent the desired Start Location and End Location respectively for the specific route you wish to model. For instance, if you want to map a path from 'Florida' to 'California', set A2 to Florida and B2 to California.
On this same worksheet, Rows 4 and beyond represent the actual locations and associated attributes. Column A is reserved specifically for the names of the locations (i.e. "Florida" "California"), and Columns B and C are reserved for the coordinates of the location (i.e. (10,-5) -> B2 = 10, C2 = -5). Columns D and beyond are any additional attributes associated with each location.

On the second worksheet, only columns A and B are used. Each row should contain the names of exactly two locations that are connected to one another. Columns C and beyond are not read! So for instance, to indicate that "Florida" and "Georgia" have a direction connection, set A1 to Florida and B1 to Atlanta. Note that connections are reciprocal - in other words, you do not need to input the same connection in reverse. (i.e. A1= "Florida" B1="Georgia" means that you do not need to have A2="Georgia" B2="Florida")

Once you have configured the model to your liking, save the file and run the model (see the "Basic Usage" section).
---
Manual Input
---
To manually setup a model for analysis, open main_matrix_model.py with a text editor or IDE of your choice. Under the line that says "#--Configuration--" will be several variables. 
 
nodeAttr is a dictionary of all the locations (or "nodes") that the model will consider. It also contains any special attributes about those locations (such as position). It should be written in the following format: " 'NodeName': [x coordinate, y coordinate, attribute1, attribute2, ...] " where 'NodeName' acts as a key (or "marker") and the attributes are in list format. A node MUST have an associated x and y coordinate in the first two entries - otherwise the model will fail to be able to perform calculations!
  Example: nodeAttr = {'A': [0,0], 'B': [2,0], 'C': [2,1]}

nodeNeighbors is a list that contains all the connections that each location has to one another. Location connections must be done in the form of a nested 2D list. In other words, you must have a connection in the form of [Location A, Location B]; you cannot make a connection in the form of [Location A, Location B, Location C]. Connections are two-way, so you do not need to make a seperate connection for an opposite route (i.e. [A,B] implies [B,A] is also a connection)
  Example: nodeNeighbors = [['A','B'],['B','C']]

pathDesired is a tuple between a starting location and ending location that is used to determine the best route to take between these two locations. This can change over time depending on your needs. Note that like nodeNeighbors, this must be between exactly two locations in the form of (Location A, Location B).
  Example: pathDesired = ('A','C')

Once you have configured the model to your liking, save the file, close the editor and run the model (see the "Basic Usage" section).
=====

Updating the Model
=====
(Note: Currently, the model does not operate continously, but this section has been created for when the program does so)
---
Addition/Removal of Nodes & Re-Routing
---
To add or remove a node during operation, functions within the main() can called. 

To remove a node, call the function pathMatrix = nop.network_remove_node(NODENAME,outGraph,nodeAttr,nodePos,pathMatrix), where NODENAME is replaced with a string of the name of the node that you wish to remove.

To add a node, call the function pathMatrix = nop.network_add_node(NODENAME,NODEATTRIBUTES,NODENEIGHBORS,outGraph,nodeAttr,nodePos,pathMatrix)
, where NODENAME is replaced with a string of the name of the node that you wish to remove, NODEATTRIBUTES is a list of attributes you wish to assign the node (the first two entries must be coordinates), and NODENEIGHBORS is a list of nodes that the new node will be linked to. Note that NODENEIGHBORS is a list of -other- nodes, so the correct format would be ['B','C'] instead of [['A','B'],['B','C']].

It it imperative that in both of these functions that "pathMatrix =" is at the beginning of the function calls - otherwise the matrix containing all the potential routes will not be updated accordingly!

To re-route the model path, simply change the variable pathDesired to a 2D tuple with the starting and ending locations. For instance, nodeNeighbors = ('A','B') will change the model to find the best path from 'A' to 'B'.

If you are attempting to perform any of this by modifying the main_matrix_model.py file, ensure that it is within the main() block and under the line that says "#-Main Operating Block-" and above the line that says "#-Graph Drawing-".

  Example: removing node 'C' then adding node 'D' and re-routing from 'A' to 'D'
  > pathMatrix = nop.network_remove_node('C',outGraph,nodeAttr,nodePos,pathMatrix)    
  > pathMatrix = nop.network_add_node('D',[1,2],['B','E'],outGraph,nodeAttr,nodePos,pathMatrix)
  > pathDesired = ('A','D')
---
Changing Pathing Calculations
---
To change the method that the model calculates the best path - whether it be to consider a new node attribute or disregard distance - open the func_network_operations.py file in a text editor or IDE of your choice.

A short explanation: currently, the best path is determined by a 'weight' variable on each edge that connects two nodes. This specific 'weight' value that determines its suitability for being traveled on. The lower the 'weight' value, the less it will be considered in the final route determination. 

For most purposes, you can simply modify how the 'weight' value is calculated in each edge to re-determine what the best possible path should be. To do so, look into the function calc_edge_weights. Make any necessary changes that you wish in the function and set a "result" variable to final results. If you wish to add additional inputs, ensure that this is reflected in nop.calc_edge_weights in the main_matrix_model.py as well. 
To finalize these changes, change the 'weight' attribute for every edge in the graph to the "result" variable you created. This can be done via a for loop, in either of the following manner:
> for node1,node2 in graph.edges(): graph[node1][node2]['weight'] = result;
OR
> for i in graph.(data=True): i[2]['weight'] = result;
Now the the weighting calculations have been changed, the "best route" will likely change based on these new values that model determines.

If you wish the change the actual algorithm itself however (to consider other aspects instead of a 'weight' attribute), look into the get_shortest_path_info function. Modify the line that says best_route = nx.dijkstra_path(graph,startnode,endnode) and instead replace it with your own algorithm. Modify everything under the "else:" line below it accordingly as well. This is generally not a recommended course of action, as the NetworkX library an already ample enough solution for determining the best route. Do note that the pathing matrix takes in a list called "info" containing the total path distance in index 0 and a nested list of all of the edges the route takes in 2D tuples in index 1. Index 1 in particular is immensely important, as that is what is referenced for all outputs - ensure that this property is sustained or that the outputs are adjusted accordingly.
---
Adding Attributes to Paths
---
To add additional attributes to the paths themselves (rather than individual nodes), open the func_network_operations.py file in a text editor or IDE of your choice. Look towards the get_shortest_path_info function - specifically under the 'else:' line underneath the first 'try:' and 'except:' that appears.

Here, the basic path attributes are determined based on the graph, starting node, ending node, and node attributes. Perform any operations as you see fit, then look towards the "info =" line. Simply append the attributes you wish to consider to this list, and now they will be included in the pathing matrix. From here, you can change the routing calculations (see the subsection "Changing Pathing Calculations") with these new attributes added to the paths.