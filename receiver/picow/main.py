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
rssiVals = []
ledOnboard = Pin("LED", Pin.OUT)

async def find_beacon(debug_info):
    # Scan for 3 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(3000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == "widmedia.ch":
                    return result
                else:
                    if debug_info: print("did find something but name does not match. Name is: "+result.name())
    return None

def print_infos(filehandle, loopvar, timeDiff, name, addr, rssi, movAverageFast, movAverageSlow):
    txt_csv = "%d, %d, %s, %s, %d, %d, %d\n" % (loopvar, timeDiff, name, addr, rssi, movAverageFast, movAverageSlow)
    print (txt_csv, end ='') # need the newline for the csv write. No additional new line here
    filehandle.write(txt_csv)

# calculate an average of the last 5 and 25 measurements
# issue here: out of range is taking about 5 seconds whereas range measurements happen every 1 or two seconds. So, OOR should have more weight
def moving_average(rssi):
    rssiVals.append(rssi)
    movAverageFast = RSSI_INVALID
    movAverageSlow = RSSI_INVALID
    length = len(rssiVals)
    if length >= NUM_OF_RSSIS_FAST:
        movAverageFast = sum(rssiVals[length-NUM_OF_RSSIS_FAST:length]) / NUM_OF_RSSIS_FAST # this results in an integer value
    if length > NUM_OF_RSSIS_SLOW:
        rssiVals.pop(0)
        movAverageSlow = sum(rssiVals) / (length-1) # -1 because of the pop before
    
    
    return (movAverageFast, movAverageSlow) 

####
# lane counting conditions which have to be fullfilled:
# a: detect a beacon. b: rssi goes down. c: beacon out of range. d: beacon detected again. e: rssi goes up
# -> whole sequence takes from 30 seconds to 2 minutes (normal 1 min per 50meter)
# b and e are difficult to detect. a/c/d are more robust.
# c: at least 10 seconds. Need time measurements, periods of non-detection
##

# counts the seconds in each stage (per lane)
def categorize():
  # out of range. Means the moving average is equal to the out-of-range value
  stage_oor = 0 # out of range state
  stage_decr = 0 # signal strength goes down
  stage_incr = 0 # signal strength goes up

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
    timeDiff = 100
    lastTime = ticks_ms()
    ledOnboard.on()

    while loopvar < LOOP_MAX: # while True:
        loopvar = loopvar + 1
        result = await find_beacon(debug_info=False)
        if result:
            device = result.device
            name = result.name()[0:11]
            addr = "%s" % device # need to get string representation first
            addr = addr[20:37] # only take the MAC part
            rssi = result.rssi
        else: # it's not a error, just beacon out of range
            name = 'widmedia.ch'
            addr = 'xx:xx:xx:xx:xx:xx'
            rssi = RSSI_OOR 

        timeDiff = ticks_diff(ticks_ms(), lastTime) # update the timeDiff whether a beacon has been found or not
        lastTime = ticks_ms()
                
        (movAverageFast, movAverageSlow) = moving_average(rssi) # average value of 0 means it's not yet valid
        print_infos(filehandle=filehandle, loopvar=loopvar, timeDiff=timeDiff, 
                    name=name, addr=addr, rssi=rssi, movAverageFast=movAverageFast, movAverageSlow=movAverageSlow)
        
        ledOnboard.toggle()
        sleep(SLEEP_TIME)
 
    filehandle.close()

    print("\n********\n* done *\n********")    

asyncio.run(main())
