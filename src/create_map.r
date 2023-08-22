library(optparse)
settings <- parse_args(OptionParser(
  option_list = list(
    make_option(c("--interactive"),
      action = "store_true", default = FALSE,
      help = "Opens map in interactive viewer"
    ),
    make_option(c("--keep-crumbs"),
      action = "store_true", default = FALSE,
      help = "Keep very small features instead of deleting them"
    ),
    make_option(c("-i", "--interval"),
      default = 1,
      help = "Set contour interval in blocks (default=1)"
    ),
    make_option(c("-s", "--scale"),
      default = 5000,
      help = "Set scale ratio of resulting map (default=5000 (representing 1:5000))"
    ),
    make_option(c("-k", "--smoothing"),
      default = 1,
      help = "set smoothing of map or set to 0 to turn off (default=1)"
    )
  )
), )

library(logger)
log_layout(layout_glue_generator(format = "map: ({level}) {msg}"))
options(warn = -1)
log_info("Attaching packages...")

suppressPackageStartupMessages({
  library(sf)
  library(terra)
  library(tmap)

  library(jsonlite)
  library(tiff)
  library(smoothr)
})

symbol_data <- fromJSON("symbols.json", simplifyDataFrame = FALSE)
exif <- tiff::readTIFF("data/dem.tif", payload = FALSE)

# increase smoothing with more downsampling to account for inaccuracies
resolution <- exif$x.resolution / 300
dpi <- 300
in_per_block <- 39.3701
in_per_mm <- in_per_block / 1000

canopy_buffer <- 2
crop_buffer <- 16

small_tree_buffer <- 11
distinctive_tree_buffer <- 19

# helper functions to convert mm to tmap's internal sizing
lwd_from_mm <- function(mmwidth) {
  lwd_in <- 0.01038889
  inwidth <- in_per_mm * mmwidth
  inwidth / lwd_in
}
size_from_mm <- function(mmwidth) {
  size_in <- 0.0225
  inwidth <- in_per_mm * mmwidth
  inwidth^2 / size_in
}

log_info("Reading data...")
data <- lapply(list(
  dem = terra::rast("data/dem.tif"),
  canopy = terra::rast("data/canopy.tif"),
  landcover = terra::rast("data/landcover.tif"),
  trees = terra::rast("data/trees.tif")
), function(raster) {
  crs(raster) <- "ESRI:53032"
  raster
})

bounds <- st_as_sf(vect(ext(
  ext(data$dem)$xmin + crop_buffer,
  ext(data$dem)$xmax - crop_buffer,
  ext(data$dem)$ymin + crop_buffer,
  ext(data$dem)$ymax - crop_buffer
)))
st_crs(bounds) <- "ESRI:53032"

surface_blocks <- symbol_data |>
  lapply(function(obj) obj$blocks$ground) |>
  unlist() |>
  unique()

log_info("Creating symbols...")
log_info("Creating contours...")
contours <- list(
  feature = data$dem |>
    terra::as.contour(
      maxcell = Inf,
      levels = seq(
        from = min(data$dem[]),
        to = max(data$dem[]),
        by = settings$interval
      )
    ),
  render = list(tm_lines(lwd = lwd_from_mm(0.14), col = "#D15C00")),
  smoothing = 3
)

log_info("Creating water...")
water <- data$landcover
water[!(data$landcover %in% (match(symbol_data$`301`$blocks$ground, surface_blocks) - 1))] <- NA
water <- list(
  feature = water |>
    terra::as.polygons(),
  render = list(
    tm_fill(col = "#00FFFF"),
    tm_borders(lwd = lwd_from_mm(0.18), col = "black")
  ),
  smoothing = 3
)

log_info("Creating ice...")
ice <- data$landcover
ice[!(data$landcover %in% (match(symbol_data$`314`$blocks$ground, surface_blocks) - 1))] <- NA
ice <- list(
  feature = ice |>
    terra::as.polygons(),
  render = list(tm_fill(col = "#BFFFFF")),
  smoothing = 3
)

log_info("Creating bare rock...")
bare_rock <- data$landcover
bare_rock[!(data$landcover %in% (match(symbol_data$`214`$blocks$ground, surface_blocks) - 1))] <- NA
bare_rock <- list(
  feature = bare_rock |>
    terra::as.polygons(),
  render = list(tm_fill(col = "#B3B3B3")),
  smoothing = 3
)

log_info("Creating sand...")
sand <- data$landcover
sand[!(data$landcover %in% (match(symbol_data$`213`$blocks$ground, surface_blocks) - 1))] <- NA
sand <- list(
  feature = sand |>
    terra::as.polygons(),
  render = list(tm_fill(col = "#FFFF80")),
  smoothing = 3
)

log_info("Creating canopy...")
data$canopy[data$canopy == 0] <- NA
canopy <- list(
  feature = terra::as.polygons(data$canopy) |>
    terra::buffer(canopy_buffer * as.logical(settings$smoothing)),
  render = list(tm_fill(col = "#FFFFFF")),
  smoothing = 20
)

# point symbols should only be created if resolution has block accuracy
if (resolution == 1) {
  log_info("Creating trees...")
  trees <- (data$trees |>
    focal(w = small_tree_buffer, fun = "sum") |>
    clamp(lower = 1, upper = 1, values = F) &
    data$trees) |>
    ifel(1, NA)
  distinctive <- (data$trees |>
    focal(w = distinctive_tree_buffer, fun = "sum") |>
    clamp(lower = 1, upper = 1, values = F) &
    data$trees) |>
    ifel(1, NA)
  only_trees <- (trees |> is.na() |> ifel(0, 1)) - (distinctive |> is.na() |> ifel(0, 1)
  )
  only_trees <- only_trees |> ifel(1, NA)

  trees <- list(
    feature = only_trees |> as.points(),
    render = list(
      tm_symbols(
        size = size_from_mm(0.4),
        alpha = 0,
        border.col = "#3DFF17",
        border.lwd = lwd_from_mm(0.2)
      )
    )
  )
  dist_trees <- list(
    feature = distinctive |> as.points(),
    render = list(
      tm_symbols(
        size = size_from_mm(0.72),
        alpha = 0,
        border.col = "#3DFF17",
        border.lwd = lwd_from_mm(0.18)
      )
    )
  )
}
if (resolution == 1) { # include point symbols
  symbols <- list(
    ice = ice,
    sand = sand,
    bare_rock = bare_rock,
    canopy = canopy,
    contours = contours,
    water = water,
    trees = trees,
    dist_trees = dist_trees
  )
} else { # exclude point symbols
  symbols <- list(
    ice = ice,
    sand = sand,
    bare_rock = bare_rock,
    canopy = canopy,
    contours = contours,
    water = water
  )
}

log_info("Applying geometry operations to symbols...")
symbols <- mapply(function(symbol, name) {
  log_info(sprintf("Applying geometry operations to %s...", name))
  feature <- symbol$feature |> st_as_sf()
  geom_types <- feature |>
    st_geometry_type() |>
    as.character() # smooth only if feature is line or polygon
  if ("MULTIPOLYGON" %in% geom_types | "MULTILINESTRING" %in% geom_types) {
    smoothing <- symbol$smoothing * resolution * settings$smoothing
    if (smoothing >= 0.1) {
      feature <- feature |>
        smoothr::smooth(
          method = "ksmooth",
          smoothness = smoothing
        )
    }
    if (!settings$`keep-crumbs`) {
      feature <- feature |> smoothr::drop_crumbs(2) # drop <2x2 (single block)
    }
  }
  list(
    feature = feature,
    render = symbol$render
  )
}, symbols, names(symbols), SIMPLIFY = FALSE)

symbols <- symbols[symbols |> sapply(function(symbol) {
  as.logical(length(symbol$feature$geometry))
})] # filter symbols to only include those with geometry

log_info("Creating map objects...")
render <- symbols |>
  lapply(function(symbol) {
    c(
      list(tm_shape(st_cast(symbol$feature))),
      symbol$render
    )
  }) |>
  unlist(recursive = FALSE) # create list of tmap elements
render <- c(
  list(
    tm_shape(bounds),
    tm_fill(col = "#FFBA35")
  ), # add border to elements
  render
)

img_width <- (exif$width - 2 * crop_buffer) / settings$scale * in_per_block
img_length <- (exif$length - 2 * crop_buffer) / settings$scale * in_per_block
margins <- c(0, 0, 0, 0)

log_info("Rendering map...")
tmap_options(
  check.and.fix = TRUE,
  output.dpi = dpi,
  output.size = img_width * img_length,
  basemaps = NULL
)
(map <- Reduce("+", render) +
  tm_layout(
    frame = FALSE,
    outer.margins = margins,
    inner.margins = margins,
  ) +
  tm_view(
    set.zoom.limits = c(17, 21),
    set.view = 18,
    bbox = bounds
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
