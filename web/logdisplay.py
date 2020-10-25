#!/usr/bin/python
#######################################
# Log display for RpiThermostat       #
# 2014-04-13                          #
# modified 2020-10-24                 #
# Eric Adler                          #
#######################################

sqlite_database = "../main/thermo.sqlite"

print "importing"
from datetime import datetime, timedelta
import time

from scipy import signal
import numpy as np

import sqlite3

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
statuses = { 1    : 70.8, #warming
             2    : 69.2, #cooling
             3    : 70.0, #at target
             0    : 70.2  #Hold-off
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
logdataend    = int(time.time())
logdatastart  = logdataend - 691200  #8 days * 24 hours/day * 60 minutes/hour * 60 seconds/minute
logdatastart2 = logdataend - 100800  #28 hours * 60 minutes/hour * 60 seconds/minute
logdatastart3 = logdataend - 7200    #2 hours * 60 minutes/hour * 60 seconds/minute
print "Start of chart: ", datetime.utcfromtimestamp(logdatastart).strftime('%Y-%m-%d %H:%M:%S')
print "Start of chart2:", datetime.utcfromtimestamp(logdatastart2).strftime('%Y-%m-%d %H:%M:%S')
print "Start of chart3:", datetime.utcfromtimestamp(logdatastart3).strftime('%Y-%m-%d %H:%M:%S')
print "End of chart:   ", datetime.utcfromtimestamp(logdataend).strftime('%Y-%m-%d %H:%M:%S')

print "reading log database"
dbconn = sqlite3.connect(sqlite_database)
db = dbconn.cursor()

db.execute("SELECT * FROM temp_log WHERE datetime >= " + str(logdatastart) + ";")
      # VALUES (" + str(int(time.time())) + "," + str(comp_temp) +");"
lines = db.fetchall()
for line in lines:
  logdata_avg.append([line[0], float(line[1])]) #datetime, number

db.execute("SELECT * FROM target_log WHERE datetime >= " + str(logdatastart) + ";")
      # VALUES (" + str(int(time.time())) + "," + str(target_temp) + "," + str(targethigh) + "," + str(targetlow) + "," + str(hysteresis) + ");"
lines = db.fetchall()
for line in lines:
  logdata_target.append([line[0], float(line[1])])       #datetime, target
  logdata_target_high.append([line[0], float(line[2])])  #datetime, hightarget
  logdata_target_low.append([line[0], float(line[3])])   #datetime, lowtarget

db.execute("SELECT * FROM status_log WHERE datetime >= " + str(logdatastart) + ";")
lines = db.fetchall()
for line in lines:
  logdata_status.append([line[0], statuses[line[1]]])   #datetime, status

print "Log data loaded"
dbconn.close()
print "log database closed"

if len(logdata_status) == 0:
  raise Exception('Status array empty.')

print "Converting date formats"
logdata_avg_dates = [mdates.date2num(datetime.fromtimestamp(item[0])) for item in logdata_avg]
logdata_avg_values = [item[1] for item in logdata_avg]

logdata_target_dates = [mdates.date2num(datetime.fromtimestamp(item[0])) for item in logdata_target]
logdata_target_values = [item[1] for item in logdata_target]

logdata_target_high_dates = [mdates.date2num(datetime.fromtimestamp(item[0])) for item in logdata_target_high]
logdata_target_high_values = [item[1] for item in logdata_target_high]

logdata_target_low_dates = [mdates.date2num(datetime.fromtimestamp(item[0])) for item in logdata_target_low]
logdata_target_low_values = [item[1] for item in logdata_target_low]

logdata_status_dates = [mdates.date2num(datetime.fromtimestamp(item[0])) for item in logdata_status]
logdata_status_values = [item[1] for item in logdata_status]

print "handling data"
array_avg = np.array((logdata_avg_dates, logdata_avg_values))
print "Avg array built"
try:
  array_avg_y = moving_average(array_avg[:,1], 1500)
  print "Moving avg 1500 array built"
except:
  arravg_len = len(array_avg)
  array_avg_y = moving_average(array_avg[:,1], arravg_len-1) 
  print "Moving avg {0} array built".format(arravg_len)
array_status = np.array((logdata_status_dates, logdata_status_values))
print "Status array built"
array_upperbound = np.array((logdata_target_high_dates, logdata_target_high_values))
print "upper bound array built"
array_lowerbound = np.array((logdata_target_low_dates, logdata_target_high_values))
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

#ax.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f'))
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
