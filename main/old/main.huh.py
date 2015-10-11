###############################################
# 2014-03-16                                  #
# Thermostatic control of energy consumption  #
# ## Python for Raspberry Pi     ##           #
# Eric Adler   <tonsofpcs@gmail.com>          #
###############################################

# BACKEND:
# log anything written to std-out and std-err

# variable definitions
def declarations():
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
	global signed float target_temp = 65
	global signed float current_temp(10)
	global unsigned float heat_tolerance = 2
	global unsigned float cool_tolerance = 2
	global unsigned float hysteresis = 1
	global unsigned long iterator = 0
	global unsigned int act_rate = 100, adjust_rate = 7, sample_rate = 2,
	global unsigned int LCM_rates
	global gpo_heat = 17
	global gpo_cool = 18
	global gpo_target = 22
	global gpo_hold = 23
	global gpo_warn = 24
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

def get_temp_F():
	tfile = open("/sys/bus/w1/devices/28-0000055d5974/w1_slave")
	text = tfile.read()
	tfile.close()
	secondline = text.split("\n")[1]
	temperaturedata = secondline.split(" ")[9]
	temperature = float(temperaturedata[2:])
	temperature = (temperature * 1.8 + 32000) / 1000
	return temperature

def first_runtime():
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
		Get current_temp(i) 10x to fill buffer
		write to std-err as "[timestamp] Temp reading: %d".
        
        read target_temp,heat_tolerance,cool_tolerance,hysteresis from file
        write all of above to std-out as "Target: %d, tolerances: +%u,-%u, hysteresis: +-%u".
        read act_rate, adjust_rate, sample_rate from file
        calculate least common multiple of above as LCM_rates
        write all of above to std-out as "Act every %u00ms, Adjust every %u00ms, Sample every %u00ms, reset counter every %u00ms"
}

Main loop {
        iterator++;

        if (iterator % sample_rate)==0:
                Get temp from sensor
                write to std-err as "[timestamp] Temp reading: %d"
                write to current_temp(10) and shift buffer downward, dumping current_temp(0).  (keep last 10 current_temps in memory)

        if (iterator % adjust_rate)==0:
                read target_temp,heat_tolerance,cool_tolerance from file // only do this once every n samples so that we don't slow down too much and we introduce some hysteresis

        if (iterator % act_rate)==0:
                call function Act on temperature

        wait 100ms

        if {iterator == LCM_rates}: iterator = 0
}


function - Act on temperature {
        Calculate AVG(current_temp[0-9])
        write AVG and variables(target,heat_tolerance,cool_tolerance) to std-err as "Temp AVG: %d; Target: %d; Tolerances: +%u,-%u".
        Compare AVG with variables
                > target+heat_tolerance+hysteresis //We're too warm, let's try to cool down
                        write 0 to GPO(relay1,LED1,LED2,LED3)
                        write 1 to GPO(relay2) // cool
                        write "too warm, cooling!" to std-out

                < target-cool_tolerance-hysteresis  //We're too cold, let's try to warm up
                        write 0 to GPO(relay2,LED1,LED2,LED3)
                        write 1 to GPO(relay1) // heat
                        write "too cool, warming!" to std-out

                <= target+heat_tolerance && >= target+cool_tolerance // temperature's good! Stop adjusting.
                        write 0 to GPO(relay1,relay2,LED2,LED3)
                        Write 1 to GPO(LED1) // at target
                        write "ahh, just right!" to std-out
                ELSE
                        write 1 to GPO(LED3) // hold-off
                        write "within hysteresis, holding off any state change" to std-out
}

// Input handlers:

web interface with four buttons:
*up* *down* *gone*, sets setback mode, [with a setback values stored in a file] and *coming home*, sets occupied mode [with occupied values stored in a file]

physical interfaces:
push-button for "warmup once now" - needs backend change to implement.  Will need to think on this
push-button to activate occupied mode
dual-pole switch with center-off - one way sets to 'occupied' and overrides other inputs (except maybe web with over-override password?), other way sets to 'vacant' (setback)

occupancy sensors?

time-based set-back.

time-based occupied?  I probably wouldn't use this but it wouldn't be hard to implement it.


