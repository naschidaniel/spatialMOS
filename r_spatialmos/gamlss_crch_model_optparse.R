#!/usr/bin/env Rscript
library("optparse")

option_list = list(
  make_option(c("-p", "--parm"), type="character", default=NULL, 
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
if (is.null(opt$parm)){
  print("-h Fuer mehr Infos | Bitte geben Sie eine Option für --parm ein | -p tmp_2m oder rh_2m oder wind_10m")
  quit()
}else if (opt$parm == 'tmp_2m' | opt$parm == 'rh_2m' | opt$parm == 'wind_10m'){
  name_parm <- opt$parm
  print(paste0("--parm: ", name_parm))
}else {
  print(paste0("Ihre Eingabe für ist falsch! -h fuer mehr Infos! | --parm | ", opt$parm))
  quit()
}

if (is.null(opt$validation)){
  print("-h Fuer mehr Infos | Bitte geben Sie eine Option für --validation ein | -v True oder False")
  quit()
}else if (!is.na(opt$validation)){
  validation <- opt$validation
  print(paste0("--validation: ", validation))
}else {
  print(paste0("Ihre Eingabe ist falsch! -h fuer mehr Infos! | --validation | ", opt$validation))
  quit()
}

if (validation == TRUE){
  if (is.null(opt$kfold)){
    print("-h Fuer mehr Infos | Bitte geben Sie einen Tag im Jahr für --beginn oder und --end ein | -c [Integer 1 bis 10]")
    quit()
  }else if (opt$kfold > 0 & opt$kfold <= 10){
    kfold <- opt$kfold
    print(paste0("--kfold: ", kfold))
  }else {
    print(paste0("Ihre Eingabe ist falsch! -h fuer mehr Infos! | --kfold | ", opt$kfold))
    quit()
  }
}
print("---------------------------------------")
