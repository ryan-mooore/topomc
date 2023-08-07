library(optparse)
library(tmap)
library(sf)
library(smoothr)
library(terra)

contour_interval <- 1
smoothing <- 8

canopy_smoothing <- 25
canopy_buffer <- 2
crop_buffer <- 16

settings <- parse_args(OptionParser(
    option_list=list(make_option(c("--interactive"), action="store_true", default=F))),
)

layers <- lapply(list(
    dem=terra::rast("data/dem.tif"),
    vegetation=terra::rast("data/vegetation.tif"),
    landcover=terra::rast("data/landcover.tif")
), function(layer) {crs(layer) <- "ESRI:53032"; layer})

bounds <- st_as_sf(vect(ext(
    ext(layers$dem)$xmin + crop_buffer,
    ext(layers$dem)$xmax - crop_buffer,
    ext(layers$dem)$ymin + crop_buffer,
    ext(layers$dem)$ymax - crop_buffer
)))
st_crs(bounds) <- "ESRI:53032"

layers$vegetation[layers$vegetation == 0] <- NA

contours <- list(
    feature=layers$dem |>
    terra::as.contour(levels = seq(
        from = min(layers$dem[]),
        to = max(layers$dem[]),
        by = contour_interval
    )) |>
    st_as_sf() |>
    smoothr::smooth(method = "ksmooth", smoothness = smoothing),
    render=list(tm_lines(lwd = 1, col = "#D15C00"))
)


water <- list(
    feature=terra::classify(layers$landcover, rcl = matrix(
    data = c(
        -Inf, 19, NA,
        19, 21, 1,
        21, Inf, NA
    ), ncol = 3, nrow = 3, byrow = TRUE
    )) |>
    terra::as.polygons() |>
    st_as_sf() |>
    smoothr::smooth(method = "ksmooth", smoothness = smoothing) |>
    st_buffer(dist = 0), # fix self-intersection
    render=list(tm_fill(col = "#00FFFF"), tm_borders(col = "black"))
)

canopy <- list(
    feature=terra::as.polygons(layers$vegetation) |>
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

symbols <- symbols |> lapply(function(symbol) list(
        feature=symbol$feature |> st_crop(bounds),
        render=symbol$render
    ) # crop all symbols to extent
) 
symbols <- symbols[symbols |> sapply(function(symbol) {
    as.logical(length(symbol$feature$geometry))
})] # filter symbols to only include those with geometry

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

tmap_options(check.and.fix = TRUE, output.dpi = 600, basemaps=NULL)
print("map: Rendering map...")
(map <- Reduce("+", render) +
  tm_layout(scale=0.25, frame=F) +
  tm_view(
    set.zoom.limits = c(17, 21),
    set.view = 18
  )
)

print("map: Saving map...")

if (settings$interactive) {
    tmap_mode("view")
    tmap_save(map, "map.html")
} else {
    tmap_mode("plot")
    tmap_save(map, "map.png")
}