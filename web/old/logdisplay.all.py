#!/usr/bin/python
#######################################
# Log display for RpiThermostat       #
# 2014-04-13                          #
# Eric Adler                          #
#######################################

print "importing"
import datetime
import numpy as np
import re
import matplotlib as mpl
mpl.use('Agg')
print "importing ."
import matplotlib.colors as colors
print "importing . ."
# import matplotlib.finance as finance
# print "importing . . ."
import matplotlib.dates as mdates
# print "importing . ."
# import matplotlib.ticker as mticker
print "importing ."
import matplotlib.mlab as mlab
print "importing . ."
import matplotlib.pyplot as plt
print "importing . . ."
import matplotlib.font_manager as font_manager

# import Gnuplot, Gnuplot.funcutils

print "done importing ."

def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
#    x = np.asarray(x)
    if type=='simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()


    a =  np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a

print "defining statuses"
statuses = { "WARMING" : 4,
             "COOLING" : 8,
             "At target." : 2,
             "Hold-off." : 1
}

print "generating regexp"
regexptest = re.compile(' \\] |:  |: |\\+ | ,- | , ')

print "setting log source"
log_source = "/var/www/thermostat.log"

logdata_avg = []
logdata_target = []
logdata_target_high = []
logdata_target_low = []
logdata_status = []

logdataitem = []

print "opening log file"
logfile = open(log_source)

print "reading log file"
# logdata = logfile.read()
for line in logfile:
   logdataitem = re.split(regexptest,line.lstrip('[ ').rstrip('\n'))
   if len(logdataitem) > 1:
       if logdataitem[1] == 'AVG':
           logdata_avg.append([datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f'),float(logdataitem[2])])
       elif logdataitem[1] == 'Status':
           logdata_status.append([datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f'),statuses[logdataitem[2]]])
       elif logdataitem[1] == 'Target':
           logdata_target.append([datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f'),float(logdataitem[2])])
           logdata_target_high.append([datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f'),float(logdataitem[2])+float(logdataitem[5])])
           logdata_target_low.append([datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f'),float(logdataitem[2])-float(logdataitem[6])])
print "Log data loaded"
logfile.close()
print "log file closed"
# logdata = logdata.split("\n")
# print "split log data"
logdata = ''

print "handling data"
#x = -1
#while (len(logdataitem) <= 1):
#   x += 1
#   print "x =",x
#   logdataitem = re.split(regexptest,logdata[x].lstrip('[ '))
#   print "logdataitem =",logdataitem
#logdatastart = datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f')

logdataitem = []
x = 0
#while (len(logdataitem) <= 1):
#   x -= 1
#   print "x =",x
#   logdataitem = re.split(regexptest,logdata[x].lstrip('[ '))
#   print "logdataitem =",logdataitem
# logdataend = datetime.datetime.strptime(logdataitem[0], '%Y-%m-%d %H:%M:%S.%f')

array_avg = np.array(logdata_avg)
print "Avg array built"
logdatastart = array_avg[0,0]
print "Start of log:",logdatastart
logdataend = array_avg[-1,0]
print "End of log:  ",logdataend
array_avg1500y= moving_average(array_avg[:,1],1500)
print "Moving avg 1500 array built"
array_status = np.array(logdata_status)
print "Status array built"
array_upperbound = np.array(logdata_target_high)
print "upper bound array built"
array_lowerbound = np.array(logdata_target_low)
print "lower bound array built"

# np.save('/var/www/array_avg', array_avg)

# print array_status 

fig, ax = plt.subplots()
ax.plot(array_avg[:,0], array_avg[:,1], 'b', lw=1)
print "plotted avg array"
ax.plot(array_avg[:,0], array_avg1500y, 'r', lw=1)
print "plotted moving average (1500) array"
ax.plot(array_upperbound[:,0], array_upperbound[:,1], 'k', lw=1)
print "plotted upperbound array"
ax.plot(array_lowerbound[:,0], array_lowerbound[:,1], 'k', lw=1)
print "plotted lowerbound array"

# ax.xaxis.set_major_locator(days)
# ax.xaxis.set_major_formatter(daysFmt)
# ax.xaxis.set_minor_locator(hours)
ax.set_xlim(logdatastart,logdataend)

ax.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
#ax.format_ydata = 
ax.grid(True)

fig.autofmt_xdate()

print "formatting set, saving file..."

# plt.show()
plt.savefig('/var/www/test.png')
print "done!"

quit()

# startdate = datetime.date(2006,1,1)
# today = enddate = datetime.date.today()
# ticker = 'SPY'
# fh = finance.fetch_historical_yahoo(ticker, startdate, enddate)
# a numpy record array with fields: date, open, high, low, close, volume, adj_close)
# r = mlab.csv2rec(fh); fh.close()

r.sort()


