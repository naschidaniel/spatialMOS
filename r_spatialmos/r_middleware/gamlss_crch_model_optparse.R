#!/usr/bin/env Rscript
library("optparse")

# Functions
check_input <- function(rawinput){
  if (is.null(rawinput)){
    print("-h Get help | Please enter one day a year for --begin and --end | -b [0, ..., 364] -e [1, ..., 365]")
    quit()
  }else if (rawinput > 0 & rawinput <= 365){
    yday <- rawinput
  }else {
    print(paste0("Your entry is incorrect! | ", rawinput))
    quit()
  }
  return(yday)
}


if (required_gamlss_model_inputs && !required_climatologies_model_inputs) {
required_climatologies_model_inputs <- FALSE
}
if (required_climatologies_model_inputs) {
required_gamlss_model_inputs <- FALSE
}


option_list <- list(
  make_option(c("-p", "--parameter"), type="character", default=NULL, 
              help="Ein Parameter | tmp_2m oder rh_2m", metavar="character"),
  make_option(c("-b", "--begin"), type="integer", default=NULL, 
              help="Ein Tag im Jahr | <interger>", metavar="integer"),
  make_option(c("-e", "--end"), type="integer", default=NULL, 
              help="Ein Tag im Jahr | <interger>", metavar="integer"),
  make_option(c("-v", "--validation"), type="logical", default=NULL, 
              help="TRUE oder FALSE", metavar="character"),
  make_option(c("-k", "--kfold"), type="integer", default=NULL, 
              help="kfold ID | <interger>", metavar="integer")
); 

opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser);

print("optparse Entries:")
print("---------------------------------------")
if (is.null(opt$parameter)){
  print("-h Get help | Enter an option for --parameter | -p ['tmp_2m', 'rh_2m', 'wind_10m']")
  quit()
}else if (opt$parameter == 'tmp_2m' | opt$parameter == 'rh_2m' | opt$parameter == 'wind_10m'){
  parameter <- opt$parameter
  print(paste0("--parameter: ", parameter))
}else {
  print(paste0("Your entry is incorrect! | --parameter | ", opt$parameter))
  quit()
}

if (isTRUE(required_gamlss_model_inputs)){
  if (is.null(opt$validation)){
    print("-h Get help | Enter an option for --validation | -v [True, False]")
    quit()
  }else if (!is.na(opt$validation)){
    validation <- opt$validation
    print(paste0("--validation: ", validation))
  }else {
    print(paste0("Your entry is incorrect! | --validation | ", opt$validation))
    quit()
  }

  if (validation == TRUE){
    if (is.null(opt$kfold)){
      print("-h Get help | Enter an option for --kfold | -c [1, ..., 10]")
      quit()
    }else if (opt$kfold > 0 & opt$kfold <= 10){
      kfold <- opt$kfold
      print(paste0("--kfold: ", kfold))
    }else {
      print(paste0("Your entry is incorrect! | --kfold | ", opt$kfold))
      quit()
    }
  }
}

if (isTRUE(required_climatologies_model_inputs)){
  daybegin <- check_input(opt$begin)
  print(paste0("--begin: ", daybegin))
  dayend <- check_input(opt$end)
  print(paste0("--end: ", dayend))
  
  if ((dayend - daybegin) < 1) {
    print("Please check your entered --begin and --end options.")
    quit()
  }
}
print("---------------------------------------")
