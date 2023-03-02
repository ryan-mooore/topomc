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
    smoothr::smooth(method = "ksmooth", smoothness = smoothing)

water <- terra::classify(landcover, rcl = matrix(
    data = c(
        -Inf, 19, NA,
        19, 21, 1,
        21, Inf, NA
    ), ncol = 3, nrow = 3, byrow = TRUE
)) |>
    terra::as.polygons() |>
    smoothr::smooth(method = "ksmooth", smoothness = smoothing)

canopy <- terra::as.polygons(vegetation) |>
    terra::buffer(canopy_buffer) |>
    smoothr::smooth(method = "ksmooth", smoothness = canopy_smoothing)

tmap_mode("view")
tmap_options(check.and.fix = TRUE)
print("RSCRIPT: Drawing features...")
contours_tm <- tm_shape(st_as_sf(contours)) +
    tm_lines(lwd = 1, col = "#D15C00")
vegetation_tm <- tm_shape(vegetation) + tm_raster()
water_tm <- tm_shape(st_as_sf(water)) +
    tm_fill(col = "#00FFFF") +
    tm_borders(col = "black")
canopy_tm <- tm_shape(st_as_sf(canopy)) +
    tm_fill(col = "#FFFFFF")

print("RSCRIPT: Rendering map...")
map <- tm_view(set.zoom.limits = c(18, 25)) +
    tm_basemap(NULL) +
    tm_layout(bg.color = "#FFBA35") +
    canopy_tm +
    water_tm +
    contours_tm

print("RSCRIPT: Saving map...")
tmap_save(map, "map.html")
