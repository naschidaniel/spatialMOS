#!/usr/bin/env Rscript
library("optparse")

eingabecheck <- function(rawinput){
  if (is.null(rawinput)){
    print("-h Fuer mehr Infos | Bitte geben Sie einen Tag im Jahr für --beginn oder und --end ein | -b 140 -e 160 ")
    quit()
  }else if (rawinput > 0 & rawinput <= 365){
    yday <- rawinput
  }else {
    print(paste0("Ihre Eingabe ist falsch! -h fuer mehr Infos | ", rawinput))
    quit()
  }
  return(yday)
}

option_list = list(
  make_option(c("-p", "--parm"), type="character", default=NULL, 
              help="Ein Parameter | tmp_2m oder rh_2m", metavar="character"),
  make_option(c("-b", "--beginn"), type="integer", default=NULL, 
              help="Ein Tag im Jahr | <interger>", metavar="integer"),
  make_option(c("-e", "--end"), type="integer", default=NULL, 
              help="Ein Tag im Jahr | <interger>", metavar="integer")
); 

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$parm)){
  print("-h Fuer mehr Infos | Bitte geben Sie eine Option für -p ein | tmp_2m oder rh_2m oder rh_2m")
  quit()
}else if (opt$parm == 'tmp_2m' | opt$parm == 'rh_2m' | opt$parm == 'wind_10m'){
  name_parm <- opt$parm
}else {
  print(paste0("Ihre Eingabe ist falsch! -h fuer mehr Infos | ", opt$parm))
  quit()
}


daybegin <- eingabecheck(opt$beginn)
dayend <- eingabecheck(opt$end)

print("optparse Eingaben:")
print("---------------------------------------")
print(paste0("--parm: ", name_parm))
print(paste0("--beginn: ", daybegin))
print(paste0("--end: ", dayend))
print("---------------------------------------")



