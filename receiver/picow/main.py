##
# using aioble library (https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble)
##
# external libraries: do once (or tools -> manage packages -> install (uasyncio is already part of micropython))
# import mip
# mip.install("aioble")

from machine import Pin #type: ignore
from time import ticks_ms, ticks_diff
import array
from math import floor

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)

# files on file system
from lcd import LCD_disp # import the display class
from BEACON_SIM import BEACON_SIM # import the simulator class

# beacon simulation variables
SIMULATE_BEACON = True
REAL_LIFE_SPEED = False
beaconSim = BEACON_SIM(REAL_LIFE_SPEED)

RSSI_OOR = -120 # What value do I give to out-of-range beacons?
SECS_OF_RSSIS = 60 # how long do I store values for the lane counter decision. TODO: not yet implemented

## global variables
f_dataLog = open('logData.csv', 'a') # append
# LCD calls the framebuf module, see https://docs.micropython.org/en/latest/library/framebuf.html
LCD = LCD_disp() # 240px high, 320px wide, see https://www.waveshare.com/wiki/Pico-ResTouch-LCD-2.8
LOOP_MAX = 20000

async def find_beacon(loopCnt:int):
    if SIMULATE_BEACON:                
        return beaconSim.get_sim_val(mode='fieldTest', loopCnt=loopCnt)
    else:
        # Scan for 2 seconds, in active mode, with very low interval/window (to maximise detection rate).
        async with aioble.scan(2000, interval_us=20000, window_us=20000, active=True) as scanner:
            async for result in scanner:
                if(result.name()): # most are empty...
                    if result.name()[0:11] == 'widmedia.ch':
                        return result
        return None

def my_print(text:str, sink:dict):
    if sink['serial']:
        print(text, end='') # text needs a newline at the end
    if sink['lcd']: # text area of the LCD
        LCD.fill_rect(0,60,320,20,LCD.BLACK) # currently only one line instead of a text box
        LCD.text(text[0:len(text)-1],0,60,LCD.WHITE) # last character is a newline, LCD.text can't handle that
        LCD.show_up()
    if sink['dataLog']:
        f_dataLog.write(text)
        f_dataLog.flush()

def print_infos(meas:dict, laneCounter:int):    
    txt_csv = "%5d, %4d, %s, %4d, %4d, %4d\n" % (meas['loopCnt'], meas['timeDiff'], meas['addr'], meas['rssi'], meas['rssiAve'], laneCounter)
    my_print(text=txt_csv, sink={'serial':True,'lcd':True,'dataLog':True})

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
        update_lane_disp(laneCounter+1)
        rssiHistory.clear() # empty the list. Don't want to increase the lane counter on the next value again
        # nb: rssiHistory is a reference, can clear it here
        return True

def update_lane_disp(laneCounter:int):
    LCD.fill_rect(130,80,190,160,LCD.BLACK)
    if laneCounter > 99:
        return
    if laneCounter > 9: # draw it only when there are two digits
        draw_digit(digit=floor(laneCounter / 10), posMsb=True)
    draw_digit(digit=(laneCounter % 10), posMsb=False)
    LCD.show_up()
    return

def draw_digit(digit:int, posMsb:bool):   
    #      a
    #    f   b
    #      g
    #    e   c
    #      d
    segments = 0
    if digit == 0:   segments=  63 # abcdef
    elif digit == 1: segments=   6 #  bc
    elif digit == 2: segments=  91 # ab de g
    elif digit == 3: segments=  79 # abcd  g
    elif digit == 4: segments= 102 #  bc  fg
    elif digit == 5: segments= 109 # a cd fg
    elif digit == 6: segments= 124 #   cdefg
    elif digit == 7: segments=   7 # abc
    elif digit == 8: segments= 127 # abcdefg
    elif digit == 9: segments= 103 # abc  fg
    else: return # error case

    # box size (for two digits) is about 190 x 160
    # one segment is 56x8, spacing is 5, thus resulting in 61x12 per segment+space
    # x-direction: between digits another 20px is reserved, thus 12+56+12 +20+ 12+56+12 = 180    
    x = 130 # start point x
    y = 80
    spc_big = 61 # 56+5
    spc_sml = 12 # 8+4

    if not posMsb:
        x = x + 2*(spc_sml) + spc_big + 20
  
    if segments % 2   > 0: draw_segment(x=x+spc_sml,         y=y,                     horiz=True)  # the a-segment is required
    if segments % 4   > 2: draw_segment(x=x+spc_big+spc_sml, y=y+spc_sml,             horiz=False) # b-segment
    if segments % 8   > 4: draw_segment(x=x+spc_big+spc_sml, y=y+2*spc_sml+spc_big,   horiz=False) # c-segment
    if segments % 16  > 8: draw_segment(x=x+spc_sml,         y=y+2*(spc_sml+spc_big), horiz=True)  # d-segment
    if segments % 32  > 16:draw_segment(x=x,                 y=y+2*spc_sml+spc_big,   horiz=False) # e-segment
    if segments % 64  > 32:draw_segment(x=x,                 y=y+spc_sml,             horiz=False) # f-segment
    if segments % 128 > 64:draw_segment(x=x+spc_sml,         y=y+spc_sml+spc_big,     horiz=True)  # g-segment
    return


def draw_segment(x:int, y:int, horiz:bool):
    if horiz:
        if (x+56 > 319) or (y+8 > 239):
            print("coord error: x=%d, y=%d, horiz=%s" % (x, y, horiz))
            return
        coord = array.array('I', [0,4, 4,0, 52,0, 56,4, 52,8, 4,8]) # unsigned integers array
    else: # vertical
        if (x+8 > 319) or (y+56 > 239):
            print("coord error: x=%d, y=%d, horiz=%s" % (x, y, horiz))
            return
        coord = array.array('I', [4,0, 0,4, 0,52, 4,56, 8,52, 8,4])
    LCD.poly(x, y, coord, LCD.WHITE, True) # array is required, can't write the coordinates directly
    return # NB: no lcd.show_up as this is called after all segments are drawn

# main program
async def main():
    # clear the display
    LCD.bl_ctrl(100)
    LCD.fill(LCD.BLACK)
    LCD.text("Schwimm-Messer",95,17,LCD.WHITE) # LCD.text etc. are framebuffer functions
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
    my_print(text=txt_csv, sink={'serial':True,'lcd':False,'dataLog':True})

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
        # loop time is about 300 ms or 800 ms, with some outliers at 1300 ms. OOR measurements however take about 2 seconds (timeout)
 
    f_dataLog.close()

asyncio.run(main())
