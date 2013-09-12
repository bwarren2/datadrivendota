# sudo aptitude install libcurl4-openssl-dev
# sudo aptitude install libxml2-dev
#gridSVG
install.packages("RJSONIO", repos = "http://www.omegahat.org/R", type = "source")
install.packages("gridSVG",repos='http://cran.rstudio.com/')

#rcharts
install.packages('devtools',repos='http://cran.rstudio.com/')
require('devtools')
install.packages('plyr',repos='http://cran.rstudio.com/')
install.packages('yaml',repos='http://cran.rstudio.com/')

install_github('rCharts', 'ramnathv')

