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
import matplotlib.dates as mdates
print "importing ."
import matplotlib.mlab as mlab
print "importing . ."
import matplotlib.pyplot as plt
print "importing . . ."
import matplotlib.transforms as mtransforms

print "done importing ."

def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    if type=='simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()


    a =  np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a

print "defining statuses"
statuses = { "WARMING"    : 70.8,
             "COOLING"    : 69.2,
             "At target." : 70.0,
             "Hold-off."  : 70.2
           }

print "generating regexp"
regexptest = re.compile(' \\] |:  |: |\\+ | ,- | , ')

print "setting log source"
log_source = "../main/sample.log"

logdata_avg         = []
logdata_target      = []
logdata_target_high = []
logdata_target_low  = []
logdata_status      = []
logdataitem         = []

print "opening log file"
logfile = open(log_source)

print "setting plot times"
logdataend    = datetime.datetime.now()
logdatastart  = logdataend - datetime.timedelta(days=8)
logdatastart2 = logdataend - datetime.timedelta(hours=28)
logdatastart3 = logdataend - datetime.timedelta(hours=2)
print "Start of chart: ", logdatastart
print "Start of chart2:", logdatastart2
print "Start of chart3:", logdatastart3
print "End of chart:   ", logdataend

strp = datetime.datetime.strptime
print "reading log file"
for line in logfile:
  logdataitem = re.split(regexptest,line.lstrip('[ ').rstrip('\n'))
  logdatestr = logdataitem[0]
  
  if len(logdataitem) > 1:
    if '\x00' not in logdatestr:
      try: 
        logdataitemdate = strp(logdatestr, '%Y-%m-%d %H:%M:%S.%f')
      except:
        logdataitemdate = strp(logdatestr, '%Y-%m-%d %H:%M:%S')
      logdatatype = logdataitem[1]
      if True:
        if logdatatype == 'AVG':
          logavg = logdataitem[2]
          logdata_avg.append([logdataitemdate, logavg])
        elif logdatatype == 'Target':
          logtarget        = logdataitem[2]
          loglowtolerance  = logdataitem[5]
          loghightolerance = logdataitem[6]

          logdata_target.append([logdataitemdate, logtarget])
          logdata_target_high.append([logdataitemdate, logtarget  + loglowtolerance])
          logdata_target_low.append([logdataitemdate,  logtarget  - loghightolerance])

print "Log data loaded"
logfile.close()
print "log file closed"
logdata = ''

print "handling data"

logdataitem = []
x = 0
array_avg = np.array(logdata_avg)
print "Avg array built"
array_avg1500y= moving_average(array_avg[:,1],900)
print "Moving avg 1500 array built"
array_status = np.array(logdata_status)
print "Status array built"
array_upperbound = np.array(logdata_target_high)
print "upper bound array built"
array_lowerbound = np.array(logdata_target_low)
print "lower bound array built"


fig, ax = plt.subplots()

trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)

ax.fill_between(array_status[:,0], -1, 101, where=array_status[:,1]==70.8, facecolor='red', edgecolor='none', alpha=0.3, transform=trans)
ax.fill_between(array_status[:,0], -1, 101, where=array_status[:,1]==69.2, facecolor='blue', edgecolor='none', alpha=0.3, transform=trans)
ax.fill_between(array_status[:,0], -1, 101, where=array_status[:,1]==70, facecolor='green', edgecolor='none', alpha=0.4, transform=trans)
ax.fill_between(array_status[:,0], -1, 101, where=array_status[:,1]==70.2, facecolor='green', edgecolor='none', alpha=0.2, transform=trans)

print "plotted status array"
ax.plot(array_avg[:,0], array_avg[:,1], 'b', lw=1)
print "plotted avg array"
ax.plot(array_avg[:,0], array_avg1500y, 'r', lw=1)
print "plotted moving average (1500) array"
ax.plot(array_upperbound[:,0], array_upperbound[:,1], 'k', lw=1)
print "plotted upperbound array"
ax.plot(array_lowerbound[:,0], array_lowerbound[:,1], 'k', lw=1)
print "plotted lowerbound array"

ax.set_xlim(logdatastart,logdataend)
ax.set_ylim(55,90)

ax.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
ax.grid(True)

fig.autofmt_xdate()

print "formatting set, saving file..."

plt.savefig('/var/www/week.png')

print "saving file2..."
ax.set_xlim(logdatastart2,logdataend)
plt.savefig('/var/www/day.png')

print "saving file3..."
ax.set_xlim(logdatastart3,logdataend)
plt.savefig('/var/www/hour.png')

print "done!"

quit()
r.sort()


