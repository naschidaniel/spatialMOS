# A Programm to create climatetologies fuer die weitere bearbeitung
rm(list = ls())
setwd('/usr/src/app/')
start_time = Sys.time()

library(feather)
library(crch)
library(gamlss)
library(gamlss.add)
library(gamlss.cens)
library(gamlss.spatial)
library(raster)
source("./r_spatialmos/functions.R")

# Parse Inputs
required_climatologies_model_inputs <- TRUE
source("./r_spatialmos/spatial_climatologies_optparser.R")


# Main
# Predict the Modellclimatetologie
dayseq <- seq(daybegin,dayend,by=1)
source("./r_spatialmos/gam_crch_model.R.conf")

folder <- "climate_samos"
spatial_alt_area_df <- read_feather("./data/get_available_data/gadm/spatial_alt_area_df.feather")

climate <- read.csv(file=paste0("./data/GAM/", parameter, "/", parameter, "_alle_stationswerte.csv"), sep=";", header = TRUE)
load(paste0("./data/GAM/", parameter, "/gam_", parameter, "_alle_stationswerte.RData"))

#TODO Check Dayminutes
dayminutes <- sort(unique(climate$dayminute))
dayminutes <- c(0, 360, 720, 1080)

for (yday in dayseq){
  daystring <- sprintf("%02d",yday)
  datestring <- as.character(as.Date(yday, origin = "2018-12-31"))
  for (dayminute in dayminutes){
    
    data_path_climatologies <- paste0("./data/spatialmos_climatology/gam/", parameter, "/", folder)
    dir.create(file.path(data_path_climatologies), showWarnings = FALSE)
    
    filename_feather <- paste0(data_path_climatologies, "/yday_", daystring, "_dayminute_", dayminute, ".feather")
    print(filename_feather)
    if (!file.exists(filename_feather)){
      predict_climate_day_df <- data.frame(yday = yday, dayminute = dayminute, alt = spatial_alt_area_df["alt"], lon= spatial_alt_area_df["lon"], lat=spatial_alt_area_df["lat"])
      predict_climate_day_df_na_omit <- na.omit(predict_climate_day_df)
      
      climate_fit = predict(gam_climate, data = climate, newdata=predict_climate_day_df_na_omit, what= "mu", type="response")
      climate_sd = predict(gam_climate, data = climate, newdata=predict_climate_day_df_na_omit, what= "sigma", type="response")

      save_predict_climate_day_df <- cbind(predict_climate_day_df_na_omit, climate_fit)
      save_predict_climate_day_df <- cbind(save_predict_climate_day_df, climate_sd)

      # export GEFS Reforcast climatologies for further processing in Python 
      write_feather(save_predict_climate_day_df, filename_feather)
      
      # erase main memory
      rm(predict_climate_day_df)
      rm(predict_climate_day_df_na_omit)
      rm(save_predict_climate_day_df)
      rm(climate_fit)
      rm(climate_sd)
    }
    diff_time = Sys.time() - start_time
    print(diff_time)
  }
}
