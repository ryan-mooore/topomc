#Oricraft
Oricraft is a python project that will eventually be able to reproduce an orienteering map from a section of a minecraft world. For now all this program does is converts a minecraft chunk into contour data.

###How it Works
Chunk data is decoded and converted to a heightmap using the anvil-parser library for .mca files. A rudimentary Marching Squares algorithm is used for conversion to iso-lines. Points are then converted to tuples and are read by the pyglet graphics program to create the map.

###Installation and running
You'll need all the dependencies listed in requirements.txt. You'll also need to be running a python version at least 3.7 or higher. A virtual environment is reccommended.

Once the script is downloaded, you'll need a file called 'path_to_saves.txt' which should contain a relative or absolute path to the minecraft saves folder.

Currently the script Only works on Linux & Mac.