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
from micropython import const #type: ignore

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)

# files on file system
from lcd import LCD_disp # import the display class
from BEACON_SIM import BEACON_SIM # import the simulator class

# beacon simulation variables
SIMULATE_BEACON = const(True)
REAL_LIFE_SPEED = const(False)
beaconSim = BEACON_SIM(REAL_LIFE_SPEED)

RSSI_OOR = const(-120) # What value do I give to out-of-range beacons?
NUM_OF_RSSIS = const(60) # how many RSSI values do I store (for the lane counter decision). maybe to do: should use seconds instead of num of measurements

## global variables
f_dataLog = open('logData.csv', 'a') # append
# LCD calls the framebuf module, see https://docs.micropython.org/en/latest/library/framebuf.html
LCD = LCD_disp() # 240px high, 320px wide, see https://www.waveshare.com/wiki/Pico-ResTouch-LCD-2.8
LOOP_MAX = const(20000)

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
    if sink['dataLog']:
        f_dataLog.write(text)
        f_dataLog.flush()


def print_lcd_dbg(meas:dict, laneCounter:int):
    X = const(10)
    y = 80
    LINE = const(15)
    LCD.fill_rect(X,y,180,6*LINE,LCD.BLACK) # clear the area
    
    LCD.text("Loop:     %4d" % meas['loopCnt'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("Timediff: %4d" % meas['timeDiff'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("Address:  %s"  % meas['addr'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("RSSI:     %4d" % meas['rssi'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("RSSI ave: %4d" % meas['rssiAve'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("Lane:     %4d" % laneCounter,X,y,LCD.WHITE)
    LCD.show_up()


def print_infos(meas:dict, laneCounter:int):
    txt_csv = "%5d, %4d, %s, %4d, %4d, %4d\n" % (meas['loopCnt'], meas['timeDiff'], meas['addr'], meas['rssi'], meas['rssiAve'], laneCounter)
    my_print(text=txt_csv, sink={'serial':True,'lcd':True,'dataLog':True})
    print_lcd_dbg(meas=meas, laneCounter=laneCounter)   


# calculate an average of the last 2 measurements
# possible issue here: out of range is taking about 3 seconds whereas range measurements happen every 1 or two seconds. So, OOR should have more weight
def moving_average(rssiVals:list, meas:dict):
    rssiVals.append(meas['rssi'])
    rssiVals.pop(0)
    meas['rssiAve'] = sum(rssiVals) / 2
    return


def fill_history(rssiHistory:list, newVal:int):
    rssiHistory.append(newVal)
    if (len(rssiHistory) > NUM_OF_RSSIS): # TODO: use abs_time instead of num of measurements
        rssiHistory.pop(0) # remove the oldest one
    return


"""
lane counting conditions which have to be fullfilled:
a: rssi goes down. b: beacon low (or out of range) c: rssi goes up
-> whole sequence takes from 30 seconds to 2 minutes (normal 1 min per 50meter)
beacon out-of-range measurements take 2 seconds while others take about 0.3 seconds
"""
def lane_decision(rssiHistory:list, laneCounter:int):
    DBM_DIFF = const(10)
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
    if laneCounter > 9: # draw it only when there really are two digits
        draw_digit(digit=floor(laneCounter / 10), posLsb=False)
    draw_digit(digit=(laneCounter % 10), posLsb=True)
    LCD.show_up()
    return


def draw_digit(digit:int, posLsb:bool):
    if digit > 9 or digit < 0:
        return
    #          a,b,c,d,e,f,g 
    arrSeg = [[1,1,1,1,1,1,0], # arrSeg[0] displays 0
              [0,1,1,0,0,0,0], # 1
              [1,1,0,1,1,0,1], # 2
              [1,1,1,1,0,0,1], # 3
              [0,1,1,0,0,1,1], # 4
              [1,0,1,1,0,1,1], # 5
              [1,0,1,1,1,1,1], # 6
              [1,1,1,0,0,0,0], # 7
              [1,1,1,1,1,1,1], # 8
              [1,1,1,1,0,1,1]] # 9
    segments = arrSeg[digit]
    
    # box size (for two digits) is about 190 x 160
    # one segment is 56x8, spacing is 5, thus resulting in 61x12 per segment+space
    # x-direction: between digits another 20px is reserved, thus 12+56+12 +20+ 12+56+12 = 180    
    x = 130 # start point x
    Y = const(80)
    SPC_BIG = const(61) # 56+5
    SPC_SML = const(12) # 8+4

    if posLsb:
        x = x + 2*(SPC_SML) + SPC_BIG + 20
  
    if segments[0]: draw_segment(x=x+SPC_SML,         y=Y,                     horiz=True)  # a-segment
    if segments[1]: draw_segment(x=x+SPC_BIG+SPC_SML, y=Y+SPC_SML,             horiz=False) # b-segment
    if segments[2]: draw_segment(x=x+SPC_BIG+SPC_SML, y=Y+2*SPC_SML+SPC_BIG,   horiz=False) # c-segment
    if segments[3]: draw_segment(x=x+SPC_SML,         y=Y+2*(SPC_SML+SPC_BIG), horiz=True)  # d-segment
    if segments[4]: draw_segment(x=x,                 y=Y+2*SPC_SML+SPC_BIG,   horiz=False) # e-segment
    if segments[5]: draw_segment(x=x,                 y=Y+SPC_SML,             horiz=False) # f-segment
    if segments[6]: draw_segment(x=x+SPC_SML,         y=Y+SPC_SML+SPC_BIG,     horiz=True)  # g-segment
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


def load_background():
    LCD.bl_ctrl(100)
    LCD.fill(LCD.BLACK)
    LCD.show_up() # the code below takes some time, have it black from start onwards
    
    BG_IMAGE_SIZE_BYTE = const(60*320*2) # I don't load the full image, it's too big/slow. Only part of it and the rest is constant color
    with open ('background.bin', "rb") as file:
        position = 0
        while position < BG_IMAGE_SIZE_BYTE: # two bites per pixel are read
            b0 = int.from_bytes(file.read(2), 'big')
            LCD.buffer[position] = b0 % 256 # b0 & 0xFF # not sure whether this really works. Maybe use b0 % 256
            LCD.buffer[position+1] = floor(b0 / 256) # does not work: b0 & 0xFF00 
            position += 2
            
            # should be the same (maybe swap b0 and b1). If this works, then I can just do the while loop normally, with one var and position += 1.
            """
            b0 = int.from_bytes(file.read(1), 'big')
            b1 = int.from_bytes(file.read(1), 'big')
            LCD.buffer[position] = b0
            LCD.buffer[position+1] = b1
            position += 2            
            """

            # some other small optimization (don't need to copy black values)
            """
            b0 = int.from_bytes(file.read(2), 'big')
            if b0 > 0:
                LCD.buffer[position] = b0 % 256 # b0 & 0xFF # not sure whether this really works. Maybe use b0 % 256
                LCD.buffer[position+1] = floor(b0 / 256) # does not work: b0 & 0xFF00 
            position += 2            
            """

            # alternative solution I found
            """
            # bytearray is as its stored in the file. However, this looks like it stores the whole thing in RAM, wouldn't work
            fb_smile1 = framebuf.FrameBuffer(bytearray(b'\x00~\x00\x03\xff\xc0\x07\x81\xe0\x1e\x00x8\x00\x1c0\x00\x0c`\x00\x0ea\xc3\x86\xe0\x00\x07\xc0\x00\x03\xc0\x00\x03\xc0\x00\x02\xc0\x00\x03\xc0\x00\x03\xe0B\x07`<\x06`\x00\x060\x00\x0c8\x00\x1c\x1e\x00x\x07\x81\xe0\x03\xff\xc0\x00\xff\x00'), 24, 23, framebuf.MONO_HLSB)
            LCD.framebuf.blit(fb_smile1, 0, 20)
            LCD.show_ip()
            """

            # using a struct to get from bytestream to int array

    file.close()
    LCD.show_up()   


# main program
async def main():
    load_background()
    
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
