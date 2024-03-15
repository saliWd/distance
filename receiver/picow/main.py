##
# using aioble library (https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble)
##
# external libraries: do once (or tools -> manage packages -> install (uasyncio is already part of micropython))
# import mip
# mip.install("aioble")

from time import sleep_ms, ticks_ms, ticks_diff
from machine import Pin #type: ignore

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)

from lcd import LCD_disp # import the display class
from BEACON_SIM import BEACON_SIM # import the simulator class

# beacon simulation variables
SIMULATE_BEACON = False
REAL_LIFE_SPEED = False
beaconSim = BEACON_SIM(REAL_LIFE_SPEED)

RSSI_OOR = -120 # What value do I give to out-of-range beacons?
SECS_OF_RSSIS = 60 # how long do I store values for the lane counter decision. TODO: not yet implemented

## global variables
f_textLog = open('logText.txt', 'a') # append
f_dataLog = open('logData.csv', 'a') # append
LCD = LCD_disp() # 240px high, 320px wide
LOOP_MAX = 20000

async def find_beacon(loopCnt:int):
    if SIMULATE_BEACON:                
        return beaconSim.get_sim_val(mode='fieldTest', loopCnt=loopCnt)
    else:
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
    if sink['lcd']: # text area of the LCD
        LCD.fill_rect(0,60,240,160,LCD.BLACK)
        LCD.text(text[0:len(text)-1],0,60,LCD.WHITE) # last character is a newline, LCD.text can't handle that
        LCD.show_up()
    if sink['textLog']:
        f_textLog.write(text)
        f_textLog.flush()
    if sink['dataLog']:
        f_dataLog.write(text)
        f_dataLog.flush()

def print_infos(meas:dict, laneCounter:int):    
    txt_csv = "%5d, %4d, %s, %4d, %4d, %4d\n" % (meas['loopCnt'], meas['timeDiff'], meas['addr'], meas['rssi'], meas['rssiAve'], laneCounter)
    my_print(text=txt_csv, sink={'serial':True,'lcd':True,'textLog':False,'dataLog':True})

# calculate an average of the last 2 measurements
# possible issue here: out of range is taking about 3 seconds whereas range measurements happen every 1 or two seconds. So, OOR should have more weight
def moving_average(rssiVals:list, meas:dict):
    rssiVals.append(meas['rssi'])
    rssiVals.pop(0)
    meas['rssiAve'] = sum(rssiVals) / 2
    return


def fill_history(rssiHistory:list, newVal:int):
    rssiHistory.append(newVal)
    if (len(rssiHistory) > SECS_OF_RSSIS): # TODO: use abs_time instead of num of measurements
        rssiHistory.pop(0) # remove the oldest one
    return

##
# lane counting conditions which have to be fullfilled:
# a: rssi goes down. b: beacon low (or out of range) c: rssi goes up
# -> whole sequence takes from 30 seconds to 2 minutes (normal 1 min per 50meter)
# beacon out-of-range measurements take 3 seconds while others take about 0.5 seconds
##
def lane_decision(rssiHistory:list, laneCounter:int):
    DBM_DIFF = 10
    length = len(rssiHistory)
    if length < 30: # can't make a meaningful decision on only a few values. TODO: maybe link to SECS_OF_RSSIS
        return False
    
    middle = int(length / 2) # doesn't matter whether it's one off
    minVal = min(rssiHistory)

    if rssiHistory[middle] != minVal: # only look at the stuff if the minimum value is in the middle
        return False

    if ((rssiHistory[0] - minVal) > DBM_DIFF) and ((rssiHistory[length-1] - minVal) > DBM_DIFF):
        my_print(text="increase the lane counter!\n", sink={'serial':True,'lcd':False,'textLog':True,'dataLog':False})
        update_lane_disp(laneCounter+1)
        rssiHistory.clear() # empty the list. Don't want to increase the lane counter on the next value again
        # nb: rssiHistory is a reference, can clear it here
        return True

def update_lane_disp(laneCounter:int):
    LCD.fill_rect(240,60,80,180,LCD.BLACK)
    if laneCounter > 99:
        return
    laneText = ("%02d" % laneCounter)
    LCD.text(laneText,240,60,LCD.RED) # TODO: make text huge
    LCD.show_up()
    # this is just debug output. To be removed again
    my_print(text="Lane counter now: "+laneText+"\n", sink={'serial':True,'lcd':False,'textLog':True,'dataLog':False})
    return

# main program
async def main():
    # clear the display
    LCD.bl_ctrl(100)
    LCD.fill(LCD.BLACK)
    LCD.text("Schwimm-Messer",90,17,LCD.WHITE)
    LCD.text("id    time addr rssi ave",2,40,LCD.WHITE) # not using my_print because this shall be displayed all the time
    LCD.show_up()

    loopCnt = 0
    lastTime = ticks_ms()
    ledOnboard = Pin("LED", Pin.OUT)
    ledOnboard.on()
    absTime_ms = 0
    laneCounter = 0
    update_lane_disp(laneCounter)
    
    txt_csv = "   id, time,  addr, rssi,  ave, lane\n"
    my_print(text=txt_csv, sink={'serial':True,'lcd':False,'textLog':False,'dataLog':True})

    rssiVals = [-50,-50] # taking the average of 2 measurements, that's enough
    rssiHistory = []
    
    while loopCnt < LOOP_MAX:
        meas = {
            'loopCnt':loopCnt, # a counter
            'timeDiff':0,      # in milliseconds
            'addr':'xx:xx',    # string
            'rssi':RSSI_OOR,   # in dBm
            'rssiAve':0        # in dBm
        }
        
        result = await find_beacon(loopCnt=loopCnt)
        if result:
            addr = "%s" % result.device # need to get string representation first
            meas['addr'] = addr[32:37] # only take the MAC part, the last 5 characters
            meas['rssi'] = result.rssi
        # else: it's not a error, just beacon out of range

        meas['timeDiff'] = ticks_diff(ticks_ms(), lastTime) # update the timeDiff
        absTime_ms += meas['timeDiff']
        lastTime = ticks_ms()
                
        moving_average(rssiVals=rssiVals, meas=meas) # average value of 0 means it's not yet valid
        fill_history(rssiHistory=rssiHistory, newVal=meas['rssiAve']) # use the averaged value        
        if lane_decision(rssiHistory=rssiHistory, laneCounter=laneCounter):
            laneCounter += 1
        print_infos(meas=meas, laneCounter=laneCounter)
        
        ledOnboard.toggle()
        loopCnt += 1
        if REAL_LIFE_SPEED:
            sleep_ms(200) # 0.2 secs sleep result in measurements taking 500 ms or 1000 ms, with some outliers at 1500 ms. OOR measurements however take about 3.2 seconds (timeout+sleep)

 
    f_dataLog.close()
    f_textLog.close()

asyncio.run(main())
