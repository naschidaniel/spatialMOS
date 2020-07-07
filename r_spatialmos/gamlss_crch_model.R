# A Programm to build spatial climatetologies on Basis of Historical Data for a pre defined Area
rm(list = ls())
setwd('~/spatialMOS/')
stations = read.csv('./data/climate/stations.csv')

library(crch)
library(gamlss)
library(gamlss.add)
library(gamlss.cens)
library(gamlss.spatial)
library(foreach)
library(doParallel)
source("./r_spatialmos/r_middleware/functions.R")
source("./r_spatialmos/gamlss_crch_model_optparse.R")
source("./r_spatialmos/gam_crch_model.R.conf")

# Check if GADM data are available
if (!dir.exists(paste0("./data/spatialmos_climatology/", parameter))){
  print(paste0('The folder for the parameter ', parameter, ' was not found'))
  quit(status=1)
}

# Daten aus modellclimatetologies.py einlesen
climate <- read.csv(paste0("./data/spatialmos_climatology/", parameter, "/", parameter, "station_observations_and_reforcasts.csv"), sep=";", header = TRUE)
colnamesObsclimate <- colnames(climate)
colnamesObsclimate <- colnamesObsclimate[1:6]

#Build von climateValidation auf Basis von Kfold
if (validation == FALSE){
  SAMOS_coef_dir <- paste0('./data/spatialmos_climatology/', parameter, '/', 'SAMOS_coef')
  dir.create(SAMOS_coef_dir, showWarnings = FALSE)
  
  #Erstellen des Verzeichniss für die GAM NWP climatetologien
  dir.create(file.path(paste0('./data/spatialmos_climatology/', parameter, '/'), 'gam_nwp'), showWarnings = FALSE)

  file <- paste0("./data/spatialmos_climatology/", parameter, "/gam_", parameter, "station_observations_and_reforcasts.RData")
} else {
  #Erstellen des Verzeichniss für die Validation GAM climatetologien
  validationDir <- paste0("./data/spatialmos_climatology/", parameter, "/validation/")
  dir.create(file.path(validationDir), showWarnings = FALSE)
  
  validation_gam_NWP_dir <- paste0('./data/spatialmos_climatology/', parameter, '/validation/', 'gam_nwp')
  dir.create(file.path(validation_gam_NWP_dir), showWarnings = FALSE)
  
  validation_SAMOS_coef_dir <- paste0('./data/spatialmos_climatology/', parameter, '/validation/', 'SAMOS_coef')
  dir.create(file.path(validation_SAMOS_coef_dir), showWarnings = FALSE)
  
  predictionsdir <- paste0('./data/spatialmos_climatology/', parameter, '/validation/', 'predictions')
  dir.create(file.path(predictionsdir), showWarnings = FALSE)
  
  file <- paste0(validationDir, "gam_", parameter, "_kfold_", kfold, ".RData")
  climate <- climate[which(climate$kfold != kfold),]
}

#Erstellen der GAMLSS climatetologien
if(!file.exists(file)){
  if (validation == TRUE){
    print(paste0('GAMLSS climatetologie für -p = ', parameter, " und kfold -k = ", kfold, " wird erstellt!"))
  }else {
    print(paste0('GAMLSS climatetologie für ', parameter, " wird erstellt!"))
  }
  print(paste('Parameter       | (lon, lat) =', lat_lon_k, '| dayminute = ', dayminute_k, 'yday = ', yday_k))
  print(paste('Parameter Sigma | (lon, lat) =', lat_lon_sigma_k, '| dayminute = ', dayminute_sigma_k, 'yday = ', yday_sigma_k))
  
  gam_climate <- gamlss(obs ~ ga(~ti(lon, lat, k = lat_lon_k, d = c(2), bs = c("tp"))) + 
                                alt + 
                                pbc(dayminute, df=dayminute_k, by=alt) + 
                                pbc(yday, df=yday_k, by=alt), 
                              sigma.formula = ~ ga(~ti(lon, lat, k = lat_lon_sigma_k, d = c(2), bs = c("tp"))) + 
                                alt + 
                                pbc(dayminute, df=dayminute_sigma_k, by=alt) + 
                                pbc(yday, df=yday_sigma_k, by=alt),
                              data = climate)
  save(gam_climate, file=file)
} else {
  print(paste0("File (", file, ") existiert und wird geladen!"))
  load(file)
}



############# NWP Daten ##########
nwp_files <- list.files(path = paste0("./data/spatialmos_climatology/", parameter ,"/climate_nwp"), pattern=".csv", full.names = TRUE, recursive = FALSE)

start_time <- Sys.time()

for(i in 1:length(nwp_files)){
  stepstr <- substr(nwp_files[i], start=nchar(nwp_files[i])-6, stop=nchar(nwp_files[i])-4)

  if (validation == TRUE){
    climateNWPValidationFilename <- paste0(predictionsdir, "/samos_pred_", parameter, "_", stepstr, "_kfold_", kfold, ".csv")
  
    if (file.exists(climateNWPValidationFilename)){
      print(paste("Durchlauf für", nwp_files[i], "übersprungen. Validation File ------ ",  climateNWPValidationFilename, "ist schon vorhanden ------"))
      next()
    }else{
      print(paste0('GAMLSS NWP-climatetologie für -p = ', parameter, " und kfold -k = ", kfold, " wird erstellt!"))
    }
  } else{
    print(paste0('GAMLSS NWP-climatetologie für ', parameter, " wird erstellt!"))
  }
  


  #Modellclimatetologie 
  climateNWP <- read.csv(file = nwp_files[i], sep=";", header = TRUE)
  #Crossvalidation 
  if (validation == TRUE){
    climateNWPValidation <- climateNWP[which(climateNWP$kfold == kfold),]
    climateNWP <- climateNWP[which(climateNWP$kfold != kfold),]
    
    gam_nwp_climateFilename <- paste0(validation_gam_NWP_dir, "/gam_nwp_", parameter, "_", stepstr, "_kfold_", kfold, ".RData")
    gam_nwp_log_sdFilename <- paste0(validation_gam_NWP_dir, "/gam_nwp_log_sd_", parameter, "_", stepstr, "_kfold_", kfold, ".RData")
  }else if (validation == FALSE){
    gam_nwp_climateFilename <- paste0("./data/spatialmos_climatology/", parameter, "/gam_nwp/gam_nwp_", parameter, "_", stepstr, ".RData")
    gam_nwp_log_sdFilename <- paste0("./data/spatialmos_climatology/", parameter, "/gam_nwp/gam_nwp_log_sd_", parameter, "_", stepstr, ".RData")
  }
  
  #########Generalized Additive Modell
  #Building the Modellclimatetologie fuer NWP LOG_SD
  if (!file.exists(gam_nwp_climateFilename)){
    diff_time = Sys.time() - start_time
    print(paste('Time:               | ', diff_time))
    print(paste('Step:               | ', stepstr))
    print(paste('NWP Parameter       | (lon, lat) =', nwp_lat_lon_k, 'yday = ', nwp_yday_k))
    print(paste('NWP Parameter Sigma | (lon, lat) =', nwp_lat_lon_sigma_k, 'yday = ', nwp_yday_sigma_k))
    print('----------------------------------------')
    
    gam_nwp_climate <- gamlss(mean ~ ga(~ti(lon, lat, k = nwp_lat_lon_k, d = c(2), bs = c("tp"))) + 
                              alt + 
                              pbc(yday, df=nwp_yday_k, by=alt), 
                            sigma.formula = ~ ga(~ti(lon, lat, k = nwp_lat_lon_sigma_k, d = c(2), bs = c("tp"))) + 
                              alt + 
                              pbc(yday, df=nwp_yday_sigma_k, by=alt),
                            data = climateNWP)
    
    save(gam_nwp_climate, file=gam_nwp_climateFilename)
  }else {
    print(paste0("File (", gam_nwp_climateFilename, ") existiert und wird geladen!"))
    load(gam_nwp_climateFilename)
  }

  #########Generalized Additive Modell
  #Building the Modellclimatetologie fuer NWP LOG_SD
  if (!file.exists(gam_nwp_log_sdFilename)){
    diff_time = Sys.time() - start_time
    print(paste('Time:               | ', diff_time))
    print(paste('Step:               | ', stepstr))
    print(paste('NWP LOG_SD Parameter       | (lon, lat) =', nwp_log_sd_lat_lon_k, 'yday = ', nwp_log_sd_yday_k))
    print(paste('NWP LOG_SD Parameter Sigma | (lon, lat) =', nwp_log_sd_lat_lon_sigma_k, 'yday = ', nwp_log_sd_yday_sigma_k))
    print('----------------------------------------')
    
    gam_nwp_log_sd <- gamlss(log_spread ~ ga(~ti(lon, lat, k = nwp_log_sd_lat_lon_k, d = c(2), bs = c("tp"))) +
                               alt + 
                               pbc(yday, df=nwp_log_sd_yday_k, by=alt),
                             sigma.formula = ~ ga(~ti(lon, lat, k = nwp_log_sd_lat_lon_sigma_k, d = c(2), bs = c("tp"))) + 
                               alt + 
                               pbc(yday, df=nwp_log_sd_yday_sigma_k, by=alt),
                             data = climateNWP)
    
    save(gam_nwp_log_sd, file=gam_nwp_log_sdFilename)
  }else {
    print(paste0("File (", gam_nwp_log_sdFilename, ") existiert und wird geladen!"))
    load(gam_nwp_log_sdFilename)
  }
  
  mean_fit <- predict(gam_nwp_climate, what= "mu", type ="response")
  mean_fit_sd <- predict(gam_nwp_climate, what= "sigma", type ="response")
  
  log_spread_fit <- predict(gam_nwp_log_sd, what= "mu", type ="response")
  log_spread_fit_sd <- predict(gam_nwp_log_sd, what= "sigma", type ="response")
  
  #Observations fit
  climate_fit <- predict(gam_climate, what= "mu", type="response", data = climate, newdata = climateNWP[colnamesObsclimate])
  climate_fit_sd <- predict(gam_climate, what= "sigma", type="response", data = climate, newdata = climateNWP[colnamesObsclimate])

  climateNWP <- cbind(climateNWP, climate_fit)
  climateNWP <- cbind(climateNWP, climate_fit_sd)
  climateNWP <- cbind(climateNWP, mean_fit)
  climateNWP <- cbind(climateNWP, mean_fit_sd)
  climateNWP <- cbind(climateNWP, log_spread_fit)
  climateNWP <- cbind(climateNWP, log_spread_fit_sd)
  
  climate_anom <- (climateNWP$obs - climateNWP$climate_fit) / climateNWP$climate_fit_sd
  mean_anom <- (climateNWP$mean - climateNWP$mean_fit) / climateNWP$mean_fit_sd
  log_spread_anom <- (climateNWP$log_spread - climateNWP$log_spread_fit) / climateNWP$log_spread_fit_sd
  
  climateNWP <- cbind(climateNWP, climate_anom)
  climateNWP <- cbind(climateNWP, mean_anom)
  climateNWP <- cbind(climateNWP, log_spread_anom)
  
  SAMOS <- crch(climateNWP$climate_anom ~ climateNWP$mean_anom | climateNWP$log_spread_anom)
  SAMOS_coef <- coef(SAMOS)
  SAMOS_coef <- as.data.frame(t(c(stepstr, SAMOS_coef)))
  colnames(SAMOS_coef)<- c("step", "intercept", "mean_anom", "intercept_log_spread", "log_spread_anom")
  
  #Erstellen des Verzeichniss für die Koefezienten für NWP climatetologien
  if (validation == FALSE){
    write.csv2(SAMOS_coef, file = paste0(SAMOS_coef_dir, "/SAMOS_coef_", parameter, "_", stepstr, ".csv"),
               row.names=FALSE, quote = TRUE)
  }else {
    write.csv2(SAMOS_coef, file = paste0(validation_SAMOS_coef_dir, "/SAMOS_coef_", parameter, "_", stepstr, "_kfold_", kfold, ".csv"),
               row.names=FALSE, quote = TRUE)

    #TODO Dokumentation und Check ob das so richtig ist
    climate_fit_Validation_kfold <- predict(gam_climate, what= "mu", type="response", data = climate, newdata = climateNWPValidation[colnamesObsclimate])
    climate_fit_sd_Validation_kfold <- predict(gam_climate, what= "sigma", type="response", data = climate, newdata = climateNWPValidation[colnamesObsclimate])
    
    mean_fit <- predict(gam_nwp_climate, what= "mu", type ="response", data = climateNWP, newdata = climateNWPValidation)
    mean_fit_sd <- predict(gam_nwp_climate, what= "sigma", type ="response", data = climateNWP, newdata = climateNWPValidation)
    
    log_spread_fit <- predict(gam_nwp_log_sd, what= "mu", type ="response", newdata = climateNWPValidation)
    log_spread_fit_sd <- predict(gam_nwp_log_sd, what= "sigma", type ="response", newdata = climateNWPValidation)
    
    nwp_anom <- (climateNWPValidation$mean - mean_fit) / mean_fit_sd
    log_spread_nwp_anom <- (climateNWPValidation$log_spread - log_spread_fit) / log_spread_fit_sd
    
    samos_anom <- SAMOS$coefficients$location[1] + SAMOS$coefficients$location[2] * nwp_anom
    samos_pred <- samos_anom * climate_fit_sd_Validation_kfold + climate_fit_Validation_kfold
    
    samos_log_anom_spread <- SAMOS$coefficients$scale[1] + SAMOS$coefficients$scale[2] * exp(log_spread_nwp_anom) #Formelcheck | auch in prediction/pointprediction.py überprüfen!!!!!!!
    #TODO Stimmt das so= laut Formel So exp(samos_log_anom_spread) * climate_fit_sd_Validation_kfold laut paper
    samos_pred_spread = samos_log_anom_spread * climate_fit_sd_Validation_kfold

    climateNWPValidation <- cbind(climateNWPValidation, samos_pred)
    climateNWPValidation <- cbind(climateNWPValidation, samos_pred_spread)
    write.csv2(climateNWPValidation, file = climateNWPValidationFilename,
               row.names=FALSE, quote = TRUE)
  }
  #clear Memory
  rm(climateNWP)
}
rm(climate)
diff_time = Sys.time() - start_time
print(diff_time)
