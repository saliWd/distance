##
# using aioble library (https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble)
##
# external libraries: do once (or tools -> manage packages -> install (uasyncio is already part of micropython))
# import mip
# mip.install("aioble")

from time import sleep, ticks_ms, ticks_diff
from machine import Pin #type: ignore

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)

LOOP_MAX = 50
RSSI_OOR = -120 # What value do I give to out-of-range beacons?
RSSI_INVALID = 0
NUM_OF_RSSIS_FAST = 5 # how many values do I take for the fast moving average
NUM_OF_RSSIS_SLOW = 25 # how many values do I take for the slow moving average
# 0.2 secs sleep result in measurements taking 500 ms or 1000 ms, with some outliers at 1500 ms. OOR measurements however take about 3.2 seconds (timeout+sleep)
SLEEP_TIME = 0.2

# global variables
rssiVals = []
ledOnboard = Pin("LED", Pin.OUT)
stages = { # keeps track of the seconds spent in each stage
  'oor': 0,  # out of range
  'incr': 0, # signal strength increasing
  'decr': 0  # signal srength decreasing
}

async def find_beacon():
    # Scan for 3 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(3000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == "widmedia.ch":
                    return result                
    return None

def print_infos(filehandle, meas):
    txt_csv = "%d, %d, %s, %s, %d, %d, %d\n" % (meas['loopvar'], meas['timeDiff'], meas['name'], meas['addr'], meas['rssi'], meas['rssiAveFast'], meas['rssiAveSlow'])
    print (txt_csv, end ='') # need the newline for the csv write. No additional new line here
    filehandle.write(txt_csv)

# calculate an average of the last 5 and 25 measurements
# issue here: out of range is taking about 5 seconds whereas range measurements happen every 1 or two seconds. So, OOR should have more weight
def moving_average(meas):
    meas['rssiAveFast'] = RSSI_INVALID
    meas['rssiAveSlow'] = RSSI_INVALID
    rssiVals.append(meas['rssi'])
    length = len(rssiVals)
    if length >= NUM_OF_RSSIS_FAST:
        meas['rssiAveFast'] = sum(rssiVals[length-NUM_OF_RSSIS_FAST:length]) / NUM_OF_RSSIS_FAST # this results in an integer value
    if length > NUM_OF_RSSIS_SLOW:
        rssiVals.pop(0)
        meas['rssiAveSlow'] = sum(rssiVals) / (length-1) # -1 because of the pop before
    return meas

####
# lane counting conditions which have to be fullfilled:
# a: detect a beacon. b: rssi goes down. c: beacon out of range. d: beacon detected again. e: rssi goes up
# -> whole sequence takes from 30 seconds to 2 minutes (normal 1 min per 50meter)
# b and e are difficult to detect. a/c/d are more robust.
# c: at least 10 seconds. Need time measurements, periods of non-detection
##

# counts the seconds in each stage (per lane)
def categorize(meas):
    if meas['rssiAveFast'] == RSSI_OOR:
        stages["oor"] += meas['timeDiff']


  # laneCounter increase when following stages happen in this order: stage_decr -> stage_oor -> stage_incr

#   if is_oor():
#       stage_oor += 3 # TODO
#   if is_decr():
#       stage_decr += 3    

#   return  

# def is_oor():
#     if (moving_average() == RSSI_OOR) and (len(rssiVals) >= NUM_OF_RSSIS_FAST): # need to have a full array to make a decision
#         return True
#     return False

# def is_decr(): # TODO
#     # need a slower moving average mechanism
#     return False


# main program
async def main():
    filehandle = open('data.csv', 'a') # append
    txt_csv = "id, time_ms, name, address, rssi, average_fast, average_slow\n"
    print (txt_csv, end ='')
    filehandle.write(txt_csv)

    loopvar = 0
    lastTime = ticks_ms()
    ledOnboard.on()
    
    while loopvar < LOOP_MAX: # while True:
        meas = {
            'loopvar': 0,                # a counter
            'timeDiff': 0,               # in milliseconds
            'name': 'widmedia.ch',       # string
            'addr': 'xx:xx:xx:xx:xx:xx', # string
            'rssi': RSSI_OOR,            # in dBm
            'rssiAveFast': 0,            # in dBm
            'rssiAveSlow': 0             # in dBm
        }

        loopvar += 1
        meas['loopvar'] = loopvar
        result = await find_beacon()
        if result:
            device = result.device
            meas['name'] = result.name()[0:11]
            addr = "%s" % device # need to get string representation first
            meas['addr'] = addr[20:37] # only take the MAC part
            meas['rssi'] = result.rssi
        # else: it's not a error, just beacon out of range

        meas['timeDiff'] = ticks_diff(ticks_ms(), lastTime) # update the timeDiff
        lastTime = ticks_ms()
                
        meas = moving_average(meas) # average value of 0 means it's not yet valid
        print_infos(filehandle=filehandle, meas=meas)
        
        ledOnboard.toggle()
        sleep(SLEEP_TIME)
 
    filehandle.close()
    print("\n********\n* done *\n********")    

asyncio.run(main())
