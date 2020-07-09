FROM r-base

ENV TZ=UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y

RUN apt-get install gdal-bin libgdal-dev libproj-dev proj-bin -y

RUN apt-get clean all

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

RUN R -e "install.packages(c('foreach'), repos='http://cran.rstudio.com/')"

RUN R -e "install.packages(c('doParallel'), repos='http://cran.rstudio.com/')"

WORKDIR /usr/src/app
