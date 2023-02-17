# TopoMC

TopoMC is a collection of R and python scripts that use the data from your Minecraft worlds to create beautiful topographical maps.

TopoMC is in the process of being completely rewritten though the use of spatial data packages in R. The original marching squares functionality, written in Python, has been moved to a separate directory, [vector-marching-squares](https://github.com/ryan-mooore/vector-marching-squares). Functionality has been preserved - the script will output a `.tif` file that can be imported into the new project to render a topographical map.

## How it Works

Firstly the raw chunk data needs to be read and processed. This is done by opening the minecraft world save directory and reading the region files (`.mca`) for a world save. The data in these files is processed by the **anvil-parser** python library. This may change in the future.

Once the region data is decoded chunks can be iterated through in order to find ground blocks (can be changed by passing a custom settings file). To make this process more efficient, the loop can take advantage of precomputed heightmaps. These heightmaps contain info such as the y-level of the first motion-blocking minecraft block. By starting the loop from the height precalculated by these heightmaps, efficiency is greatly improved.

## Installation and running

### Installation

1. Clone the repo
2. If you have pipenv, just run `pipenv install && pipenv shell`. If not make sure all [dependencies](Pipfile) are installed.
3. Run the scripts (as a module, using the `-m` flag), which will output a `dem.tif` file in the root directory of the project.
4. To generate a topographic map, the `.tif` file can be imported into a project such as [vector-marching-squares](https://github.com/ryan-mooore/vector-marching-squares)

### Synopsis

python topomc -m **x1 z1 x2 z2** \[--world **worldname**\] \[--debug\] \[--settings **path/to/settings.yml**\]

- (`x1`, `z1`) - Top left chunk
- (`x2`, `z2`) - Bottom right chunk

### Options

- `-w, --world` World to use. If not specified the world named "_New World_" will attempt to be mapped
- `--settings` Path to a `.yml` file with with more advanced settings like if you are using a third party launcher and have a non-standard minecraft saves directory.

Example settings.yml:

```yml
saves path: "/Applications/MultiMC.app/Data/instances/topomc/.minecraft/saves"

surface blocks:
  - "grass_block"
  - "grass_path"
  - "dirt"
  - "coarse_dirt"
```

### Example

`python -m topomc 0 0 5 5 --world MyWorld --settings MySettings.yml` (Assuming there is a valid world called _MyWorld_ and a settings file in the root directory of the project called _MySettings.yml_)
