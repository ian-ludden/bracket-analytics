# Title     : TODO
# Objective : TODO
# Created by: nbermudezs
# Created on: 11/7/18

# as seen in
# https://cran.r-project.org/web/packages/BradleyTerryScalable/vignettes/BradleyTerryScalable.html

library(BradleyTerryScalable)
library(Matrix)
library(Matrix.utils)

options("width"=300)
options("sparse.colnames"=TRUE)

for (year in 2013:2019) {
    basketball <- read.csv(paste('bradleyTerry/counts-', year, '.csv', sep=""))
    basketball_btdata <- btdata(basketball)
    basketball_fit <- btfit(basketball_btdata, a=1)
    seed_probs <- btprob(basketball_fit, as_df=TRUE)
    outfile <- paste('bradleyTerry/probs-', year, '.csv', sep="")
    write.csv(seed_probs, file=outfile)
}
