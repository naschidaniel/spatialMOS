#Funktionen für Spatial Prediction
formula_generator = function(yday_df, lon_lat_df, hour_df)
{
  formel <- paste0("ti(lon, lat, k=", c(lon_lat_df), ", d=c(2), bs=c('tp')) + 
                    alt +
                    ti(yday, k=", c(yday_df), ", d=c(1), bs=c('cc')) + 
                    ti(yday, k=", c(yday_df), ", d=c(1), bs=c('cc'), by=alt) + ")
                    #ti(hour, k=", c(hour_df), ", d=c(1), bs=c('cc')) +
                    #ti(hour, k=", c(hour_df), ", d=c(1), bs=c('cc'), by=alt) + 
  formel <- substr(formel, start = 0, stop =  (nchar(formel) - 3))
  formel <- paste0("ga(~", formel, ")")
  return(formel)
}

build_plot_mask = function(werte, dgm, mask)
{
  plot_area <- raster(nrows = nrow(dgm), ncols = ncol(dgm), xmn=xmin(dgm), xmx=xmax(dgm), ymn=ymin(dgm), ymx=ymax(dgm))
  values(plot_area) <- NA
  values(plot_area) <- werte
  plot_area_mask <- mask(plot_area, mask)
  return(plot_area_mask)
}


stepstr = function(i){
  if (i <= 9) {
    stepstr <- paste0("00",i)
  } else if (i < 100){
    stepstr <- paste0("0",i)
  } else {
    stepstr <- i
  } 
  return(stepstr)
}
