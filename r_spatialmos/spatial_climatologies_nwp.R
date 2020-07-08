rm(list = ls())
setwd('~/spatialMOS/')
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
# Predict the Modellklimatologie
dayseq <- seq(daybegin,dayend,by=1)
#TODO kill this line commandArgs folder
source("./r_spatialmos/gam_crch_model.R.conf")

folder <- 'klima_samos_nwp'
spatial_alt_area_df <- read_feather('./data/DGM/SPATIAL_ALT_area_df.feather')

klima_nwp_files = list.files(path = paste0("./data/GAM/", name_parm, "/klima_nwp/"), pattern=".csv", full.names = TRUE, recursive = FALSE)

allpredictions <- length(klima_nwp_files) * length(dayseq)
pb <- txtProgressBar(min = 0, max = allpredictions, style = 3)
j <- 0
for (i in 1:length(klima_nwp_files)){
  klima <- read.csv(file=klima_nwp_files[i], sep=";", header = TRUE)
  dayminute <- unique(klima$dayminute)
  stepstr <- substr(klima_nwp_files[i], start=nchar(klima_nwp_files[i])-6, stop=nchar(klima_nwp_files[i])-4)
  load(paste0("./data/GAM/", name_parm, "/gam_nwp/gam_nwp_", name_parm, "_", stepstr, ".RData"))
  load(paste0("./data/GAM/", name_parm, "/gam_nwp/gam_nwp_log_sd_", name_parm, "_", stepstr, ".RData"))
  
  for (yday in dayseq){
    daystring <- sprintf("%02d",yday)
    datestring <- as.character(as.Date(yday, origin = "2018-12-31"))
    
    path_feather <- paste0("./data/GAM/", name_parm, "/", folder)
    dir.create(file.path(path_feather), showWarnings = FALSE)
    
    filename_feather <- paste0(path_feather, "/yday_", daystring, "_dayminute_", as.character(unique(klima$dayminute)), "_step_", stepstr, ".feather")
    print(filename_feather)
    if (!file.exists(filename_feather)){
      predict_klima_day_df <- data.frame(yday = yday, dayminute=dayminute, alt = spatial_alt_area_df['alt'], 
                                         lon= spatial_alt_area_df['lon'], lat=spatial_alt_area_df['lat'])
      predict_klima_day_df_na_omit <- na.omit(predict_klima_day_df)

      mean_fit = predict(gam_nwp_klima, data = klima, newdata=predict_klima_day_df_na_omit, what= "mu", type="response")
      mean_sd = predict(gam_nwp_klima, data = klima, newdata=predict_klima_day_df_na_omit, what= "sigma", type="response")
      
      log_spread_fit = predict(gam_nwp_log_sd, data = klima, newdata=predict_klima_day_df_na_omit, what= "mu", type="response")
      log_spread_sd = predict(gam_nwp_log_sd, data = klima, newdata=predict_klima_day_df_na_omit, what= "sigma", type="response")

      save_predict_klima_day_df <- cbind(predict_klima_day_df_na_omit, mean_fit)
      save_predict_klima_day_df <- cbind(save_predict_klima_day_df, mean_sd)
      save_predict_klima_day_df <- cbind(save_predict_klima_day_df, log_spread_fit)
      save_predict_klima_day_df <- cbind(save_predict_klima_day_df, log_spread_sd)
      
      #TODO Feather?
      write_feather(save_predict_klima_day_df, filename_feather)
      
      #clear Memory
      rm(predict_klima_day_df)
      rm(predict_klima_day_df_na_omit)
      rm(save_predict_klima_day_df)
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
  rm(klima)
  rm(gam_nwp_klima)
  rm(gam_nwp_log_sd)
}
close(pb)
