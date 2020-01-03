# Oricraft

Oricraft is a python project that will eventually be able to reproduce an orienteering map from a section of a minecraft world. For now all this program does is converts a minecraft chunk into contour data.

## How it Works

Firstly, chunk data is decoded and read from minecraft's save-files using the anvil-parser library for .mca files. A program then iterates through the chunk data to create a heightmap. A rudimentary Marching Squares algorithm is then used for conversion to basic iso-lines. These iso-lines are transformed into co-ordinates in order for the pyglet canvas library to draw them in a window.

## Installation and running

### Installation

Firstly, make sure all the dependencies listed in requirements.txt are installed. You'll also need to be running a python version at least 3.7 or higher.

Once the script is downloaded, you'll need to create a file in the project's root directory, called 'path_to_saves.txt' which should contain a relative or absolute path to the minecraft saves folder.

### Running

Currently the script only works on Linux & Mac.

to run it, use the following format: main.py worldname chunkx1 chunky1 chunkx2 chunky2