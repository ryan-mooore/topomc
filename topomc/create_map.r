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

tmap::tmap_mode("view")
tmap::tmap_options(check.and.fix = TRUE)

contours_tm <- tmap::tm_shape(sf::st_as_sf(contours)) + tmap::tm_lines(lwd = 1, col = "#D15C00")
dem_tm <- tmap::tm_shape(dem) + tmap::tm_raster()
vegetation_tm <- tmap::tm_shape(vegetation) + tmap::tm_raster()
water_tm <- tmap::tm_shape(sf::st_as_sf(water)) + tmap::tm_fill(col = "#00FFFF") + tmap::tm_borders(col = "black")
canopy_tm <- tmap::tm_shape(sf::st_as_sf(canopy)) + tmap::tm_fill(col = "#FFFFFF")

map <- tmap::tm_view(set.zoom.limits = c(18, 25)) + tmap::tm_basemap(NULL) + tmap::tm_layout(bg.color = "#FFBA35") +
    canopy_tm +
    water_tm +
    contours_tm

tmap::tmap_save(map, "map.html")
