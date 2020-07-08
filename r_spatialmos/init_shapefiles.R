rm(list = ls())

library(tools)
library(raster)
library(rgdal)
library(rasterVis)
library(feather)

#setwd(file_path_as_absolute())
#setwd('~/dev/spatialMOSv2/r_spatialmos/')
setwd('/usr/src/app/')
plotpdf = TRUE
stations = read.csv('./data/spatialmos_climatology/stations.csv')

# GADM Files from http://www.gadm.org/

dir.create('./data/get_available_data/gadm/', showWarnings = FALSE)
dgm <- getData('alt', country='AUT', mask=FALSE, path='./data/get_available_data/gadm/', download = TRUE)
aut_border <- getData('GADM', country='AUT', level=0, download = TRUE, path='./data/get_available_data/gadm/')
ntirol_border <- getData('GADM', country='AUT', level=1, download = TRUE, path='./data/get_available_data/gadm/')
stirol_border <- getData('GADM', country='ITA', level=2, download = TRUE, path='./data/get_available_data/gadm/')
dgm <- raster('./data/get_available_data/gadm/AUT_alt.grd')
aut_border <- readRDS('./data/get_available_data/gadm/gadm36_AUT_0_sp.rds')
ntirol_border <- readRDS('./data/get_available_data/gadm/gadm36_AUT_1_sp.rds')
ntirol_border <- ntirol_border[ntirol_border$NAME_1 %in% c('Tirol'), ]
stirol_border <- readRDS('./data/get_available_data/gadm/gadm36_ITA_2_sp.rds')
stirol_border <- stirol_border[stirol_border$NAME_2 %in% c('Bolzano'), ]

saveRDS(aut_border, file='./data/get_available_data/gadm/aut_border.rds')
saveRDS(ntirol_border, file='./data/get_available_data/gadm/ntirol_border.rds')
saveRDS(stirol_border, file='./data/get_available_data/gadm/stirol_border.rds')

# Create shapefiles
r_size <- raster(nrows = nrow(dgm), ncols = ncol(dgm), xmn=xmin(dgm), xmx=xmax(dgm), ymn=ymin(dgm), ymx=ymax(dgm))
if(!file.exists('./data/get_available_data/gadm/aut_area.grd')){
  aut_area <- rasterize(aut_border, r_size, progress="last", background=NA)
  writeRaster(aut_area, filename="./data/get_available_data/gadm/aut_area.grd", overwrite=TRUE)
}else{
  aut_area <- raster('./data/get_available_data/gadm/aut_area.grd')
}

if(!file.exists('./data/get_available_data/gadm/ntirol_area.grd')){
  ntirol_area <- rasterize(ntirol_border, r_size, progress="last", background=NA)
  writeRaster(ntirol_area, filename="./data/get_available_data/gadm/ntirol_area.grd", overwrite=TRUE)
}else{
  ntirol_area <- raster('./data/get_available_data/gadm/ntirol_area.grd')
}

if(!file.exists('./data/get_available_data/gadm/stirol_area.grd')){
  stirol_area <- rasterize(stirol_border, r_size, progress="last", background=NA)
  writeRaster(stirol_area, filename="./data/get_available_data/gadm/stirol_area.grd", overwrite=TRUE)
}else{
  stirol_area <- raster('./data/get_available_data/gadm/stirol_area.grd')
}

if(!file.exists('./data/get_available_data/gadm/spatial_area.grd')){
  spatial_area <- merge(ntirol_area, stirol_area)
  writeRaster(spatial_area, filename="./data/get_available_data/gadm/spatial_area.grd", overwrite=TRUE)
}else{
  spatial_area <- raster('./data/get_available_data/gadm/spatial_area.grd')
}

spatial_alt_area <- mask(dgm, spatial_area)
extend_area <- as(extent(10, 13, 46, 48), 'SpatialPolygons')
spatial_alt_area <- crop(spatial_alt_area, extend_area)
writeRaster(spatial_alt_area, filename="./data/get_available_data/gadm/spatial_alt_area.grd", overwrite=TRUE)


lonlat <- xyFromCell(spatial_alt_area, c(1:ncell(spatial_alt_area)))
spatial_alt_area_df = data.frame(lon = lonlat[,1],
                                 lat = lonlat[,2],
                                 alt = values(spatial_alt_area))

write_feather(spatial_alt_area_df, './data/get_available_data/gadm/spatial_alt_area_df.feather')
write.csv2(spatial_alt_area_df, './data/get_available_data/gadm/spatial_alt_area_df.csv')

##### Plot a map with used Stations
if (plotpdf == TRUE) jpeg("./data/static/measuring_stations.jpg", height=500, width=800, pointsize = 20, quality=99)
plot(spatial_alt_area, legend=TRUE, xlab="Longitude", ylab="Latitude", add=FALSE, las=1)#, col=gray.colors(255))
grid()
#plot(spatial_alt_area, legend=TRUE, add=TRUE)
#lines(aut_border, col="black")
lines(stirol_border, col="black")
lines(stirol_border, col="black")
points(stations[,4:5], col='orangered', pch=20, cex=1.)
if (plotpdf == TRUE) dev.off()


