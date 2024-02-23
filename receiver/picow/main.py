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
from random import randint

LOOP_MAX = 5000
SIMULATE_BEACON = True
SIMULATE_TIME_SHORT = 0.1 # 0.2 (0.2 is comparable to normal mode)
SIMULATE_TIME_LONG  = 0.2 # 2.8 (2.8 is comparable to normal mode)
RSSI_OOR = -120 # What value do I give to out-of-range beacons?
NUM_OF_RSSIS = 5 # how many values do I take for the moving average
# 0.2 secs sleep result in measurements taking 500 ms or 1000 ms, with some outliers at 1500 ms. OOR measurements however take about 3.2 seconds (timeout+sleep)
LOOP_SLEEP_TIME = 0.2
DEFAULT_MEAS = {
    'loopCnt': 0,                # a counter
    'timeDiff': 0,               # in milliseconds
    'addr': 'xx:xx:xx:xx:xx:xx', # string
    'rssi': RSSI_OOR,            # in dBm
    'rssiAve': 0                 # in dBm
}

async def find_beacon():
    # Scan for 3 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(3000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == 'widmedia.ch':
                    return result                
    return None

def print_infos(filehandle, meas:dict):
    txt_csv = "%d, %d, %s, %d, %d\n" % (meas['loopCnt'], meas['timeDiff'], meas['addr'], meas['rssi'], meas['rssiAve'])
    print (txt_csv, end ='') # need the newline for the csv write. No additional new line here
    filehandle.write(txt_csv)

# calculate an average of the last 5 and 25 measurements
# issue here: out of range is taking about 5 seconds whereas range measurements happen every 1 or two seconds. So, OOR should have more weight
def moving_average(rssiVals:list, meas:dict):
    meas['rssiAve'] = 0 # if I can't calculate a meaningful average yet, returning 0    
    rssiVals.append(meas['rssi'])
    length = len(rssiVals)
    if length >= NUM_OF_RSSIS:
        rssiVals.pop(0)
        meas['rssiAve'] = sum(rssiVals) / (length-1) # -1 because of the pop before. This results in an integer value
    return (rssiVals, meas)

####
# lane counting conditions which have to be fullfilled:
# a: detect a beacon. b: rssi goes down. c: beacon out of range. d: beacon detected again. e: rssi goes up
# -> whole sequence takes from 30 seconds to 2 minutes (normal 1 min per 50meter)
# b and e are difficult to detect. a/c/d are more robust.
# c: at least 10 seconds. Need time measurements, periods of non-detection
##

# laneCounter increase when following stages happen in this order: stage_decr -> stage_oor -> stage_incr
def checkCriterias(laneCriterias:dict, loopCnt:int, meas:dict, oldMeas:dict):
    if (loopCnt % NUM_OF_RSSIS) > 0: # don't do this every time
        return (laneCriterias, oldMeas)

    if oldMeas['rssiAve'] == 0: # at the very beginning, I can't make comparisons because the old average is not yet valid
        return (laneCriterias, meas.copy())

    someThingChanged = False

    DELTA = 2 # maybe to do: meaningful delta value
    if meas['rssiAve'] < (oldMeas['rssiAve'] - DELTA):
        if not laneCriterias['didSeeDecr']:
            laneCriterias['didSeeDecr'] = True
            someThingChanged = True
    elif meas['rssiAve'] == RSSI_OOR:
        if laneCriterias['didSeeDecr'] and not laneCriterias['didSeeOor']:
            laneCriterias['didSeeOor'] = True
            someThingChanged = True
    elif meas['rssiAve'] > (oldMeas['rssiAve'] + DELTA):
        if laneCriterias['didSeeDecr'] and laneCriterias['didSeeOor'] and not laneCriterias['didSeeIncr']:
            laneCriterias['didSeeIncr'] = True
            someThingChanged = True

    if laneCriterias['didSeeDecr'] and laneCriterias['didSeeOor'] and laneCriterias['didSeeIncr']:
        laneTime = ticks_diff(ticks_ms(), laneCriterias['absTime'])
        laneCriterias['absTime'] = ticks_ms()
        laneCriterias['didSeeDecr'] = False
        laneCriterias['didSeeOor']  = False
        laneCriterias['didSeeIncr'] = False
        someThingChanged = True
        print("*** laneCounter + 1, laneTime: %d ***\n" % (laneTime))
    # else just return
    if someThingChanged:
        print("something changed at categorization. Comparing %d and %d" % (meas['rssiAve'], oldMeas['rssiAve']))
        print(laneCriterias)  
    return (laneCriterias, meas.copy())


# main program
async def main():
    filehandle = open('data.csv', 'a') # append
    txt_csv = "id, time_ms, address, rssi, average\n"
    print (txt_csv, end ='')
    filehandle.write(txt_csv)

    loopCnt = 0
    lastTime = ticks_ms()
    ledOnboard = Pin("LED", Pin.OUT)
    ledOnboard.on()

    rssiVals = []
    meas    = DEFAULT_MEAS.copy()
    oldMeas = DEFAULT_MEAS.copy()    

    laneCriterias = {
        'absTime':0,
        'didSeeDecr':False,
        'didSeeOor':False,
        'didSeeIncr':False
    }
    laneCriterias['absTime'] = ticks_ms()

    
    while loopCnt < LOOP_MAX: # while True:
        meas = DEFAULT_MEAS.copy()

        loopCnt += 1
        meas['loopCnt'] = loopCnt

        if SIMULATE_BEACON:
            sleep(SIMULATE_TIME_SHORT)
            randNum = randint(0,3) # 4 different values
            if randNum == 0:
                sleep(SIMULATE_TIME_LONG) # simulating time out
            else:
                meas['addr'] = '01:23:45:67:89:AB'
                meas['rssi'] = randint(-90,-45)
        else:
            result = await find_beacon()
            if result:
                addr = "%s" % result.device # need to get string representation first
                meas['addr'] = addr[20:37] # only take the MAC part
                meas['rssi'] = result.rssi
            # else: it's not a error, just beacon out of range

        meas['timeDiff'] = ticks_diff(ticks_ms(), lastTime) # update the timeDiff
        lastTime = ticks_ms()
                
        (rssiVals, meas) = moving_average(rssiVals=rssiVals, meas=meas) # average value of 0 means it's not yet valid
        print_infos(filehandle=filehandle, meas=meas)
        
        ledOnboard.toggle()
        (laneCriterias, oldMeas) = checkCriterias(laneCriterias=laneCriterias, loopCnt=loopCnt, meas=meas, oldMeas=oldMeas)
        sleep(LOOP_SLEEP_TIME)
 
    filehandle.close()
    print("\n********\n* done *\n********")
    print(laneCriterias)

asyncio.run(main())
