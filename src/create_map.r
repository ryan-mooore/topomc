suppressPackageStartupMessages({
    library(logger)
    log_layout(layout_glue_generator(format = 'map: ({level}) {msg}'))
    log_info("Attaching packages...")
    library(optparse)

    library(sf)
    library(terra)
    library(tmap)

    library(tiff)
    library(smoothr)
})
options(warn = -1)

contour_interval <- 1
canopy_buffer <- 2
crop_buffer <- 16
surface_blocks <- read.table("surface_blocks.txt")$V1

# increase smoothing with more downsampling to account for inaccuracies
resolution <- tiff::readTIFF("data/dem.tif", payload=F)$x.resolution / 300
smoothing <- 3 * resolution 
canopy_smoothing <- 20 * resolution

settings <- parse_args(OptionParser(
    option_list=list(make_option(c("--interactive"), action="store_true", default=F))),
)

log_info("Reading data...")
data <- lapply(list(
    dem=terra::rast("data/dem.tif"),
    vegetation=terra::rast("data/vegetation.tif"),
    landcover=terra::rast("data/landcover.tif")
), function(raster) {crs(raster) <- "ESRI:53032"; raster})

bounds <- st_as_sf(vect(ext(
    ext(data$dem)$xmin + crop_buffer,
    ext(data$dem)$xmax - crop_buffer,
    ext(data$dem)$ymin + crop_buffer,
    ext(data$dem)$ymax - crop_buffer
)))
st_crs(bounds) <- "ESRI:53032"

log_info("Creating symbols...")
log_info("Creating contours...")
contours <- list(
    feature=data$dem |>
    terra::as.contour(levels = seq(
        from = min(data$dem[]),
        to = max(data$dem[]),
        by = contour_interval
    )) |>
    st_as_sf() |>
    smoothr::smooth(method = "ksmooth", smoothness = smoothing),
    render=list(tm_lines(lwd = 1, col = "#D15C00"))
)

log_info("Creating water...")
water <- data$landcover
water[data$landcover != (match("water", surface_blocks) - 1)] <- NA
water <- list(
    feature=water |>
    terra::as.polygons() |>
    st_as_sf() |>
    smoothr::smooth(method = "ksmooth", smoothness = smoothing) |>
    st_buffer(dist = 0), # fix self-intersection
    render=list(tm_fill(col = "#00FFFF"), tm_borders(col = "black"))
)

log_info("Creating canopy...")
data$vegetation[data$vegetation == 0] <- NA
canopy <- list(
    feature=terra::as.polygons(data$vegetation) |>
    terra::buffer(canopy_buffer) |>
    st_as_sf() |>
    smoothr::smooth(method = "ksmooth", smoothness = canopy_smoothing) |>
    st_buffer(dist = 0), # fix self-intersection
    render=list(tm_fill(col = "#FFFFFF"))
)

symbols <- list(
    canopy=canopy,
    water=water,
    contours=contours
) # symbols in overprinting order for rendering

log_info("Cropping symbols...")
symbols <- symbols |> lapply(function(symbol) list(
  feature=symbol$feature |> st_crop(bounds),
  render=symbol$render
  ) # crop all symbols to extent
) 

symbols <- symbols[symbols |> sapply(function(symbol) {
  as.logical(length(symbol$feature$geometry))
})] # filter symbols to only include those with geometry

log_info("Creating map objects...")
render <- symbols |> 
    lapply(function(symbol) {c(
    list(tm_shape(symbol$feature)),
    symbol$render)
    }) |>
    unlist(recursive=F) # create list of tmap elements
render <- c(
  list(
    tm_shape(bounds),
    tm_fill(col="#FFBA35"),
    tm_borders(col="black")
  ), # add border to elements
  render
)

log_info("Rendering map...")
tmap_options(check.and.fix = TRUE, output.dpi = 600, basemaps=NULL)
(map <- Reduce("+", render) +
  tm_layout(scale=0.25, frame=F) +
  tm_view(
    set.zoom.limits = c(17, 21),
    set.view = 18
  )
)

log_info("Saving map...")
suppressMessages({
    if (settings$interactive) {
        tmap_mode("view")
        tmap_save(map, "map.html")
    } else {
        tmap_mode("plot")
        tmap_save(map, "map.png")
    }
})