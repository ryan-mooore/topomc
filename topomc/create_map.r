library(tmap)
library(sf)
library(smoothr)
library(terra)

requireNamespace("smoothr")
requireNamespace("terra")

dem <- terra::rast("data/dem.tif")
vegetation <- terra::rast("data/vegetation.tif")
vegetation[vegetation == 0] <- NA
landcover <- terra::rast("data/landcover.tif")

contour_interval <- 1
smoothing <- 10

canopy_smoothing <- 30
canopy_buffer <- 2

contours <- dem |>
    terra::as.contour(levels = seq(
        from = min(dem[]),
        to = max(dem[]),
        by = contour_interval
    )) |>
    st_as_sf() |>
    smoothr::smooth(method = "ksmooth", smoothness = smoothing)

water <- terra::classify(landcover, rcl = matrix(
    data = c(
        -Inf, 19, NA,
        19, 21, 1,
        21, Inf, NA
    ), ncol = 3, nrow = 3, byrow = TRUE
    )) |>
    terra::as.polygons() |>
    st_as_sf() |>
    smoothr::smooth(method = "ksmooth", smoothness = smoothing)

canopy <- terra::as.polygons(vegetation) |>
    terra::buffer(canopy_buffer) |>
    st_as_sf() |>
    smoothr::smooth(method = "ksmooth", smoothness = canopy_smoothing)

tmap_mode("view")
tmap_options(check.and.fix = TRUE)
print("RSCRIPT: Drawing features...")
layers <- list()

if (length(canopy$geometry)) layers <- c(layers, list(tm_shape((canopy)), tm_fill(col = "#FFFFFF")))
if (length(contours$geometry)) layers <- c(layers, list(tm_shape((contours)), tm_lines(lwd = 1, col = "#D15C00")))
if (length(water$geometry)) layers <- c(layers, list(tm_shape(water), tm_fill(col = "#00FFFF"), tm_borders(col = "black")))
# layers <- c(layers, list(tm_shape(vegetation) + tm_raster()))

print("RSCRIPT: Rendering map...")
map <- tm_view(
    # set.zoom.limits = c(0, 10)
    ) +
    tm_basemap(NULL) +
    tm_layout(bg.color = "#FFBA35") + 
    Reduce("+", layers)

print("RSCRIPT: Saving map...")
tmap_save(map, "map.html")
