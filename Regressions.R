library(readxl)
TEData <- read_excel("xls/TEData.xlsx", col_types = c("skip", 
                                                      "numeric", "numeric", "numeric", "numeric", 
                                                       "numeric", "text", "date"))
View(TEData)

Midfield <- log(TEData$MID)
Forward <- log(TEData$FW)/Midfield
Defense <- log(TEData$D)/Midfield
Pts <- log(TEData$Points)/Midfield

mod.ols <- lm(Pts ~ Forward + Defense)

# starts writing to output file
sink('regression-output.txt')

summary(mod.ols)

lm(formula = Pts ~ Forward + Defense)

library(car)
durbinWatsonTest(mod.ols, max.lag=5)

# alternative measre of DW stat

library(lmtest)
dwtest(mod.ols, alternative="two.sided")

library(nlme)
mod.gls <- gls(Pts ~ Forward + Defense, correlation=corARMA(p=2), method="ML")
summary(mod.gls)

# testing for other correlations
mod.gls.3 <- update(mod.gls, correlation=corARMA(p=3)) #AR(3)
mod.gls.1 <- update(mod.gls, correlation=corARMA(p=1)) #AR(1)
mod.gls.0 <- update(mod.gls, correlation=NULL) #no correlation

# display results
anova(mod.gls, mod.gls.1)
anova(mod.gls, mod.gls.0)
anova(mod.gls, mod.gls.3)

# Calculate R-Squared by comparing to a linear model and calculating the squared residuals
R2 <- cor(TEData$Points, predict(mod.gls))^2
R2

# stops writing to output file
sink()

# Append more stuff to output file
sink('regression-output.txt', append = TRUE)
cat("These results are based on the panel data from the Python output TEData. This is the random effects model and need to 
    compare it with the fixed-effects (within) model")
sink()

#Within estimation (fixed effects model) 
#Removes the fixed effect by demeaning individual effects from each variable (the so called within estimator) need multiple seasons to run
g <- TEData
for (i in unique(TEData$Year)) {
    timemean <- mean(TEData[TEData$Year==i,])
    g$Points[TEData$Year==i] <- TEData$Points[TEData$Year==i]-timemean["Points"]
    g$FW[TEData$Year==i] <- TEData$FW[TEData$Year==i]-timemean["FW"]
    g$D[TEData$Year==i] <- TEData$D[TEData$Year==i]-timemean["D"]
 }
