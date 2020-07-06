# A Programm to build spatial Klimatologies on Basis of Historical Data for a pre defined Area
rm(list = ls())
setwd('~/spatialMOS/')
stations = read.csv('./data/klima/stations.csv')

library(crch)
library(gamlss)
library(gamlss.add)
library(gamlss.cens)
library(gamlss.spatial)
library(foreach)
library(doParallel)
source("./r_spatialmos/functions.R")

#Einlsen des optparsers Parameter
source("./r_spatialmos/gamlss_crch_model_optparse.R")

#TODO make a Config file
source("./r_spatialmos/gam_crch_model.R.conf")

#Check ob Daten existieren
if (!dir.exists(paste0("./data/GAM/", name_parm))){
  print(paste0('Der Ordner für den Parameter ', name_parm, ' wurde nicht gefunden'))
  quit(status=1)
}

#Daten aus modellklimatologies.py einlesen
klima <- read.csv(paste0("./data/GAM/", name_parm, "/", name_parm, "_alle_stationswerte.csv"), sep=";", header = TRUE)
colnamesObsKlima <- colnames(klima)
colnamesObsKlima <- colnamesObsKlima[1:6]

#Build von klimaValidation auf Basis von Kfold
if (validation == FALSE){
  SAMOS_coef_dir <- paste0('./data/GAM/', name_parm, '/', 'SAMOS_coef')
  dir.create(SAMOS_coef_dir, showWarnings = FALSE)
  
  #Erstellen des Verzeichniss für die GAM NWP Klimatologien
  dir.create(file.path(paste0('./data/GAM/', name_parm, '/'), 'gam_nwp'), showWarnings = FALSE)

  file <- paste0("./data/GAM/", name_parm, "/gam_", name_parm, "_alle_stationswerte.RData")
} else {
  #Erstellen des Verzeichniss für die Validation GAM Klimatologien
  validationDir <- paste0("./data/GAM/", name_parm, "/validation/")
  dir.create(file.path(validationDir), showWarnings = FALSE)
  
  validation_gam_NWP_dir <- paste0('./data/GAM/', name_parm, '/validation/', 'gam_nwp')
  dir.create(file.path(validation_gam_NWP_dir), showWarnings = FALSE)
  
  validation_SAMOS_coef_dir <- paste0('./data/GAM/', name_parm, '/validation/', 'SAMOS_coef')
  dir.create(file.path(validation_SAMOS_coef_dir), showWarnings = FALSE)
  
  predictionsdir <- paste0('./data/GAM/', name_parm, '/validation/', 'predictions')
  dir.create(file.path(predictionsdir), showWarnings = FALSE)
  
  file <- paste0(validationDir, "gam_", name_parm, "_kfold_", kfold, ".RData")
  klima <- klima[which(klima$kfold != kfold),]
}

#Erstellen der GAMLSS Klimatologien
if(!file.exists(file)){
  if (validation == TRUE){
    print(paste0('GAMLSS Klimatologie für -p = ', name_parm, " und kfold -k = ", kfold, " wird erstellt!"))
  }else {
    print(paste0('GAMLSS Klimatologie für ', name_parm, " wird erstellt!"))
  }
  print(paste('Parameter       | (lon, lat) =', lat_lon_k, '| dayminute = ', dayminute_k, 'yday = ', yday_k))
  print(paste('Parameter Sigma | (lon, lat) =', lat_lon_sigma_k, '| dayminute = ', dayminute_sigma_k, 'yday = ', yday_sigma_k))
  
  gam_klima <- gamlss(obs ~ ga(~ti(lon, lat, k = lat_lon_k, d = c(2), bs = c("tp"))) + 
                                alt + 
                                pbc(dayminute, df=dayminute_k, by=alt) + 
                                pbc(yday, df=yday_k, by=alt), 
                              sigma.formula = ~ ga(~ti(lon, lat, k = lat_lon_sigma_k, d = c(2), bs = c("tp"))) + 
                                alt + 
                                pbc(dayminute, df=dayminute_sigma_k, by=alt) + 
                                pbc(yday, df=yday_sigma_k, by=alt),
                              data = klima)
  save(gam_klima, file=file)
} else {
  print(paste0("File (", file, ") existiert und wird geladen!"))
  load(file)
}



############# NWP Daten ##########
nwp_files <- list.files(path = paste0("./data/GAM/", name_parm ,"/klima_nwp"), pattern=".csv", full.names = TRUE, recursive = FALSE)

start_time <- Sys.time()

for(i in 1:length(nwp_files)){
  stepstr <- substr(nwp_files[i], start=nchar(nwp_files[i])-6, stop=nchar(nwp_files[i])-4)

  if (validation == TRUE){
    klimaNWPValidationFilename <- paste0(predictionsdir, "/samos_pred_", name_parm, "_", stepstr, "_kfold_", kfold, ".csv")
  
    if (file.exists(klimaNWPValidationFilename)){
      print(paste("Durchlauf für", nwp_files[i], "übersprungen. Validation File ------ ",  klimaNWPValidationFilename, "ist schon vorhanden ------"))
      next()
    }else{
      print(paste0('GAMLSS NWP-Klimatologie für -p = ', name_parm, " und kfold -k = ", kfold, " wird erstellt!"))
    }
  } else{
    print(paste0('GAMLSS NWP-Klimatologie für ', name_parm, " wird erstellt!"))
  }
  


  #Modellklimatologie 
  klimaNWP <- read.csv(file = nwp_files[i], sep=";", header = TRUE)
  #Crossvalidation 
  if (validation == TRUE){
    klimaNWPValidation <- klimaNWP[which(klimaNWP$kfold == kfold),]
    klimaNWP <- klimaNWP[which(klimaNWP$kfold != kfold),]
    
    gam_nwp_klimaFilename <- paste0(validation_gam_NWP_dir, "/gam_nwp_", name_parm, "_", stepstr, "_kfold_", kfold, ".RData")
    gam_nwp_log_sdFilename <- paste0(validation_gam_NWP_dir, "/gam_nwp_log_sd_", name_parm, "_", stepstr, "_kfold_", kfold, ".RData")
  }else if (validation == FALSE){
    gam_nwp_klimaFilename <- paste0("./data/GAM/", name_parm, "/gam_nwp/gam_nwp_", name_parm, "_", stepstr, ".RData")
    gam_nwp_log_sdFilename <- paste0("./data/GAM/", name_parm, "/gam_nwp/gam_nwp_log_sd_", name_parm, "_", stepstr, ".RData")
  }
  
  #########Generalized Additive Modell
  #Building the Modellklimatologie fuer NWP LOG_SD
  if (!file.exists(gam_nwp_klimaFilename)){
    diff_time = Sys.time() - start_time
    print(paste('Time:               | ', diff_time))
    print(paste('Step:               | ', stepstr))
    print(paste('NWP Parameter       | (lon, lat) =', nwp_lat_lon_k, 'yday = ', nwp_yday_k))
    print(paste('NWP Parameter Sigma | (lon, lat) =', nwp_lat_lon_sigma_k, 'yday = ', nwp_yday_sigma_k))
    print('----------------------------------------')
    
    gam_nwp_klima <- gamlss(mean ~ ga(~ti(lon, lat, k = nwp_lat_lon_k, d = c(2), bs = c("tp"))) + 
                              alt + 
                              pbc(yday, df=nwp_yday_k, by=alt), 
                            sigma.formula = ~ ga(~ti(lon, lat, k = nwp_lat_lon_sigma_k, d = c(2), bs = c("tp"))) + 
                              alt + 
                              pbc(yday, df=nwp_yday_sigma_k, by=alt),
                            data = klimaNWP)
    
    save(gam_nwp_klima, file=gam_nwp_klimaFilename)
  }else {
    print(paste0("File (", gam_nwp_klimaFilename, ") existiert und wird geladen!"))
    load(gam_nwp_klimaFilename)
  }

  #########Generalized Additive Modell
  #Building the Modellklimatologie fuer NWP LOG_SD
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
                             data = klimaNWP)
    
    save(gam_nwp_log_sd, file=gam_nwp_log_sdFilename)
  }else {
    print(paste0("File (", gam_nwp_log_sdFilename, ") existiert und wird geladen!"))
    load(gam_nwp_log_sdFilename)
  }
  
  mean_fit <- predict(gam_nwp_klima, what= "mu", type ="response")
  mean_fit_sd <- predict(gam_nwp_klima, what= "sigma", type ="response")
  
  log_spread_fit <- predict(gam_nwp_log_sd, what= "mu", type ="response")
  log_spread_fit_sd <- predict(gam_nwp_log_sd, what= "sigma", type ="response")
  
  #Observations fit
  klima_fit <- predict(gam_klima, what= "mu", type="response", data = klima, newdata = klimaNWP[colnamesObsKlima])
  klima_fit_sd <- predict(gam_klima, what= "sigma", type="response", data = klima, newdata = klimaNWP[colnamesObsKlima])

  klimaNWP <- cbind(klimaNWP, klima_fit)
  klimaNWP <- cbind(klimaNWP, klima_fit_sd)
  klimaNWP <- cbind(klimaNWP, mean_fit)
  klimaNWP <- cbind(klimaNWP, mean_fit_sd)
  klimaNWP <- cbind(klimaNWP, log_spread_fit)
  klimaNWP <- cbind(klimaNWP, log_spread_fit_sd)
  
  klima_anom <- (klimaNWP$obs - klimaNWP$klima_fit) / klimaNWP$klima_fit_sd
  mean_anom <- (klimaNWP$mean - klimaNWP$mean_fit) / klimaNWP$mean_fit_sd
  log_spread_anom <- (klimaNWP$log_spread - klimaNWP$log_spread_fit) / klimaNWP$log_spread_fit_sd
  
  klimaNWP <- cbind(klimaNWP, klima_anom)
  klimaNWP <- cbind(klimaNWP, mean_anom)
  klimaNWP <- cbind(klimaNWP, log_spread_anom)
  
  SAMOS <- crch(klimaNWP$klima_anom ~ klimaNWP$mean_anom | klimaNWP$log_spread_anom)
  SAMOS_coef <- coef(SAMOS)
  SAMOS_coef <- as.data.frame(t(c(stepstr, SAMOS_coef)))
  colnames(SAMOS_coef)<- c("step", "intercept", "mean_anom", "intercept_log_spread", "log_spread_anom")
  
  #Erstellen des Verzeichniss für die Koefezienten für NWP Klimatologien
  if (validation == FALSE){
    write.csv2(SAMOS_coef, file = paste0(SAMOS_coef_dir, "/SAMOS_coef_", name_parm, "_", stepstr, ".csv"),
               row.names=FALSE, quote = TRUE)
  }else {
    write.csv2(SAMOS_coef, file = paste0(validation_SAMOS_coef_dir, "/SAMOS_coef_", name_parm, "_", stepstr, "_kfold_", kfold, ".csv"),
               row.names=FALSE, quote = TRUE)

    #TODO Dokumentation und Check ob das so richtig ist
    klima_fit_Validation_kfold <- predict(gam_klima, what= "mu", type="response", data = klima, newdata = klimaNWPValidation[colnamesObsKlima])
    klima_fit_sd_Validation_kfold <- predict(gam_klima, what= "sigma", type="response", data = klima, newdata = klimaNWPValidation[colnamesObsKlima])
    
    mean_fit <- predict(gam_nwp_klima, what= "mu", type ="response", data = klimaNWP, newdata = klimaNWPValidation)
    mean_fit_sd <- predict(gam_nwp_klima, what= "sigma", type ="response", data = klimaNWP, newdata = klimaNWPValidation)
    
    log_spread_fit <- predict(gam_nwp_log_sd, what= "mu", type ="response", newdata = klimaNWPValidation)
    log_spread_fit_sd <- predict(gam_nwp_log_sd, what= "sigma", type ="response", newdata = klimaNWPValidation)
    
    nwp_anom <- (klimaNWPValidation$mean - mean_fit) / mean_fit_sd
    log_spread_nwp_anom <- (klimaNWPValidation$log_spread - log_spread_fit) / log_spread_fit_sd
    
    samos_anom <- SAMOS$coefficients$location[1] + SAMOS$coefficients$location[2] * nwp_anom
    samos_pred <- samos_anom * klima_fit_sd_Validation_kfold + klima_fit_Validation_kfold
    
    samos_log_anom_spread <- SAMOS$coefficients$scale[1] + SAMOS$coefficients$scale[2] * exp(log_spread_nwp_anom) #Formelcheck | auch in prediction/pointprediction.py überprüfen!!!!!!!
    #TODO Stimmt das so= laut Formel So exp(samos_log_anom_spread) * klima_fit_sd_Validation_kfold laut paper
    samos_pred_spread = samos_log_anom_spread * klima_fit_sd_Validation_kfold

    klimaNWPValidation <- cbind(klimaNWPValidation, samos_pred)
    klimaNWPValidation <- cbind(klimaNWPValidation, samos_pred_spread)
    write.csv2(klimaNWPValidation, file = klimaNWPValidationFilename,
               row.names=FALSE, quote = TRUE)
  }
  #clear Memory
  rm(klimaNWP)
}
rm(klima)
diff_time = Sys.time() - start_time
print(diff_time)
