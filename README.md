# TopoMC

![](images/example.png)

TopoMC is a collection of R and python scripts that use the data from your Minecraft worlds to create beautiful topographical maps. TopoMC currently only supports versions 1.17 and below, but adding support for the latest version is a priority and should be added soon™.

## How it Works

Firstly the raw chunk data needs to be read and processed. This is done by opening the minecraft world save directory and reading the region files (`.mca`) for a world save. The data in these files is processed by the **anvil-parser** python library. This may change in the future.

Once the region data is decoded chunks can be iterated through in order to find ground blocks (can be changed by passing a custom settings file). To make this process more efficient, the loop can take advantage of precomputed heightmaps. These heightmaps contain info such as the y-level of the first motion-blocking minecraft block. By starting the loop from the height precalculated by these heightmaps, efficiency is greatly improved.

After the chunks are read several `.tif` files are saved in a folder called `data` at the root directory of the project. These files contain the raw data extracted from the minecraft files that is needed to create the topographical map. `.tif` files are chosen as they are cross-compatible and effective data matrix format.

The final part of the script runs the R spatial processes which format the data into a presentable and interactive map, which opens in the default web browser after the data processing is complete.

## Installation and running

### Installation

1. Make sure you have Python >= 3.9 and R installed on your computer
2. Clone the repo
3. If you have pipenv, just run `pipenv install && pipenv shell`. If not make sure all [dependencies](Pipfile) are installed
4. The project uses `renv` for R dependency management. This should install the required R packages when the script is run - `terra`, `smoothr`, `sf`, and `tmap`. However if this does not work make sure to install these packages manually with `install.packages()`
5. Run the scripts (as a module, using the `-m` flag), which will output the raw `.tif` files in the generated `data` folder
6. The interactive map of the minecraft world will open in your web browser

> Note: Currently the script only supports version 1.17 and below. Additionally, the script can only work if all the bounded chunks have been loaded in game previously. This means you may have to open the world in game and walk around in order to load the chunks you want to map.

### Synopsis

python -m topomc **x1 z1 x2 z2** \[--world **worldname**\] \[--debug\] \[--settings **path/to/settings.yml**\]

- (`x1`, `z1`) - Top left chunk
- (`x2`, `z2`) - Bottom right chunk

### Options

- `-w, --world` World to use. If not specified the world named "_New World_" will attempt to be mapped
- `--settings` Path to a `.yml` file with with more advanced settings like if you are using a third party launcher and have a non-standard minecraft saves directory.

Example settings.yml:

```yml
Saves path: "/Applications/MultiMC.app/Data/instances/topomc/.minecraft/saves"

Surface blocks:
  - "grass_block"
  - "grass_path"
  - "dirt"
  - "coarse_dirt"
```

### Example

`python -m topomc -255 -255 255 255 --world MyWorld --settings MySettings.yml` (Assuming there is a valid world called _MyWorld_ and a settings file in the root directory of the project called _MySettings.yml_)

## Contributing

Feel free to create a PR at any point, or add an issue if you have any problems or suggestions.
