# A Programm to create Klimatologies fuer die weitere bearbeitung
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
source("./r_spatialmos/spatial_climatologies_optparser.R") #name_parm #daybegin #dayend

dayseq <- seq(daybegin,dayend,by=1)
#TODO kill this line commandArgs folder
source("./r_spatialmos/gam_crch_model.R.conf")

folder <- 'klima_samos'
spatial_alt_area_df <- read_feather('./data/DGM/SPATIAL_ALT_area_df.feather')

klima <- read.csv(file=paste0("./data/GAM/", name_parm, "/", name_parm, "_alle_stationswerte.csv"), sep=";", header = TRUE)
load(paste0("./data/GAM/", name_parm, "/gam_", name_parm, "_alle_stationswerte.RData"))

#TODO Check Dayminutes
dayminutes <- sort(unique(klima$dayminute))
dayminutes <- c(0, 360, 720, 1080)

for (yday in dayseq){
  daystring <- sprintf("%02d",yday)
  datestring <- as.character(as.Date(yday, origin = "2018-12-31"))
  for (dayminute in dayminutes){
    
    path_feather <- paste0("./data/GAM/", name_parm, "/", folder)
    dir.create(file.path(path_feather), showWarnings = FALSE)
    
    filename_feather <- paste0(path_feather, "/yday_", daystring, "_dayminute_", dayminute, ".feather")
    print(filename_feather)
    if (!file.exists(filename_feather)){
      predict_klima_day_df <- data.frame(yday = yday, dayminute = dayminute, 
                                             alt = spatial_alt_area_df['alt'], lon= spatial_alt_area_df['lon'], lat=spatial_alt_area_df['lat'])
      predict_klima_day_df_na_omit <- na.omit(predict_klima_day_df)
      
      klima_fit = predict(gam_klima, data = klima, newdata=predict_klima_day_df_na_omit, what= "mu", type="response")
      klima_sd = predict(gam_klima, data = klima, newdata=predict_klima_day_df_na_omit, what= "sigma", type="response")

      save_predict_klima_day_df <- cbind(predict_klima_day_df_na_omit, klima_fit)
      save_predict_klima_day_df <- cbind(save_predict_klima_day_df, klima_sd)
      
      write_feather(save_predict_klima_day_df, filename_feather)
      
      #clear Memory
      rm(predict_klima_day_df)
      rm(predict_klima_day_df_na_omit)
      rm(save_predict_klima_day_df)
      rm(klima_fit)
      rm(klima_sd)
    }
    diff_time = Sys.time() - start_time
    print(diff_time)
  }
}
