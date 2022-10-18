# TopoMC

TopoMC is a collection of R and python scripts that use the data from your Minecraft worlds to create beautiful topographical maps.

TopoMC is in the process of being completely overhauled though the use of spatial data packages in R. It if not currently in a functioning state. The original marching squares functionality, written in Python, has been moved to a separate directory, [vector-marching-squares](https://github.com/ryan-mooore/vector-marching-squares). Functionality has been preserved - the script will output a `.tif` file that can be imported into the new project to render the original result.

## How it Works

Firstly the raw chunk data needs to be read and processed. This is done by opening the minecraft world save directory and reading the region files (`.mca`) for a world save. The data in these files is processed by the **anvil-parser** python library. This may change in the future.

Once the region data is decoded chunks can be iterated through. The chunk is split up into 64 columns of depth 256. A loop iterates through the column until it locates a ground block (can be changed by passing a custom settings file).

To make this process faster and more efficient, the loop can take advantage of chunk-format heightmaps. To improve minecraft's performance, every chunk file contains precomputed heightmap data which contains info such as the first motion-blocking minecraft block from above. By starting the loop from the height precalculated by these heightmaps instead of y-256 every time a column is searched, efficiency is greatly improved.

## Installation and running

### Installation

1. Clone the repo
2. If you have pipenv, just run `pipenv install && pipenv shell`. If not make sure all [dependencies](Pipfile) are installed.
3. Run the script, which will output a `dem.tif` file in the root directory of the project.
4. To generate a topographic map, the `.tif` file can be imported into a project such as [vector-marching-squares](https://github.com/ryan-mooore/vector-marching-squares)

### Synopsis

python -m topomc **x1 z1 x2 z2** \[--world **worldname**\] \[--debug\] \[--settings **path/to/settings.yml**\]

- (`x1`, `z1`) - Top left chunk
- (`x2`, `z2`) - Bottom right chunk
  - All chunks between these chunks will be included and shown on the map.

### Options

- `-w, --world` World name to map. If not specified the world named "_New World_" will attempt to be mapped
- `--settings` Path to a `.yml` file with with more advanced settings like if you have a non-standard minecraft saves directory.
  Example settings.yml:

```yml
saves_path: "/Applications/MultiMC.app/Data/instances/topomc/.minecraft/saves"
```

### Example

`python -m topomc 0 0 5 5 --world MyWorld --settings MySettings.yml` (Assuming there is a valid world called _MyWorld_ and a settings file in the root directory of the project called _MySettings.yml_)

By default, the script will output a `.dem` file of the elevation of the area.
