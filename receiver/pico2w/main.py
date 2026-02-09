## see ProjectNotes.md about external dependencies
from gc import collect
from time import ticks_diff, ticks_ms
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB565  # type: ignore
from picovector import PicoVector, ANTIALIAS_X16, Polygon # type: ignore
from pngdec import PNG # type: ignore
from micropython import const # type: ignore
import uasyncio as asyncio # type: ignore
import aioble # type: ignore
# my own definitions
from class_def import RgbLed, BEACON_SIM
from my_config import get_config

CONFIG = get_config() # which device address do I look for and debug stuff like beacon simulation variables
beaconSim = BEACON_SIM(CONFIG)

RSSI_OOR = const(-120) # What value do I give to out-of-range beacons?

# lane decision constants
MIN_DIFF     = const(5)     # [dBm*sec]-based
RSSI_LOW     = const(-100)  # [dBm*sec]-based
RANGE_WIDTH  = const(7000)  # [ms] length of one range
MAX_NUM_HIST = const(35)    # [num of entries] corresponds to 240 seconds, max duration for a 50m lane

## global variables
f_dataLog = open('logData.csv', 'a') # append
LOOP_MAX = const(20000) # 20k corresponds to at least 2.2h (with 0.4 secs per meas)

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, rotate=0, pen_type=PEN_RGB565)
display.set_backlight(0.8)
display.set_font('bitmap8') # for the non-fancy text output during startup

vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_X16)
vector.set_font('font.af', 28)

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)


def print_lcd_dbg(meas:list, laneCounter:int):
    X_TEXT = const(10)
    X_NUM = const(160)
    Y_0 = const(80)
    LINE = const(20)
    display.set_pen(BLACK)
    display.rectangle(X_TEXT, Y_0-LINE, 284, 6*LINE) # clear the area
    display.set_pen(WHITE)

    vector.text('Loop:',X_TEXT,Y_0,0)
    vector.text('T_abs:',X_TEXT,Y_0+LINE,0)
    vector.text('T_diff:',X_TEXT,Y_0+2*LINE,0)
    vector.text('Address:',X_TEXT,Y_0+3*LINE,0)
    vector.text('RSSI:',X_TEXT,Y_0+4*LINE,0)
    vector.text('Lane:',X_TEXT,Y_0+5*LINE,0)
    
    xa, ya, w_0, ha = vector.measure_text("%4d" % meas[0], x=X_NUM, y=Y_0, angle=None)
    xa, ya, w_1, ha = vector.measure_text("%6d" % int(meas[1] / 1000), x=X_NUM, y=Y_0, angle=None)
    xa, ya, w_2, ha = vector.measure_text("%5d" % meas[2], x=X_NUM, y=Y_0, angle=None)
    xa, ya, w_3, ha = vector.measure_text("%s"  % meas[3], x=X_NUM, y=Y_0, angle=None)
    xa, ya, w_4, ha = vector.measure_text("%4d" % meas[4], x=X_NUM, y=Y_0, angle=None)
    xa, ya, w_5, ha = vector.measure_text("%4d" % laneCounter, x=X_NUM, y=Y_0, angle=None)

    vector.text("%4d" % meas[0],int(X_NUM-w_0),Y_0,0)
    vector.text("%6d" % int(meas[1] / 1000),int(X_NUM-w_1),Y_0+LINE,0)
    vector.text("%5d" % meas[2],int(X_NUM-w_2),Y_0+2*LINE,0)
    vector.text("%s"  % meas[3],int(X_NUM-w_3),Y_0+3*LINE,0)
    vector.text("%4d" % meas[4],int(X_NUM-w_4),Y_0+4*LINE,0)
    vector.text("%4d" % laneCounter,int(X_NUM-w_5),Y_0+5*LINE,0)
    
    display.update()

def print_infos(meas:list, laneCounter:int):
    txt_csv = "%5d, %6d, %5d, %s, %4d, %4d\n" % (meas[0],int(meas[1] / 1000),meas[2],meas[3],meas[4],laneCounter)
    f_dataLog.write(txt_csv)
    f_dataLog.flush()
    print(txt_csv, end='')
    print_lcd_dbg(meas=meas, laneCounter=laneCounter)

def fill_some_sec(someSecRssi:list, someSecTime:list, histRssi:list, rssi:int, timeDiff:int):
    someSecRssi.append(rssi) # example: -90 (range -60 to -120)
    someSecTime.append(timeDiff) # example: 400 (range 300 to 5300)
    
    if (sum(someSecTime) > RANGE_WIDTH): # oldest entry is older than some secs
        histRssi.append(int(sum(someSecRssi) / RANGE_WIDTH)) # rssi-dbms * seconds 
        someSecRssi.clear()
        someSecTime.clear()        
        if (len(histRssi) > MAX_NUM_HIST):
            histRssi.pop(0) # remove the oldest one
        return True
    else:
        return False

"""
lane counting conditions which have to be fullfilled:
a: rssi goes down. b: beacon low (or out of range) c: rssi goes up
-> whole sequence takes from 30 seconds to 2 minutes (normal 1 min per 50meter)
beacon out-of-range measurements take several seconds while others take about 0.3 seconds
"""
def lane_decision(histRssi:list, laneConditions:list, laneCounter:int):
    arrLen = len(histRssi)
    if arrLen < 3: # need at least some ranges to decide
        return False

    condition = 0
    
    for i in range(arrLen-2): # I have enough ranges. Start a search for the 'right conditions'. NB: range is -2, because I check with i+1
        if not laneConditions[0]:
            condition = 0
            conditionMet = down_up_check(a=histRssi[i], b=histRssi[i+1], down=True)
        elif not laneConditions[1]:
            condition = 1
            conditionMet = (histRssi[i] < RSSI_LOW)
        elif not laneConditions[2]:
            condition = 2
            conditionMet = down_up_check(a=histRssi[i], b=histRssi[i+1], down=False)
        else:
            print("Error. All conditions already fulfilled. i=%d. arrLen=%d" % (i, arrLen))

        if conditionMet:
            laneConditions[condition] = True
            # print("condition %d is fullfilled. i=%d. arrLen=%d" % (condition, i, arrLen))            
            histRssi.pop(0) # remove the oldest, so it does not trigger again for this condition
            break # break the for loop
        else:
            if i == (arrLen-3): # condition was not fulfilled in the whole for-i loop
                return False

    if laneConditions[0] and laneConditions[1] and laneConditions[2]:
        update_lane_disp(laneCounter+1)
        # print(histRssi)
        histRssi.clear() # empty the list. Don't want to increase the lane counter on the next value again
        # NB: lists are given as a reference, can clear it here
        return True
    
    return False

def down_up_check(a, b, down:bool):
    if down:
        return (a - MIN_DIFF) > b
    else:
        return (a + MIN_DIFF) < b


def update_lane_disp(laneCounter:int):
    display.set_pen(BLACK)
    display.rectangle(130,80,190,160) # clear the area
    display.set_pen(WHITE)

    if laneCounter > 99:
        return
    if laneCounter > 9: # draw it only when there really are two digits
        draw_digit(digit=int(laneCounter / 10), posLsb=False)
    draw_digit(digit=(laneCounter % 10), posLsb=True)
    display.update()
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
        coord = [(0,4), (4,0), (52,0), (56,4), (52,8), (4,8)] # unsigned integers array
    else: # vertical
        if (x+8 > 319) or (y+56 > 239):
            print("coord error: x=%d, y=%d, horiz=%s" % (x, y, horiz))
            return
        coord = [(4,0), (0,4), (0,52), (4,56), (8,52), (8,4)]
    segment = Polygon()
    segment.path(*coord)
    display.update()
    return # NB: no lcd.show_up as this is called after all segments are drawn

async def find_beacon():
    # async with aioble.scan(duration_ms=5000) as scanner: # scan for 5s in passive mode. NB: active mode may generete memAlloc issues
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner: # Scan for 5 seconds, in active mode, with very low interval/window (to maximise detection rate).
        async for result in scanner:
            if result.name() and result.name()[0:8] == 'widmedia': # name of the beacon: # most are empty...
                addr = "%s" % result.device # need to get string representation first
                if addr[32:37] == CONFIG['mac_addr_short']: # last 5 characters of MAC_ADDR
                    return result
    return None

# main program
async def main():
    # fills the screen
    png = PNG(display)
    png.open_file('background.png')
    png.decode(0, 0)
    display.update()

    
    startTime = ticks_ms() # time 0 for the absolute time measurement

    loopCnt = 0
    rgb_led = RgbLed()
    rgb_led.toggle()
    laneCounter = 0
    update_lane_disp(laneCounter)
    
    txt_csv = "   id,  t_abs,t_diff,  addr, rssi,  lane\n"
    f_dataLog.write(txt_csv)
    print(txt_csv, end='')

    # NB: be aware of list of lists, might get memAlloc issues
    histRssi = list()     

    someSecRssi:list[int] = list()
    someSecTime:list[int] = list()
    laneConditions:list[bool] = [False, False, False] # down, below, up
    
    
    while loopCnt < LOOP_MAX:
        now = ticks_ms()
        if CONFIG['simulate_beacon']:
            result = beaconSim.get_sim_val()
        else:
            result = await find_beacon()
        bleTimeDiff = ticks_diff(ticks_ms(), now)
        meas = [
            loopCnt, # 0: a counter
            0,       # 1: timeAbs in milliseconds
            0,       # 2: timeDiff in milliseconds
            'xx:xx', # 3: addr, a string
            RSSI_OOR # 4: rssi in dBm
        ]
        if result:
            addr = "%s" % result.device # need to get string representation first
            meas[3] = addr[32:37] # only take the MAC part, the last 5 characters
            meas[4] = result.rssi

        
        if CONFIG['simulate_beacon'] and CONFIG['sim_speedup']:
            meas[2] = result.diffTime
            meas[1] = 27000 # absolute time. Not really nice like this but doesn't matter
        else:
            meas[2] = bleTimeDiff
            meas[1] = ticks_diff(now, startTime) # absolute time, does not really matter whether it's taken before the BLE meas or not
        
        didCompact = fill_some_sec(someSecRssi=someSecRssi, someSecTime=someSecTime, histRssi=histRssi, rssi=(meas[4]*meas[2]), timeDiff=meas[2])
        if didCompact:
            if lane_decision(histRssi=histRssi, laneConditions=laneConditions, laneCounter=laneCounter):
                laneCounter += 1
                laneConditions = [False, False, False]
        print_infos(meas=meas, laneCounter=laneCounter)
        
        del meas, result, now, bleTimeDiff, didCompact # to combat memAlloc issues
        rgb_led.toggle()
        loopCnt += 1
        collect() # garbage collection
        # loop time is about 300 ms or 800 ms, with some outliers at 1300 ms. OOR measurements however take longer (timeout)
 
    f_dataLog.close()

asyncio.run(main())

