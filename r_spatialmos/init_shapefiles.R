rm(list = ls())
setwd('~/Dropbox/MOS/spatialMOS/')
plotpdf = TRUE
stations = read.csv('./data/GAM/stations.csv')

library(raster)
library(rgdal)
library(rasterVis)
library(feather)

# GADM Files from http://www.gadm.org/
# dgm <- getData('alt', country='AUT', mask=FALSE, path='./DGM/', download = TRUE)
# aut_border <- getData('GADM', country='AUT', level=0, download = TRUE, path='./DGM/')
# stirol_border <- getData('GADM', country='ITA', level=2, download = TRUE, path='./DGM/')
dgm <- raster('./data/DGM/AUT_alt.grd')
aut_border <- readRDS('./data/DGM/gadm36_AUT_0_sp.rds')
ntirol_border <- readRDS('./data/DGM/gadm36_AUT_1_sp.rds')
ntirol_border <- ntirol_border[ntirol_border$NAME_1 %in% c('Tirol'), ]
stirol_border <- readRDS('./data/DGM/gadm36_ITA_2_sp.rds')
stirol_border <- stirol_border[stirol_border$NAME_2 %in% c('Bolzano'), ]

saveRDS(aut_border, file='./data/DGM/aut_border.rds')
saveRDS(ntirol_border, file='./data/DGM/ntirol_border.rds')
saveRDS(stirol_border, file='./data/DGM/stirol_border.rds')

# Shapefiles
r_size <- raster(nrows = nrow(dgm), ncols = ncol(dgm), xmn=xmin(dgm), xmx=xmax(dgm), ymn=ymin(dgm), ymx=ymax(dgm))
if(!file.exists('./data/DGM/AUT_area.grd')){
  aut_area <- rasterize(aut_border, r_size, progress="last", background=NA)
  writeRaster(aut_area, filename="./data/DGM/AUT_area.grd", overwrite=TRUE)
}else{
  aut_area <- raster('./data/DGM/AUT_area.grd')
}

if(!file.exists('./data/DGM/TIAU_area.grd')){
  tiau_area <- rasterize(ntirol_border, r_size, progress="last", background=NA)
  writeRaster(tiau_area, filename="./data/DGM/TIAU_area.grd", overwrite=TRUE)
}else{
  tiau_area <- raster('./data/DGM/TIAU_area.grd')
}

if(!file.exists('./data/DGM/BZIT_area.grd')){
  bzit_area <- rasterize(stirol_border, r_size, progress="last", background=NA)
  writeRaster(bzit_area, filename="./data/DGM/BZIT_area.grd", overwrite=TRUE)
}else{
  bzit_area <- raster('./data/DGM/BZIT_area.grd')
}

if(!file.exists('./data/DGM/SPATIAL_AREA_area.grd')){
  spatial_area <- merge(tiau_area, bzit_area)
  writeRaster(spatial_area, filename="./data/DGM/SPATIAL_AREA_area.grd", overwrite=TRUE)
}else{
  spatial_area <- raster('./data/DGM/SPATIAL_AREA_area.grd')
}

if(!file.exists('./data/DGM/SPATIAL_ALT_area.grd')){
  spatial_alt_area <- mask(dgm, spatial_area)
  writeRaster(spatial_alt_area, filename="./data/DGM/SPATIAL_ALT_area.grd", overwrite=TRUE)
}else{
  spatial_alt_area <- raster('./data/DGM/SPATIAL_ALT_area.grd')
}

lonlat <- xyFromCell(spatial_alt_area, c(1:ncell(spatial_alt_area)))
spatial_alt_area_df = data.frame(lon = lonlat[,1],
                                 lat = lonlat[,2],
                                 alt = values(spatial_alt_area))

write_feather(spatial_alt_area_df, './data/DGM/SPATIAL_ALT_area_df.feather')

##### Plot MAP with Informations about used Stations
if (plotpdf == TRUE) jpeg("./media/plots/messtationen.jpg", height=500, width=800, pointsize = 20, quality=99)
plot(dgm, legend=FALSE, xlab="Längengrad", ylab="Breitengrad", add=FALSE, las=1, col=gray.colors(255))
grid()
plot(spatial_alt_area, legend=TRUE, add=TRUE)
lines(aut_border, col="black")
lines(stirol_border, col="black")
points(stations[,4:5], col='orangered', pch=20, cex=1.)
if (plotpdf == TRUE) dev.off()


