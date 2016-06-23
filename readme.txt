Usage
-----
Requirements
---
The usage of this model requires that Python 3.4 with Anaconda 3 is installed onto the system. If you do not have these installed already, please view https://www.continuum.io/downloads for more information.
---
Environment Setup
---
To set up the exact Python environment required for the model, open a command prompt/command line. Point to where the 'env' folder is located (the folder should contain a file called "environment.yml"). In the terminal, type (without the beginning >):
> conda env create -f environment.yml
If there are no errors, the environment will be created successfully and you can move onto the "Model Setup" section. 
    If an issue does occur, an alternative method of creating the environment can be used:
    > conda create --name test_networkx --file explicit-spec-file.txt
    This method explicitly links each package/dependency for Anaconda to install the environment.
---
Model Setup
---
To setup a model for analysis, open main_matrix_model.py with a text editor or IDE of your choice. Under the line that says "#--Configuration--" will be several variables. 
 
nodeAttr is a dictionary of all the locations (or "nodes") that the model will consider. It also contains any special attributes about those locations (such as position). It should be written in the format: " 'Node': (x coordinate, y coordinate, attribute1, attribute2, ...) " with each entry seperated by commas. A node MUST have an associated x and y coordinate in the first two entries - otherwise the model will fail to be able to perform calculations!
Example: nodeAttr = {'A': (0,0), 'B': (2,0), 'C': (2,1)}

nodeNeighbors is a list that contains all the connections that each location has to one another. Location connections must be done in the form of a 2D tuple. In other words, you must have a connection in the form of (Location A, Location B); you cannot make a connection in the form of (Location A, Location B, Location C). Connections are two-way, so you do not need to make a seperate connection for an opposite route (i.e. (A,B) implies (B,A) is also a connection)
Example: nodeNeighbors = [('A','B'),('B','C')]

pathDesired is a tuple between a starting location and ending location that is used to determine the best route to take between these two locations. This can change over time depending on your needs. Note that like nodeNeighbors, this must be between exactly two locations in the form of (Location A, Location B).
Example: pathDesired = ('A','C')

Once you have configured the model to your liking, save the file and close the editor. 
---
Running the Model
---
After the model is properly configured, open a command prompt/command line and point to the location where main_matrix_model.py is located. Type (without the beginning >):
> activate test_networkx
> python main_matrix_model.py
This will activate the Python environment necessary for the model (loading all necessary packages/dependencies) and run the main python file responsible for running the program. If the model was properly configured, the program will print the best route from the starting location to the desired destination as well as visually display it.
---
