FROM r-base

ENV TZ=UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y

RUN apt-get install gdal-bin libgdal-dev libproj-dev proj-bin -y

RUN apt-get clean all

RUN R -e "install.packages(c('rgdal'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('raster'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('rasterVis'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('optparse'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('crch'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('gamlss'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('gamlss.add'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('gamlss.cens'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('gamlss.spatial'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('foreach'), repos='http://cran.r-project.org/')"

RUN R -e "install.packages(c('doParallel'), repos='http://cran.r-project.org/')"

WORKDIR /usr/src/app
