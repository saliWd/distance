##
# using aioble library (https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble)
##
# external libraries: do once (or tools -> manage packages -> install (uasyncio is already part of micropython))
# import mip
# mip.install("aioble")

from time import sleep, ticks_ms, ticks_diff

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)

LOOP_MAX = 20
rssiVals = []

async def find_beacon(debug_info):
    # Scan for 5 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == "widmedia.ch":
                    return result
                else:
                    if debug_info: print("did find something but name does not match. Name is: "+result.name())
    return None

def print_infos(loopvar, timeDiff, name, addr, rssi, movAverage, filehandle):    
    txt_csv = "%d, %d, %s, %s, %d, %d\n" % (loopvar, timeDiff, name, addr, rssi, movAverage)
    print (txt_csv, end ="") # need the newline for the csv write. No additional new line here
    filehandle.write(txt_csv)

# calculate an average of the last 5 measurements
def moving_average(newValue):    
    rssiVals.append(newValue)
    if len(rssiVals) > 5:
        rssiVals.pop(0) # remove the oldest entry    
    return (sum(rssiVals) / len(rssiVals)) # this results in an integer value   

# main program
async def main():
    filehandle = open('data.csv', 'a') # append
    filehandle.write('id, time_ms, name, address, rssi, rssi_average\n')

    loopvar = 0
    timeDiff = 100
    lastTime = ticks_ms()

    # while True:
    while loopvar < LOOP_MAX:
        loopvar = loopvar + 1
        result = await find_beacon(debug_info=False)
        if result:
            device = result.device
            name = result.name()[0:11]
            addr = "%s" % device # need to get string representation first...
            addr = addr[20:37] # only take the MAC part
            rssi = result.rssi            
        else: # it's not a error, just beacon out of range
            print("Loopvar %d: no beacon found" % loopvar)
            name = 'widmedia.ch'
            addr = 'xx:xx:xx:xx:xx:xx'
            rssi = -120 # this value is important. What value do I give to out-of-range beacons?

        timeDiff = ticks_diff(ticks_ms(), lastTime) # update the timeDiff whether a beacon has been found or not
        lastTime = ticks_ms()

        movAverage = moving_average(rssi)
        print_infos(loopvar=loopvar, timeDiff=timeDiff, name=name, addr=addr, rssi=rssi, movAverage=movAverage, filehandle=filehandle)        
        sleep(0.5)
 
    filehandle.close()

    print("outputting the file contents\n")
    filehandle = open('data.csv')
    print(filehandle.read())
    filehandle.close()

####
# lane counting conditions which have to be fullfilled:
# a: detect a beacon. b: rssi goes down. c: beacon out of range. d: beacon detected again. e: rssi goes up
# -> whole sequence takes from 30 seconds to 2 minutes (normal 1 min per 50meter)
# b and e are difficult to detect. a/c/d are more robust.
# c: at least 10 seconds. Need time measurements, periods of non-detection
##

asyncio.run(main())
