#!/usr/bin/env Rscript
library("optparse")

option_list = list(
  make_option(c("-p", "--parameter"), type="character", default=NULL, 
              help="Ein Parameter | tmp_2m oder rh_2m oder wind_10m", metavar="character"),
  make_option(c("-v", "--validation"), type="logical", default=NULL, 
              help="TRUE oder FALSE", metavar="character"),
  make_option(c("-k", "--kfold"), type="integer", default=NULL, 
              help="kfold ID | <interger>", metavar="integer")
); 

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);


print("optparse Eingaben:")
print("---------------------------------------")
if (is.null(opt$parameter)){
  print("-h Get help | Enter an option for --parameter | -p tmp_2m or rh_2m or wind_10m")
  quit()
}else if (opt$parameter == 'tmp_2m' | opt$parameter == 'rh_2m' | opt$parameter == 'wind_10m'){
  parameter <- opt$parameter
  print(paste0("--parameter: ", parameter))
}else {
  print(paste0("Your entry is incorrect! | --parameter | ", opt$parameter))
  quit()
}

if (is.null(opt$validation)){
  print("-h Get help | Enter an option for --validation | -v True or False")
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
    print("-h Get help | Enter an option for --kfold | -c [Integer 1 bis 10]")
    quit()
  }else if (opt$kfold > 0 & opt$kfold <= 10){
    kfold <- opt$kfold
    print(paste0("--kfold: ", kfold))
  }else {
    print(paste0("Your entry is incorrect! | --kfold | ", opt$kfold))
    quit()
  }
}
print("---------------------------------------")
