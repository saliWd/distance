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

class SIM_RESULT():
    device = '012345678901234567890123456789__01:23'
    rssi = -27
        

# beacon simulation variables
SIMULATE_BEACON = True
SIMULATE_TIME_SHORT = 0.1 # 0.2 is comparable to normal mode
SIMULATE_TIME_LONG  = 0.0 # 2.8 is comparable to normal mode
USE_SIM_VALS = True
SIM_VALS = [ -80, -80, -80, -80, -80, -80, -80, -80, -80, -80,
             -90, -90, -90, -90, -90, -90, -90, -90, -90, -90,
            -120,-120,-120,-120,-120,-120,-120,-120,-120,-120,
             -90, -90, -90, -90, -90, -90, -90, -90, -90, -90,
             -80, -80, -80, -80, -80, -80, -80, -80, -80, -80]

RSSI_OOR = -120 # What value do I give to out-of-range beacons?
SECS_OF_RSSIS = 60 # how long do I store values for the lane counter decision
LOOP_SLEEP_TIME = 0.2 # 0.2 secs sleep result in measurements taking 500 ms or 1000 ms, with some outliers at 1500 ms. OOR measurements however take about 3.2 seconds (timeout+sleep)
DEFAULT_MEAS = {
    'loopCnt':0,     # a counter
    'timeDiff':0,    # in milliseconds
    'addr':'xx:xx',  # string
    'rssi':RSSI_OOR, # in dBm
    'rssiAve':0      # in dBm
}

## global variables
f_textLog = open('textLog.txt', 'a') # append   
f_dataLog = open('dataLog.csv', 'a') # append
LCD = LCD_disp() # 240px high, 320px wide
LOOP_MAX = 20000

async def find_beacon(simulate:bool, loopCnt:int):
    if simulate:
        result = SIM_RESULT
        sleep(SIMULATE_TIME_SHORT)
        if USE_SIM_VALS:
            result.rssi = SIM_VALS[(loopCnt-1) % len(SIM_VALS)]
            return result
        else:
            randNum = randint(0,1)
            if randNum == 0:
                sleep(SIMULATE_TIME_LONG) # simulating time out
                return None
            else:
                result.rssi = randint(-100,-80)
                return result
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
        LCD.fill_rect(2,60,300,160,LCD.BLACK)
        LCD.text(text[0:len(text)-1],2,60,LCD.WHITE) # last character is a newline, LCD.text can't handle that        
        LCD.show_up()
    if sink['textLog']:
        f_textLog.write(text)
        f_textLog.flush()
    if sink['dataLog']:
        f_dataLog.write(text)
        f_dataLog.flush()


def print_infos(meas:dict):    
    txt_csv = "%d, %d, %s, %d, %d\n" % (meas['loopCnt'], meas['timeDiff'], meas['addr'], meas['rssi'], meas['rssiAve'])
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
    DBM_DIFF = 20
    length = len(rssiHistory)
    if length < 30: # can't make a meaningful decision on only a few values
        return
    
    middle = length / 2 # doesn't matter whether it's one off
    minVal = min(rssiHistory)

    if rssiHistory[middle] != minVal: # only look at the stuff if the minimum value is in the middle
        return

    if ((rssiHistory[0] - minVal) > DBM_DIFF) and ((rssiHistory[length-1] - minVal) > DBM_DIFF):        
        my_print(text="increase the lane counter!", sink={'serial':True,'lcd':True,'textLog':True,'dataLog':True})
        laneCounter += 1
        update_lane_disp(laneCounter)
        rssiHistory.clear() # empty the list. Don't want to increase the lane counter on the next value again
        # nb: rssiHistory is a reference, can clear it here
        return

def update_lane_disp(laneCounter:int):
    LCD.fill_rect(240,40,80,200,LCD.BLACK)
    laneText = ("%02d" % laneCounter)
    LCD.text(laneText,240,40,LCD.WHITE) # TODO: make text huge
    LCD.show_up()
    return

# main program
async def main():
    # clear the display
    LCD.bl_ctrl(100)
    LCD.fill(LCD.BLACK)
    LCD.text("Schwimm-Messer",90,17,LCD.WHITE)
    LCD.text("id   time   address   rssi   average",2,40,LCD.WHITE) # not using my_print because this shall be displayed all the time    
    LCD.show_up()

    txt_csv = "id, time_ms, address, rssi, average\n"
    my_print(text=txt_csv, sink={'serial':True,'lcd':False,'textLog':False,'dataLog':True})    

    loopCnt = 0
    lastTime = ticks_ms()
    ledOnboard = Pin("LED", Pin.OUT)
    ledOnboard.on()
    absTime_ms = 0
    laneCounter = 0

    rssiVals = [-50,-50] # taking the average of 2 measurements, that's enough
    rssiHistory = []
    
    while loopCnt < LOOP_MAX:
        meas = DEFAULT_MEAS.copy()

        loopCnt += 1
        meas['loopCnt'] = loopCnt
        
        result = await find_beacon(simulate=SIMULATE_BEACON, loopCnt=loopCnt)
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
        lane_decision(rssiHistory=rssiHistory, laneCounter=laneCounter)
        print_infos(meas=meas)
        
        ledOnboard.toggle()
        sleep(LOOP_SLEEP_TIME)
 
    f_dataLog.close()
    f_textLog.close()    

asyncio.run(main())
