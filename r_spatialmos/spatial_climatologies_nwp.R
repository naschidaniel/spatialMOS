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
source("./r_spatialmos/r_middleware/functions.R")

# Parse Inputs
required_climatologies_model_inputs <- TRUE
required_gamlss_model_inputs <- FALSE
source("./r_spatialmos/r_middleware/gamlss_crch_model_optparse.R")


# Main
# Predict the Modellclimatetologie
dayseq <- seq(daybegin,dayend,by=1)
source("./r_spatialmos/gamlss_crch_model.R.conf")

folder <- "climate_samos_nwp"
spatial_alt_area_df <- read_feather("./data/get_available_data/gadm/spatial_alt_area_df.feather")

climate_nwp_files = list.files(path = paste0("./data/spatialmos_climatology/gam/", parameter, "/climate_nwp/"), pattern=".csv", full.names = TRUE, recursive = FALSE)

allpredictions <- length(climate_nwp_files) * length(dayseq)
pb <- txtProgressBar(min = 0, max = allpredictions, style = 3)
j <- 0
for (i in 1:length(climate_nwp_files)){
  climate <- read.csv(file=climate_nwp_files[i], sep=";", header = TRUE)
  dayminute <- unique(climate$dayminute)
  stepstr <- substr(climate_nwp_files[i], start=nchar(climate_nwp_files[i])-6, stop=nchar(climate_nwp_files[i])-4)
  load(paste0("./data/spatialmos_climatology/gam/", parameter, "/gam_nwp/gam_nwp_", parameter, "_", stepstr, ".RData"))
  load(paste0("./data/spatialmos_climatology/gam/", parameter, "/gam_nwp/gam_nwp_log_sd_", parameter, "_", stepstr, ".RData"))
  
  for (yday in dayseq){
    daystring <- sprintf("%02d",yday)
    datestring <- as.character(as.Date(yday, origin = "2018-12-31"))
    
    data_path_climatologies <- paste0("./data/spatialmos_climatology/gam/", parameter, "/", folder)
    dir.create(file.path(data_path_climatologies), showWarnings = FALSE)
    
    filename_feather <- paste0(data_path_climatologies, "/yday_", daystring, "_dayminute_", as.character(unique(climate$dayminute)), "_step_", stepstr, ".feather")
    print(filename_feather)
    if (!file.exists(filename_feather)){
      predict_climate_day_df <- data.frame(yday = yday, dayminute=dayminute, alt = spatial_alt_area_df["alt"], lon= spatial_alt_area_df["lon"], lat=spatial_alt_area_df["lat"])
      predict_climate_day_df_na_omit <- na.omit(predict_climate_day_df)

      mean_fit = predict(gam_nwp_climate, data = climate, newdata=predict_climate_day_df_na_omit, what= "mu", type="response")
      mean_sd = predict(gam_nwp_climate, data = climate, newdata=predict_climate_day_df_na_omit, what= "sigma", type="response")
      
      log_spread_fit = predict(gam_nwp_log_sd, data = climate, newdata=predict_climate_day_df_na_omit, what= "mu", type="response")
      log_spread_sd = predict(gam_nwp_log_sd, data = climate, newdata=predict_climate_day_df_na_omit, what= "sigma", type="response")

      save_predict_climate_day_df <- cbind(predict_climate_day_df_na_omit, mean_fit)
      save_predict_climate_day_df <- cbind(save_predict_climate_day_df, mean_sd)
      save_predict_climate_day_df <- cbind(save_predict_climate_day_df, log_spread_fit)
      save_predict_climate_day_df <- cbind(save_predict_climate_day_df, log_spread_sd)
      
      # export GEFS Reforecast climatologies for further processing in Python 
      write_feather(save_predict_climate_day_df, filename_feather)
      
      # erase main memory
      rm(predict_climate_day_df)
      rm(predict_climate_day_df_na_omit)
      rm(save_predict_climate_day_df)
      rm(mean_fit)
      rm(mean_sd)
      rm(log_spread_fit)
      rm(log_spread_sd)
    }
    diff_time = Sys.time() - start_time
    print(diff_time)
    j = j + 1
    setTxtProgressBar(pb, j)
  }
  rm(climate)
  rm(gam_nwp_climate)
  rm(gam_nwp_log_sd)
}
close(pb)
