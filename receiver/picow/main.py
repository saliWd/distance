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

from lcd import LCD_disp # import the display class

# beacon simulation variables
SIMULATE_BEACON = False
SIMULATE_TIME_SHORT = 0.1 # 0.2 is comparable to normal mode
SIMULATE_TIME_LONG  = 0.0 # 2.8 is comparable to normal mode
USE_SIM_VALS = True
SIM_VALS = [ -80, -80, -80, -80, -80, -80, -80, -80, -80, -80,
             -90, -90, -90, -90, -90, -90, -90, -90, -90, -90,
            -120,-120,-120,-120,-120,-120,-120,-120,-120,-120,
             -90, -90, -90, -90, -90, -90, -90, -90, -90, -90,
             -80, -80, -80, -80, -80, -80, -80, -80, -80, -80]

RSSI_OOR = -120 # What value do I give to out-of-range beacons?
NUM_OF_RSSIS = 5 # how many values do I take for the moving average
LOOP_SLEEP_TIME = 0.2 # 0.2 secs sleep result in measurements taking 500 ms or 1000 ms, with some outliers at 1500 ms. OOR measurements however take about 3.2 seconds (timeout+sleep)
DEFAULT_MEAS = {
    'loopCnt': 0,                # a counter
    'timeDiff': 0,               # in milliseconds
    'addr': 'xx:xx:xx:xx:xx:xx', # string
    'rssi': RSSI_OOR,            # in dBm
    'rssiAve': 0                 # in dBm
}

## global variables
f_textLog = open('textLog.txt', 'a') # append   
f_dataLog = open('dataLog.csv', 'a') # append
LCD = LCD_disp()
LOOP_MAX = 20000

async def find_beacon():
    # Scan for 3 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(3000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == 'widmedia.ch':
                    return result
    return None

def my_print(text:str, sink:dict):
    if sink['serial']:
        print(text, end='') # text needs a newline at the end
    if sink['lcd']:
        LCD.fill(LCD.BLACK) # TODO do not clear the full disp but only the 'current line'
        LCD.text(text[0:len(text)-1],2,17,LCD.WHITE) # last character is a newline, LCD.text can't handle that
        LCD.show_up()    
    if sink['textLog']:
        f_textLog.write(text)
        f_textLog.flush()
    if sink['dataLog']:
        f_dataLog.write(text)
        f_dataLog.flush()


def print_infos(meas:dict):
    shortAddr = meas['addr']
    shortAddr = shortAddr[len(shortAddr)-5:len(shortAddr)]
    txt_csv = "%d, %d, %s, %d, %d\n" % (meas['loopCnt'], meas['timeDiff'], shortAddr, meas['rssi'], meas['rssiAve'])
    my_print(text=txt_csv, sink={'serial':True,'lcd':True,'textLog':False,'dataLog':True})
    

# calculate an average of the last 5 measurements
# issue here: out of range is taking about 5 seconds whereas range measurements happen every 1 or two seconds. So, OOR should have more weight
# could add it several times? 
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
def checkCriterias(laneInfos:list, laneCriterias:dict, loopCnt:int, meas:dict, oldMeas:dict):
    if (loopCnt % NUM_OF_RSSIS) > 0: # don't do this every time
        return (laneInfos, laneCriterias, oldMeas)

    if oldMeas['rssiAve'] == 0: # at the very beginning, I can't make comparisons because the old average is not yet valid
        return (laneInfos, laneCriterias, meas.copy())

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
        # my_print(LCD=LCD, text="\n\n*** laneCounter + 1, laneTime: %d ***\n" % (laneTime))
        laneInfos.append(laneTime)
    # else just return
    
    # if someThingChanged:
    #     my_print(LCD=LCD, text="something changed at categorization. Comparing %d and %d" % (meas['rssiAve'], oldMeas['rssiAve']))
    #     my_print(LCD=LCD, text=laneCriterias)
    
    return (laneInfos, laneCriterias, meas.copy())


# main program
async def main():
    # clear the display
    LCD.bl_ctrl(100)
    LCD.fill(LCD.BLACK)
    LCD.text("Schwimm-Messer",90,17,LCD.WHITE)
    LCD.show_up()

    txt_csv = "id, time_ms, address, rssi, average\n"
    my_print(text=txt_csv, sink={'serial':True,'lcd':True,'textLog':False,'dataLog':True})    

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

    laneInfos = []
    
    while loopCnt < LOOP_MAX:
        meas = DEFAULT_MEAS.copy()

        loopCnt += 1
        meas['loopCnt'] = loopCnt

        if SIMULATE_BEACON:
            sleep(SIMULATE_TIME_SHORT)
            if USE_SIM_VALS:
                meas['addr'] = '01:23:45:67:89:AB'
                meas['rssi'] = SIM_VALS[(loopCnt-1) % len(SIM_VALS)]
            else:
                randNum = randint(0,1)
                if randNum == 0:
                    sleep(SIMULATE_TIME_LONG) # simulating time out
                else:
                    meas['addr'] = '01:23:45:67:89:AB'
                    meas['rssi'] = randint(-100,-80)
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
        print_infos(LCD=LCD, filehandle=f_dataLog, meas=meas)
        
        ledOnboard.toggle()
        (laneInfos, laneCriterias, oldMeas) = checkCriterias(laneInfos=laneInfos, laneCriterias=laneCriterias, loopCnt=loopCnt, meas=meas, oldMeas=oldMeas)
        sleep(LOOP_SLEEP_TIME)
 
    f_dataLog.close()
    # my_print(text="\n********\n* done *\n********\n")
    
    # if len(laneInfos) > 0:
    #     my_print(LCD=LCD, text='time per lane: ')
    #     my_print(LCD=LCD, text=laneInfos)
    # else:
    #     my_print(LCD=LCD, text=laneCriterias)

asyncio.run(main())
