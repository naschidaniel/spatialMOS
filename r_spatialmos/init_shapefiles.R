rm(list = ls())
setwd(getSrcDirectory()[1])
#setwd('~/dev/spatialMOSv2/r_spatialmos/')
plotpdf = TRUE
stations = read.csv('./data/spatialmos_climatology/stations.csv')

library(raster)
library(rgdal)
library(rasterVis)
library(feather)

# GADM Files from http://www.gadm.org/
# dgm <- getData('alt', country='AUT', mask=FALSE, path='./data/spatialmos_climatology/gadm/', download = TRUE)
# aut_border <- getData('GADM', country='AUT', level=0, download = TRUE, path='./data/spatialmos_climatology/gadm/')
# stirol_border <- getData('GADM', country='ITA', level=2, download = TRUE, path='./data/spatialmos_climatology/gadm/')
dgm <- raster('./data/spatialmos_climatology/gadm/AUT_alt.grd')
aut_border <- readRDS('./data/spatialmos_climatology/gadm/gadm36_AUT_0_sp.rds')
ntirol_border <- readRDS('./data/spatialmos_climatology/gadm/gadm36_AUT_1_sp.rds')
ntirol_border <- ntirol_border[ntirol_border$NAME_1 %in% c('Tirol'), ]
stirol_border <- readRDS('./data/spatialmos_climatology/gadm/gadm36_ITA_2_sp.rds')
stirol_border <- stirol_border[stirol_border$NAME_2 %in% c('Bolzano'), ]

saveRDS(aut_border, file='./data/spatialmos_climatology/gadm/aut_border.rds')
saveRDS(ntirol_border, file='./data/spatialmos_climatology/gadm/ntirol_border.rds')
saveRDS(stirol_border, file='./data/spatialmos_climatology/gadm/stirol_border.rds')

# Create shapefiles
r_size <- raster(nrows = nrow(dgm), ncols = ncol(dgm), xmn=xmin(dgm), xmx=xmax(dgm), ymn=ymin(dgm), ymx=ymax(dgm))
if(!file.exists('./data/spatialmos_climatology/gadm/aut_area.grd')){
  aut_area <- rasterize(aut_border, r_size, progress="last", background=NA)
  writeRaster(aut_area, filename="./data/spatialmos_climatology/gadm/aut_area.grd", overwrite=TRUE)
}else{
  aut_area <- raster('./data/spatialmos_climatology/gadm/aut_area.grd')
}

if(!file.exists('./data/spatialmos_climatology/gadm/ntirol_area.grd')){
  ntirol_area <- rasterize(ntirol_border, r_size, progress="last", background=NA)
  writeRaster(ntirol_area, filename="./data/spatialmos_climatology/gadm/ntirol_area.grd", overwrite=TRUE)
}else{
  ntirol_area <- raster('./data/spatialmos_climatology/gadm/ntirol_area.grd')
}

if(!file.exists('./data/spatialmos_climatology/gadm/stirol_area.grd')){
  stirol_area <- rasterize(stirol_border, r_size, progress="last", background=NA)
  writeRaster(stirol_area, filename="./data/spatialmos_climatology/gadm/stirol_area.grd", overwrite=TRUE)
}else{
  stirol_area <- raster('./data/spatialmos_climatology/gadm/stirol_area.grd')
}

if(!file.exists('./data/spatialmos_climatology/gadm/spatial_area.grd')){
  spatial_area <- merge(ntirol_area, stirol_area)
  writeRaster(spatial_area, filename="./data/spatialmos_climatology/gadm/spatial_area.grd", overwrite=TRUE)
}else{
  spatial_area <- raster('./data/spatialmos_climatology/gadm/spatial_area.grd')
}

if(!file.exists('./data/spatialmos_climatology/gadm/spatial_alt_area.grd')){
  spatial_alt_area <- mask(dgm, spatial_area)
  writeRaster(spatial_alt_area, filename="./data/spatialmos_climatology/gadm/spatial_alt_area.grd", overwrite=TRUE)
}else{
  spatial_alt_area <- raster('./data/spatialmos_climatology/gadm/spatial_alt_area.grd')
}

lonlat <- xyFromCell(spatial_alt_area, c(1:ncell(spatial_alt_area)))
spatial_alt_area_df = data.frame(lon = lonlat[,1],
                                 lat = lonlat[,2],
                                 alt = values(spatial_alt_area))

write_feather(spatial_alt_area_df, './data/spatialmos_climatology/gadm/spatial_alt_area_df.feather')

##### Plot a map with used Stations
if (plotpdf == TRUE) jpeg("./media/plots/messtationen.jpg", height=500, width=800, pointsize = 20, quality=99)
plot(dgm, legend=FALSE, xlab="Longitude", ylab="Latitude", add=FALSE, las=1, col=gray.colors(255))
grid()
plot(spatial_alt_area, legend=TRUE, add=TRUE)
lines(aut_border, col="black")
lines(stirol_border, col="black")
points(stations[,4:5], col='orangered', pch=20, cex=1.)
if (plotpdf == TRUE) dev.off()


