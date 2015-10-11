#!/usr/bin/python
#######################################
# Log display for RpiThermostat       #
# 2014-04-13                          #
# Eric Adler                          #
#######################################


import datetime
import numpy as np
print "importing ."
import matplotlib.colors as colors
print "importing . ."
# import matplotlib.finance as finance
print "importing . . ."
import matplotlib.dates as mdates
print "importing . ."
import matplotlib.ticker as mticker
print "importing ."
import matplotlib.mlab as mlab
print "importing . ."
import matplotlib.pyplot as plt
print "importing . . ."
import matplotlib.font_manager as font_manager
print "done importing ."

log_source = "/var/www/sample.log"
logfile = open(log_source)
logdata = logfile.read()
logfile.close()
logdata = logdata.split("\n")

logdataitem = []
x = -1
while (len(logdataitem) <= 1):
   x += 1
   print "x =",x
   logdataitem = logdata[x].lstrip('[ ').split(' ] ')
   print "logdataitem =",logdataitem
logdatastart = datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f')

logdataitem = []
x = 0
while (len(logdataitem) <= 1):
   x -= 1
   print "x =",x
   logdataitem = logdata[x].lstrip('[ ').split(' ] ')
   print "logdataitem =",logdataitem
logdataend = datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f')

print "Start of log:",logdatastart
print logdataend



# startdate = datetime.date(2006,1,1)
# today = enddate = datetime.date.today()
# ticker = 'SPY'
quit()


fh = finance.fetch_historical_yahoo(ticker, startdate, enddate)
# a numpy record array with fields: date, open, high, low, close, volume, adj_close)

r = mlab.csv2rec(fh); fh.close()
r.sort()


def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    x = np.asarray(x)
    if type=='simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()


    a =  np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a

