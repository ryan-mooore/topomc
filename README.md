# TopoMC

![Standard](images/example1.png) ![Amplified](images/example2.png)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/805c61e9222146e2830f0920560d6e4d)](https://www.codacy.com/manual/ryan-mooore/topomc?utm_source=github.com&utm_medium=referral&utm_content=ryan-mooore/topomc&utm_campaign=Badge_Grade)

# TODO:

- [ ] Improve tagline algorithm
- [ ] Improve chunk parsing efficiency
- [ ] Better validation
- [ ] Auto sampling level
- [ ] Symbol type inheritance
- [ ] Refactor TopoGraph class
- [ ] Rewrite README
- [ ] Symbol scaling follows IOF spec

# TO FIX:

- [ ] Steep feature edge case
- [ ] Contour interval

# Ideas

- [ ] Quick render

## How it Works

Creating the topo map from the chunks, inside the chosen bounding co-ordinates, is a 4 step process:

### 1. Reading Chunks

Firstly the raw chunk data needs to be read and processed. This is done by opening the minecraft world save directory and reading the region files (`.mca`) for a world save. The data in these files is processed by the **anvil-parser** python library. This may change in the future.

### 2. Creating a Heightmap

Once the region data is decoded chunks can be iterated through. The chunk is split up into 64 columns of depth 256. A loop iterates through the column until it locates a ground block (can be changed by passing a custom settings file).

To make this process faster and more efficient, the loop can take advantage of chunk-format heightmaps. To improve minecraft's performance, every chunk file contains precomputed heightmap data which contains info such as the first motion-blocking minecraft block from above. By starting the loop from the height precalculated by these heightmaps instead of y-256 every time a column is searched, efficiency is greatly improved.

### 3. Marching Squares Algorithm

After a heightmap has been created, it needs to be converted into coordinate data which is later used to draw lines that split up the height differences of the heightmap - or contours. To do this the heightmap is transformed into cells, with a height point in each corner. The difference between the corners is then used to decide where to place the points for the line to be drawn. This is called the [marching squares algorithm](https://en.wikipedia.org/wiki/Marching_squares).

### 4. Generalization

In order to smooth the isolines, the 1d guassian filter function from `scipy.ndimage` is used.

## Installation and running

### Installation

1. Clone the repo
2. If you have pipenv, just run `pipenv install`. If not make sure all [dependencies](Pipfile) are installed.

### Synopsis

python -m topomc **x1 z1 x2 z2** \[--world **worldname**\] \[--debug\] \[--settings **path/to/settings.yml**\]

- (`x1`, `z1`) - Top left chunk limit
- (`x2`, `z2`) - Bottom right chunk limit
  - All chunks within these arguments will be bounded and shown on the map.
  - Both co-ordinates are inclusive.

### Options

- `-w, --world` World name to map. If not specified the world named "_New World_" will attempt to be mapped
- `-D, --debug ` Will open a preview in debug mode for the top left chunk specified with (**x1 z1**).
- `--settings` Path to a `.yml` file with with more advanced settings like print scale, contour interval, changing the minecraft saves directory and `.pdf` save location. A file with all available settings and default values can be found as an example at [examples/settings/settings.yml](examples/settings/settings.yml)

### Example

`python -m topomc 0 0 5 5 --world MyWorld --settings MySettings.yml` (Assuming there is a valid world called _MyWorld_ and a settings file in the root directory of the project called _MySettings.yml_)

By default, the script will output a `.pdf` file of the map at the scale `1:1000`. As well as this, a preview window will appear. Save location and map scale can be changed by passing a custom settings `.yml` file to `--settings`.
