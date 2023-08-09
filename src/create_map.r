library(optparse)
settings <- parse_args(OptionParser(
    option_list=list(
        make_option(c("--interactive"), action="store_true", default=F, 
        help="Opens map in interactive viewer"),
        make_option(c("--keep-crumbs"), action="store_true", default=F,
        help="Keep very small features instead of deleting them"),
        make_option(c("-i", "--interval"), default=1,
        help="Set contour interval in blocks (default=1)"),
        make_option(c("-s", "--scale"), default=5000,
        help="Set scale ratio of resulting map (default=5000 (representing 1:5000))"),
        make_option(c("-k", "--smoothing"), default=1,
        help="Set smoothing of map or set to 0 to turn off (default=1)")
    )),
)

library(logger)
log_layout(layout_glue_generator(format = 'map: ({level}) {msg}'))
options(warn = -1)
log_info("Attaching packages...")

suppressPackageStartupMessages({
    library(sf)
    library(terra)
    library(tmap)

    library(tiff)
    library(smoothr)
})

surface_blocks <- read.table("surface_blocks.txt")$V1
exif <- tiff::readTIFF("data/dem.tif", payload=F)

# increase smoothing with more downsampling to account for inaccuracies
resolution <- exif$x.resolution / 300
dpi <- 300
in_per_block <- 39.3701
canopy_buffer <- 2
crop_buffer <- 16

dotwidth <- function (mmwidth) {
    in_per_mm <- in_per_block / 1000
    dots_per_mm <- in_per_mm * dpi
    mmwidth * dots_per_mm
}

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
        by = settings$interval
    )),
    render=list(tm_lines(lwd = dotwidth(0.14), col = "#D15C00")),
    smoothing=3
)

log_info("Creating water...")
water <- data$landcover
water[data$landcover != (match("water", surface_blocks) - 1)] <- NA
water <- list(
    feature=water |>
    terra::as.polygons(),
    render=list(tm_fill(col = "#00FFFF"), tm_borders(lwd = dotwidth(0.18), col = "black")),
    smoothing=3
)

log_info("Creating canopy...")
data$vegetation[data$vegetation == 0] <- NA
canopy <- list(
    feature=terra::as.polygons(data$vegetation) |>
    terra::buffer(canopy_buffer * as.logical(settings$smoothing)),
    render=list(tm_fill(col = "#FFFFFF")),
    smoothing=20
)

symbols <- list(
    canopy=canopy,
    contours=contours,
    water=water
) # symbols in overprinting order for rendering

log_info("Applying geometry operations to symbols...")
symbols <- mapply(function(symbol, name) {
    log_info(sprintf("Applying geometry operations to %s...", name))
    feature <- symbol$feature |> st_as_sf()
    smoothing <- symbol$smoothing * resolution * settings$smoothing
    if (smoothing >= 0.1) {
        feature <- feature |> smoothr::smooth(method="ksmooth", smoothness = smoothing)
    }
    if (!settings$`keep-crumbs`) {
        feature <- feature |> smoothr::drop_crumbs(12)
    }
    feature <- tryCatch({
        feature |> st_crop(bounds)
    }, error=function (error) {
        feature |> st_buffer(dist=0) |> st_crop(bounds)
    })
    list(
        feature=feature,
        render=symbol$render
    ) # crop all symbols to extent}
}, symbols, names(symbols), SIMPLIFY=F)

symbols <- symbols[symbols |> sapply(function(symbol) {
  as.logical(length(symbol$feature$geometry))
})] # filter symbols to only include those with geometry

log_info("Creating map objects...")
render <- symbols |> 
    lapply(function(symbol) {c(
    list(tm_shape(st_cast(symbol$feature))),
    symbol$render)
    }) |>
    unlist(recursive=F) # create list of tmap elements
render <- c(
  list(
    tm_shape(bounds),
    tm_fill(col="#FFBA35")
  ), # add border to elements
  render
)

img_width <- (exif$width - 2 * crop_buffer) / settings$scale * in_per_block
img_length <- (exif$length - 2 * crop_buffer) / settings$scale * in_per_block
margins <- c(0, 0, 0, 0)

log_info("Rendering map...")
tmap_options(
    check.and.fix = TRUE,
    output.dpi=dpi, 
    output.size = img_width * img_length,
    basemaps=NULL
)
(map <- Reduce("+", render) +
  tm_layout(scale=0.25, frame=F, outer.margins=margins, inner.margins=margins) +
  tm_view(
    set.zoom.limits = c(17, 21),
    set.view = 18
  )
)

log_info("Saving map...")
# suppressMessages({
    if (settings$interactive) {
        tmap_mode("view")
        tmap_save(map, "map.html")
    } else {
        tmap_mode("plot")
        tmap_save(map, "map.png")
    }
# })