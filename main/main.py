#!/usr/bin/python
###############################################
# 2014-03-16                                  #
# modified 2014-03-19                         #
# modified 2019-07-18                         #
# modified 2020-10-24                         #
# modified 2020-10-25                         #
# modified 2020-10-27                         #
# Thermostatic control of energy consumption  #
# ## Python for Raspberry Pi     ##           #
# Eric Adler   <tonsofpcs@gmail.com>          #
###############################################

# BACKEND:
# log anything written to std-out and std-err

# variable definitions
import datetime
import sys
from time import time
from time import sleep
import RPi.GPIO as GPIO
import collections
import sqlite3

temp_source = "/sys/bus/w1/devices/28-0000055d5974/w1_slave"   #Dallas OneWire temperature sensor location
cfg_source = "/home/pi/thermostat/thermo.cfg"      #configuration file.  See thermo.cfg for example
target_source = "/home/pi/thermostat/target.cfg"   #target temperature source file, used when config has 0.0 for target temp
calib = -1.2                                       #temperature sensor calibration adjustment, in degrees C
sqlite_database = "thermo.sqlite"                  #sqlite database for logging   TODO: configuration in sqlite

#Raspberry Pi GPO configuration
gpo_heat = 17           #heat output, to control Heating system and/or display status
gpo_cool = 18           #cool output, to control Cooling system and/or display status
gpo_target = 22         #"At target" status output
gpo_hold = 23           #"Hold-off" status output
gpo_warn = 24           #warning status output

#defaults, if no config found
target_temp = 65.0      #nominal temperature target
heat_tolerance = 2.0    #
cool_tolerance = 2.0    #
hysteresis = 1.0        #

#rate definitions
act_rate = 100          #action
adjust_rate = 7         #adjust
sample_rate = 2         #sample
LCM_rates = act_rate * adjust_rate * sample_rate

current_temp = collections.deque([], 10)
iterator = 0

calib = calib * 1000    #calibration conversion to uC

GPIO.setmode(GPIO.BCM)  #set GPIO mode!

# relay1 - heating
GPIO.setup(gpo_heat, GPIO.OUT)
# relay2 - cooling
GPIO.setup(gpo_cool, GPIO.OUT)
# LED1 - at target
GPIO.setup(gpo_target, GPIO.OUT) 
# LED2 - /!\Warning/!\
GPIO.setup(gpo_warn, GPIO.OUT) 
# LED3 - hold-off (hysteresis)
GPIO.setup(gpo_hold, GPIO.OUT) 

in_hysteresis = 1       #preset status to hysteresis (hold-off)

#read config
def read_cfg():
    global target_temp,heat_tolerance,cool_tolerance,hysteresis  #set up our stored config variables
    rfile = open(cfg_source)
    rcfg = rfile.read()
    rfile.close()
    rcfg = rcfg.split("\n")[1]
    rcfg_data = rcfg.split(",")
    target_temp = float(rcfg_data[0])
    heat_tolerance = float(rcfg_data[1])
    cool_tolerance = float(rcfg_data[2])
    hysteresis = float(rcfg_data[3])
    if (target_temp == 0):
        rfile = open(target_source)
        rcfg = rfile.read()
        rfile.close()
        rcfg_data = rcfg.split(",")
        target_temp = float(rcfg_data[0])
    print "[",datetime.datetime.now(),"] Target: ",target_temp,", Tolerances: +",heat_tolerance,",-",cool_tolerance,", hysteresis: ",hysteresis
    sys.stdout.flush()


def read_speeds():
    global act_rate, adjust_rate, sample_rate
    speed_source = "/home/pi/thermostat/thermospeed.cfg"
    sfile = open(speed_source)
    scfg = sfile.read()
    sfile.close()
    scfg = scfg.split("\n")[1]
    scfg_data = scfg.split(",")
    act_rate = int(scfg_data[0])
    adjust_rate = int(scfg_data[1])
    sample_rate = int(scfg_data[2])
    LCM_rates = act_rate * adjust_rate * sample_rate
    print "[",datetime.datetime.now(),"] Act every ",act_rate*100,"ms, Adjust every ",adjust_rate*100,"ms, Sample every ",sample_rate*100,"ms, Reset counter every ",LCM_rates*100,"ms"
    sys.stdout.flush()


def get_temp_F():
    tfile = open(temp_source)        #dallas onewire temperature sensor appears as a file through the 1w module
    text = tfile.read()
    tfile.close()
    temperature = float(text.split("\n")[1].secondline.split(" ")[9][2:])
    if ( ( temperature == 85 ) or ( temperature == -62 ) ):  #-62000 and 85000 are error returns from the sensor
        return -80                              # error reading, -80 is outside of the range in degrees F and C
    temperature = temperature + calib                       #calibration offset
    temperature = (temperature * 1.8 + 32000) / 1000        #convert C to F
    return temperature

def first_runtime():
    import datetime
    # Write 0 to GPO(relay1) // relay1 - heating
    GPIO.output(gpo_heat, GPIO.LOW)
    # Write 0 to GPO(relay2) // relay2 - cooling
    GPIO.output(gpo_cool, GPIO.LOW)
    # Write 0 to GPO(LED1) // at target
    GPIO.output(gpo_target, GPIO.LOW)
    # Write 1 to GPO(LED2) // warning
    GPIO.output(gpo_warn, GPIO.HIGH)
    # Write 0 to GPO(LED3) // hold-off (hysteresis as target is approached)
    GPIO.output(gpo_hold, GPIO.LOW)
    
    # Write "Initializing..." to std-out
    print "[",datetime.datetime.now(),"] Initializing..."
    sys.stdout.flush()
    
    for x in range (0, 10):
        newtemp = get_temp_F()
        current_temp.append(newtemp)
        print "[",datetime.datetime.now(),"] Temp reading for ",x,": ",newtemp
        sys.stdout.flush()
    
    read_cfg()
    read_speeds()

def main_loop():
    iterator = 0
    while True:
        iterator = iterator + 1
        
        if (iterator % sample_rate)==0:
            newtemp = get_temp_F()
            if (newtemp != -80):
               current_temp.append(newtemp)
        
        if (iterator % adjust_rate)==0:
            read_cfg()
        
        if (iterator % act_rate)==0:
            act_temp()
        
        sleep(0.1)
        
        if (iterator == LCM_rates):
            iterator = 0
            print "[",datetime.datetime.now(),"] reset iterator"
    

def act_temp():
    global in_hysteresis
    # Calculate AVG(current_temp[0-9])
    try:
        comp_temp = sum(current_temp)/len(current_temp)
        max_temp = max(current_temp)
    except:
        return("fault")
    
    # write AVG and variables(target,heat_tolerance,cool_tolerance) to std-err as "Temp AVG: %d; Target: %d; Tolerances: +%u,-%u".
    print "[",datetime.datetime.now(),"] Target: ",target_temp,", Tolerances: +",heat_tolerance,",-",cool_tolerance,", hysteresis: ",hysteresis
    
    print "[",datetime.datetime.now(),"] AVG: ",comp_temp
    print "[",datetime.datetime.now(),"] MAX: ",max_temp
    sys.stdout.flush()

    targethigh = target_temp + heat_tolerance
    targetlow = target_temp - cool_tolerance
    
    db = dbconn.cursor()
    
    db.execute("INSERT INTO target_log VALUES (" + str(int(time())) + "," + str(target_temp) + "," + str(targethigh) + "," + str(targetlow) + "," + str(hysteresis) + ");")
    db.execute("INSERT INTO temp_log VALUES (" + str(int(time())) + "," + str(comp_temp) +");")
    
    # > target+heat_tolerance+hysteresis //We're too warm, let's try to cool down
    if (comp_temp > (targethigh + (hysteresis * in_hysteresis))):
        GPIO.output(gpo_heat, GPIO.LOW)
        GPIO.output(gpo_target, GPIO.LOW)
        GPIO.output(gpo_warn, GPIO.LOW)
        GPIO.output(gpo_hold, GPIO.LOW)
        GPIO.output(gpo_cool, GPIO.HIGH)
        in_hysteresis = 0
        # write 1 to GPO(relay2) // cool
        print "[",datetime.datetime.now(),"] Status: COOLING"
        db.execute("INSERT INTO status_log VALUES (" + str(int(time())) + ", 2);")
        dbconn.commit()
        return("cool")
    
    # < target-cool_tolerance-hysteresis  //We're too cold, let's try to warm up
    if (comp_temp < (targetlow - (hysteresis * in_hysteresis))):
        GPIO.output(gpo_cool, GPIO.LOW)
        GPIO.output(gpo_target, GPIO.LOW)
        GPIO.output(gpo_warn, GPIO.LOW)
        GPIO.output(gpo_hold, GPIO.LOW)
        GPIO.output(gpo_heat, GPIO.HIGH)
        in_hysteresis = 0
        # write 1 to GPO(relay1) // heat
        print "[",datetime.datetime.now(),"] Status: WARMING"
        db.execute("INSERT INTO status_log VALUES (" + str(int(time())) + ", 1);")
        dbconn.commit()
        return("warm")
    
    # <= target+heat_tolerance && >= target+cool_tolerance // temperature's good! Stop adjusting.
    if ((comp_temp <= (targethigh)) and (comp_temp >= (targetlow))):
        GPIO.output(gpo_heat, GPIO.LOW)
        GPIO.output(gpo_cool, GPIO.LOW)
        GPIO.output(gpo_target, GPIO.HIGH)
        GPIO.output(gpo_warn, GPIO.LOW)
        GPIO.output(gpo_hold, GPIO.LOW)
        in_hysteresis = 1
        # write 1 to GPO(LED1) // at target
        print "[",datetime.datetime.now(),"] Status: At target."
        db.execute("INSERT INTO status_log VALUES (" + str(int(time())) + ", 3);")
        dbconn.commit()
        return("at target")
    
    # case else
    GPIO.output(gpo_heat, GPIO.LOW)
    GPIO.output(gpo_cool, GPIO.LOW)
    GPIO.output(gpo_target, GPIO.LOW)
    GPIO.output(gpo_warn, GPIO.LOW)
    GPIO.output(gpo_hold, GPIO.HIGH)
    # write 1 to GPO(LED3) // hold-off
    print "[",datetime.datetime.now(),"] Status: Hold-off."
    db.execute("INSERT INTO status_log VALUES (" + str(int(time())) + ", 0);")
    dbconn.commit()
    return("hysteresis")

dbconn = sqlite3.connect(sqlite_database)
first_runtime()
main_loop()
