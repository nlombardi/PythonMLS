import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats.stats import pearsonr

data = pd.read_excel('/Users/nlomb/Documents/Development/Python/MLS/xls/data_all.xlsx')

# Define containers
shots, passes, accpass, shrtpass, lball, tball, crosses, dribbles, corners, fouls, rCard, yCard, intercept, tackles, \
    clearance, disposs, HShtPred, AShtPred, PredSht, HGoalPred, AGoalPred, HPointPred, APointPred, ExpPoints,\
    ExpIndPts, dHptsdPass, dHptsdApass, dHptsdDrib, dHptsdCor, dHptsdTack, dHptsdInt, dHptsdFoul, tackratio, \
    dAptsdPass, dAptsdApass, dAptsdDrib, dAptsdCor, dAptsdTack, dAptsdInt, dAptsdFoul, passratio, succtackles \
    = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], \
        [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

ppts, apts, dpts, cpts, tpts, ipts, fpts = \
    pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# List of Coefficients
coefficients = ['', 'Passes', 'AccPass', 'Dribbles', 'Corners', 'Tackles', 'Interceptions','Fouls']

# Define function to get home/away data from the dataframe and assign it to a list for regression analysis
def appendvar(Var, Col):
    count = 0
    for i in data[Col]:
        if count < 2000:
            Var.append(i)
            count += 1

def getratio(Var1, Var2, Var3):
    for i in range(len(Var1)):
        if Var2[i] != 0:
            Var3.append(Var1[i]/Var2[i])
        else:
            Var3.append(int(0))


appendvar(shots, 'Home_Shots')
appendvar(shots, 'Away_Shots')
appendvar(passes, 'Home_Passes')
appendvar(passes, 'Away_Passes')
appendvar(accpass, 'Home_Acc. Pass')
appendvar(accpass, 'Away_Acc. Pass')
appendvar(shrtpass, 'Home_ShrtPass')
appendvar(shrtpass, 'Away_ShrtPass')
appendvar(lball, 'Home_LBalls')
appendvar(lball, 'Away_LBalls')
appendvar(tball, 'Home_ThrBalls')
appendvar(tball, 'Away_ThrBalls')
appendvar(crosses, 'Home_Crosses')
appendvar(crosses, 'Away_Crosses')
appendvar(dribbles, 'Home_Drib. Att.')
appendvar(dribbles, 'Away_Drib. Att.')
appendvar(corners, 'Home_Cor')
appendvar(corners, 'Away_Cor')
appendvar(fouls, 'Home_Fouls')
appendvar(fouls, 'Away_Fouls')
appendvar(rCard, 'Away_RedCards')
appendvar(rCard, 'Home_RedCards')
appendvar(yCard, 'Away_YelCards')
appendvar(yCard, 'Home_YelCards')
appendvar(intercept, 'Away_Int')
appendvar(intercept, 'Home_Int')
appendvar(succtackles, 'Away_Succ. Tack')
appendvar(succtackles, 'Home_Succ. Tack')
appendvar(tackles, 'Away_Tackles')
appendvar(tackles, 'Home_Tackles')
appendvar(clearance, 'Away_Clear')
appendvar(clearance, 'Home_Clear')
appendvar(disposs, 'Away_Disposs')
appendvar(disposs, 'Home_Disposs')

getratio(accpass, passes, passratio)
getratio(succtackles, tackles, tackratio)

# Create a new dataframe with the pulled data
data_all = pd.DataFrame({'Shots': shots, 'Passes': passes, 'AccPass': accpass, 'PassRatio': passratio,
                         'ShrtPass': shrtpass, 'LBall': lball, 'SuccTackles': succtackles,
                         'TBall': tball, 'Crosses': crosses, 'Dribbles': dribbles, 'Corners': corners, 'Fouls': fouls,
                         'RedCards': rCard, 'YelCards': yCard, 'Interceptions': intercept,
                         'Tackles': tackles, 'TackleRatio': tackratio,
                         'Clearances': clearance, 'Disposs': disposs})

# Run OLS regression
lm = smf.ols(formula='Shots ~ PassRatio + Crosses + Dribbles + TackleRatio + Interceptions +'
                     'Clearances + RedCards + YelCards', data=data_all).fit()

lm1 = smf.ols(formula='Shots ~ AccPass + Crosses + Dribbles + SuccTackles + Interceptions +'
                      'Clearances + RedCards + YelCards', data=data_all).fit()

lm2 = smf.ols(formula='Shots ~ PassRatio + Crosses + Dribbles + SuccTackles + '
                      'Interceptions + Clearances + RedCards + YelCards', data=data_all).fit()

lm3 = smf.ols(formula='Shots ~ PassRatio + Crosses + Dribbles + SuccTackles + '
                      'Interceptions + RedCards + YelCards', data=data_all).fit()

"""
    LM3 is the most suitable model (highest F-Stat) and we get explanatory coeffcients (+'ve pass, -'ve tackles).
    All variables except clearances are significant in the 97.5% confidence interval (LM2), thus we exclude clearances 
    from our
    model.

"""

# Assign results of OLS regression to new variables
lm1.summary()
lm2.summary()
lm3.summary()

# Auxilliary Regression to check and see how correlated the regressors are to passes
lmPass = smf.ols(formula='Passes ~ ShrtPass + TBall + Crosses + Dribbles + Corners + Tackles + Interceptions + '
                 ' RedCards', data=data_all).fit()
lmPass2 = smf.ols(formula='Passes ~ ShrtPass + TBall', data=data_all).fit()

"""
    The test for multicolinearity between passes and all other regressors elicits an R2 < 0.1 signifying they are not
    strongly correlated.
    Further, regressing just short pass and throughballs on passes elicits an R2 < 0.05 showing that less than
    5% of the model is explained by the regressors. Thus, the colinearity between passes, short passes, and
    throughballs is not significant and we can conclude that our model does not suffer from multicolinearity to a high
    degree.

"""

# Calculate the Pearson Correlation Coefficient between the variables to test the multicolinearity between passes and
# types of passes
pearsonr(data_all['Passes'], data_all['ShrtPassses'])