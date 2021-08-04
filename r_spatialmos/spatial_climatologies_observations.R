rm(list = ls())
setwd('/usr/src/app/')
start_time = Sys.time()

library(crch)
library(gamlss)
library(gamlss.add)
library(gamlss.cens)
library(gamlss.spatial)
library(raster)
source("./r_spatialmos/r_middleware/functions.R")

# Parse Inputs
required_climatologies_model_inputs <- TRUE
required_gamlss_model_inputs <- FALSE
source("./r_spatialmos/r_middleware/gamlss_crch_model_optparse.R")


# Main
# Predict the Modellclimatetologie
dayseq <- seq(daybegin,dayend,by=1)
source("./r_spatialmos/gamlss_crch_model.R.conf")


folder <- "climate_spatialmos"
spatial_alt_area_df <- read.csv("./data/get_available_data/gadm/spatial_alt_area_df.csv")

climate <- read.csv(file=paste0("./data/spatialmos_climatology/gam/", parameter, "/", parameter, "_station_observations.csv"), sep=";", header = TRUE)
load(paste0("./data/spatialmos_climatology/gam/", parameter, "/gam_", parameter, "_station_observations_and_reforecasts.RData"))

#TODO Check Dayminutes
dayminutes <- sort(unique(climate$dayminute))
dayminutes <- c(0, 360, 720, 1080)

for (yday in dayseq){
  daystring <- sprintf("%03d",yday)
  datestring <- as.character(as.Date(yday, origin = "2019-12-31"))
  for (dayminute in dayminutes){
    
    data_path_climatologies <- paste0("./data/spatialmos_climatology/gam/", parameter, "/", folder)
    dir.create(file.path(data_path_climatologies), showWarnings = FALSE)
    
    filename_csv <- paste0(data_path_climatologies, "/yday_", daystring, "_dayminute_", dayminute, ".csv")
    print(filename_csv)
    if (!file.exists(filename_csv)){
      predict_climate_day_df <- data.frame(yday = yday, dayminute = dayminute, alt = spatial_alt_area_df["alt"], lon= spatial_alt_area_df["lon"], lat=spatial_alt_area_df["lat"])
      predict_climate_day_df_na_omit <- na.omit(predict_climate_day_df)
      
      climate_fit = round(predict(gam_climate, data = climate, newdata=predict_climate_day_df_na_omit, what= "mu", type="response") ,2)
      climate_sd = round(predict(gam_climate, data = climate, newdata=predict_climate_day_df_na_omit, what= "sigma", type="response"), 2)

      save_predict_climate_day_df <- cbind(predict_climate_day_df_na_omit, climate_fit)
      save_predict_climate_day_df <- cbind(save_predict_climate_day_df, climate_sd)

      # export GEFS Reforecast climatologies for further processing in Python 
      write.csv(save_predict_climate_day_df, filename_csv)
      
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
