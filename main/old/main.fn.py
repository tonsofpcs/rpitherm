#!/usr/bin/python
###############################################
# 2014-03-16                                  #
# last modified 2014-03-17                    #
# Thermostatic control of energy consumption  #
# ## Python for Raspberry Pi     ##           #
# Eric Adler   <tonsofpcs@gmail.com>          #
###############################################

# BACKEND:
# log anything written to std-out and std-err

# variable definitions
def declarations():
    global GPIO
    import RPi.GPIO as GPIO
    import collections
    GPIO.setmode(GPIO.BCM)
    global target_temp
    target_temp = 65.0
    global current_temp
    current_temp = collections.deque([], 10)
    global heat_tolerance
    heat_tolerance = 2.0
    global cool_tolerance
    cool_tolerance = 2.0
    global hysteresis
    hysteresis = 1.0
    global iterator
    iterator = 0
    global act_rate, adjust_rate, sample_rate
    act_rate = 100
    adjust_rate = 7
    sample_rate = 2
    global LCM_rates
    LCM_rates = act_rate * adjust_rate * sample_rate
    global gpo_heat, gpo_cool, gpo_target, gpo_hold, gpo_warn
    gpo_heat = 17
    gpo_cool = 18
    gpo_target = 22
    gpo_hold = 23
    gpo_warn = 24
    global temp_source
    temp_source = "/sys/bus/w1/devices/28-0000055d5974/w1_slave"
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
    return 0


#read config
def read_cfg():
    cfg_source = "/home/pi/thermostat/thermo.cfg"
    rfile = open(cfg_source)
    rcfg = rfile.read()
    rfile.close()
    rcfg = rcfg.split("\n")[1]
    rcfg_data = rcfg.split(",")
    target_temp = float(rcfg_data[0])
    heat_tolerance = float(rcfg_data[1])
    cool_tolerance = float(rcfg_data[2])
    hysteresis = float(rcfg_data[3])
    print "Target: ",target_temp,", Tolerances: -",heat_tolerance,",+",cool_tolerance,", hysteresis: ",hysteresis

def read_speeds():
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
    print "Act every ",act_rate*100,"ms, Adjust every ",adjust_rate*100,"ms, Sample every ",sample_rate*100,"ms, Reset counter every ",LCM_rates*100,"ms"


def get_temp_F():
    tfile = open(temp_source)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = (temperature * 1.8 + 32000) / 1000
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
    print "Initializing..."
    
    for x in range (0, 9):
        newtemp = get_temp_F()
        current_temp.append(newtemp)
        print "[",datetime.datetime.now(),"] Temp reading: ",newtemp
    
    read_cfg()
    read_speeds()

def main_loop():
    import datetime
    from time import sleep
    inf = 1
    iterator = 0
    while (inf == 1):
        iterator = iterator + 1
        
        if (iterator % sample_rate)==0:
            newtemp = get_temp_F()
            print "[",datetime.datetime.now(),"] Temp reading: ",newtemp
            current_temp.append(newtemp)
        
        if (iterator % adjust_rate)==0:
            read_cfg()
        
        if (iterator % act_rate)==0:
            act_temp()
        
        sleep(0.1)
        
        if (iterator == LCM_rates): iterator = 0


def act_temp():
    # Calculate AVG(current_temp[0-9])
    comp_temp = sum(current_temp)/len(current_temp)
    # write AVG and variables(target,heat_tolerance,cool_tolerance) to std-err as "Temp AVG: %d; Target: %d; Tolerances: +%u,-%u".
    print "[",datetime.datetime.now(),"] AVG: ",comp_temp

    # > target+heat_tolerance+hysteresis //We're too warm, let's try to cool down
    if (comp_temp > (target_temp + heat_tolerance + hysteresis)):
        GPIO.output(gpo_heat, GPIO.LOW)
        GPIO.output(gpo_target, GPIO.LOW)
        GPIO.output(gpo_warn, GPIO.LOW)
        GPIO.output(gpo_hold, GPIO.LOW)
        GPIO.output(gpo_cool, GPIO.HIGH)
        # write 1 to GPO(relay2) // cool
        print "too warm, cooling!"
        return("cool")
    
    # < target-cool_tolerance-hysteresis  //We're too cold, let's try to warm up
    if (comp_temp < (target_temp - cool_tolerance - hysteresis)):
        GPIO.output(gpo_cool, GPIO.LOW)
        GPIO.output(gpo_target, GPIO.LOW)
        GPIO.output(gpo_warn, GPIO.LOW)
        GPIO.output(gpo_hold, GPIO.LOW)
        GPIO.output(gpo_heat, GPIO.HIGH)
        # write 1 to GPO(relay1) // heat
        print "too cool, warming!"
        return("warm")

    # <= target+heat_tolerance && >= target+cool_tolerance // temperature's good! Stop adjusting.
    if ((comp_temp <= (target_temp + heat_tolerance)) and (comp_temp >= (target_temp - cool_tolerance))):
        GPIO.output(gpo_heat, GPIO.LOW)
        GPIO.output(gpo_cool, GPIO.LOW)
        GPIO.output(gpo_target, GPIO.HIGH)
        GPIO.output(gpo_warn, GPIO.LOW)
        GPIO.output(gpo_hold, GPIO.LOW)
        # write 1 to GPO(LED1) // at target
        print "ahh, just right!"
        return("at target")
        
    # case else
    GPIO.output(gpo_heat, GPIO.LOW)
    GPIO.output(gpo_cool, GPIO.LOW)
    GPIO.output(gpo_target, GPIO.LOW)
    GPIO.output(gpo_warn, GPIO.LOW)
    GPIO.output(gpo_hold, GPIO.HIGH)
    # write 1 to GPO(LED3) // hold-off
    print "within hysteresis, holding off any state change"
    return("hysteresis")

declarations()
first_runtime()
main_loop()


