FROM r-base

ENV TZ=UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y

RUN apt-get install gdal-bin libgdal-dev libproj-dev proj-bin -y

RUN apt-get clean all

#RUN dnf update -y

#RUN dnf install -y dnf-plugins-core epel-release make gcc gcc-c++ libcurl-devel libxml2-devel openssl-devel

#RUN dnf install -y gfortran make gcc gcc-c++ libcurl-devel libxml2-devel openssl-devel

#RUN dnf config-manager --set-enabled PowerTools

#RUN dnf install -y R

#RUN dnf clean all

RUN R -e "install.packages(c('rgdal'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('raster'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('rasterVis'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('feather'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('optparse'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('crch'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('gamlss'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('gamlss.add'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('gamlss.cens'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('gamlss.spatial'), repos='http://cran.rstudio.com/')"

#RUN dnf install -y gdal gdal-devel 

#RUN dnf install -y proj proj-devel

WORKDIR /usr/src/app
