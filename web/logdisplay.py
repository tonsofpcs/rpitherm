#!/usr/bin/python
#######################################
# Log display for RpiThermostat       #
# 2014-04-13                          #
# Eric Adler                          #
#######################################
print "importing"
from datetime import datetime, timedelta

from scipy import signal
import numpy as np

import matplotlib as mpl
mpl.use('Agg')
print "importing ."
import matplotlib.colors as colors
print "importing . ."
import matplotlib.dates as mdates
print "importing . ."
import matplotlib.mlab as mlab
print "importing . . ."
import matplotlib.pyplot as plt
print "importing . . . ."
import matplotlib.transforms as mtransforms

print "done importing"

def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    if type=='simple':
        weights = np.ones(n)
    elif type=='exponential':
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    a = signal.fftconvolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a

print "defining statuses"
statuses = { "WARMING"    : 70.8,
             "COOLING"    : 69.2,
             "At target." : 70.0,
             "Hold-off."  : 70.2
           }

print "setting log source"
log_source = "../examples/newsample.log"

logdata_avg         = []
logdata_target      = []
logdata_target_high = []
logdata_target_low  = []
logdata_status      = []
logdataitem         = []

print "opening log file"
logfile = open(log_source, 'r')

print "setting plot times"
logdataend    = datetime.now()
logdatastart  = logdataend - timedelta(days=8)
logdatastart2 = logdataend - timedelta(hours=28)
logdatastart3 = logdataend - timedelta(hours=2)
print "Start of chart: ", logdatastart
print "Start of chart2:", logdatastart2
print "Start of chart3:", logdatastart3
print "End of chart:   ", logdataend

print "reading log file"
for line in logfile:
  logyear  = int(line[2:6])
  logmonth = int(line[7:9])
  logday   = int(line[10:12])
  loghr    = int(line[13:15])
  logmin   = int(line[16:18])
  logsec   = int(line[19:21])
  logdataitemdate = datetime(logyear, logmonth, logday,
                             loghr,   logmin,   logsec)
  if logdataitemdate >= logdatastart:
    if line[31:34] == 'AVG':
      logdata_avg.append([logdataitemdate, float(line[37:43])])
    elif line[31:37] == "Status":
      logdata_status.append([logdataitemdate, statuses[line[39:-1]]])
    elif line[31:37] == "Target":
      target = float(line[40:44])
      hightarget = target + float(line[61:64])
      lowtarget  = target - float(line[68:71])

      logdata_target.append([logdataitemdate, target])
      logdata_target_high.append([logdataitemdate, hightarget])
      logdata_target_low.append([logdataitemdate, lowtarget])

print "Log data loaded"
logfile.close()
logdata = ''
print "log file closed"

if len(logdata_status) == 0:
  raise Exception('Status array empty.')

print "handling data"
array_avg = np.array(logdata_avg)
print "Avg array built"
try:
  array_avg_y = moving_average(array_avg[:,1], 1500)
  print "Moving avg 1500 array built"
except:
  arravg_len = len(array_avg)
  array_avg_y = moving_average(array_avg[:,1], arravg_len-1) 
  print "Moving avg {0} array built".format(arravg_len)
array_status = np.array(logdata_status)
print "Status array built"
array_upperbound = np.array(logdata_target_high)
print "upper bound array built"
array_lowerbound = np.array(logdata_target_low)
print "lower bound array built"

fig, ax = plt.subplots()

trans = mtransforms.blended_transform_factory(ax.transData, 
                                              ax.transAxes)

arr_status_strs = array_status[:,0]

ax.fill_between(arr_status_strs, -1, 101, 
                where=array_status[:,1]==70.8, 
                facecolor='red', 
                edgecolor='none', 
                alpha=0.3, 
                transform=trans)

ax.fill_between(arr_status_strs, -1, 101, 
                where=array_status[:,1]==69.2, 
                facecolor='blue', 
                edgecolor='none', 
                alpha=0.3, 
                transform=trans)

ax.fill_between(arr_status_strs, -1, 101, 
                where=array_status[:,1]==70, 
                facecolor='green', 
                edgecolor='none', 
                alpha=0.4, 
                transform=trans)

ax.fill_between(arr_status_strs, -1, 101, 
                where=array_status[:,1]==70.2, 
                facecolor='green', 
                edgecolor='none', 
                alpha=0.2, 
                transform=trans)

print "plotted status array"

ax.plot(array_avg[:,0], 
        array_avg[:,1], 
        'b', 
        lw=1)
print "plotted avg array"

ax.plot(array_avg[:,0], 
        array_avg_y, 
        'r', 
        lw=1)
print "plotted moving average ({0}) array".format(len(array_avg_y))

ax.plot(array_upperbound[:,0], 
        array_upperbound[:,1], 
        'k', 
        lw=1)
print "plotted upperbound array"

ax.plot(array_lowerbound[:,0], 
        array_lowerbound[:,1], 
        'k', 
        lw=1)
print "plotted lowerbound array"

ax.set_xlim(logdatastart,logdataend)
ax.set_ylim(55,90)

ax.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
ax.grid(True)

fig.autofmt_xdate()

print "formatting set, saving file..."

plt.savefig('../week.png', dpi=50)

print "saving file2..."
ax.set_xlim(logdatastart2,logdataend)
plt.savefig('../day.png')

print "saving file3..."
ax.set_xlim(logdatastart3,logdataend)
plt.savefig('../hour.png')

print "done!"


quit()
