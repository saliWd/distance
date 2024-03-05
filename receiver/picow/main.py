##
# using aioble library (https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble)
##
# external libraries: do once (or tools -> manage packages -> install (uasyncio is already part of micropython))
# import mip
# mip.install("aioble")

from time import sleep, ticks_ms, ticks_diff
from machine import Pin,SPI,PWM #type: ignore

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)
from random import randint

import framebuf # type: ignore
import time
import os

LCD_DC   = 8
LCD_CS   = 9
LCD_SCK  = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL   = 13
LCD_RST  = 15
TP_CS    = 16
TP_IRQ   = 17


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

class LCD_disp(framebuf.FrameBuffer):

    def __init__(self):
        self.RED   =   0x07E0
        self.GREEN =   0x001f
        self.BLUE  =   0xf800
        self.WHITE =   0xffff
        self.BLACK =   0x0000
        
        self.width = 320
        self.height = 240
            
        self.cs = Pin(LCD_CS,Pin.OUT)
        self.rst = Pin(LCD_RST,Pin.OUT)
        self.dc = Pin(LCD_DC,Pin.OUT)
        
        self.tp_cs =Pin(TP_CS,Pin.OUT)
        self.irq = Pin(TP_IRQ,Pin.IN)
        
        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
              
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        #self.spi.write(bytearray([0X00]))
        self.spi.write(bytearray([buf]))
        self.cs(1)


    def init_display(self):
        """Initialize dispaly"""  
        self.rst(1)
        time.sleep_ms(5)
        self.rst(0)
        time.sleep_ms(10)
        self.rst(1)
        time.sleep_ms(5)
        
        self.write_cmd(0x11)
        time.sleep_ms(100)
        
        self.write_cmd(0x36)
        self.write_data(0x60)
        
        self.write_cmd(0x3a)
        self.write_data(0x55)
        self.write_cmd(0xb2)
        self.write_data(0x0c)
        self.write_data(0x0c)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)
        self.write_cmd(0xb7)
        self.write_data(0x35)
        self.write_cmd(0xbb)
        self.write_data(0x28)
        self.write_cmd(0xc0)
        self.write_data(0x3c)
        self.write_cmd(0xc2)
        self.write_data(0x01)
        self.write_cmd(0xc3)
        self.write_data(0x0b)
        self.write_cmd(0xc4)
        self.write_data(0x20)
        self.write_cmd(0xc6)
        self.write_data(0x0f)
        self.write_cmd(0xD0)
        self.write_data(0xa4)
        self.write_data(0xa1)
        self.write_cmd(0xe0)
        self.write_data(0xd0)
        self.write_data(0x01)
        self.write_data(0x08)
        self.write_data(0x0f)
        self.write_data(0x11)
        self.write_data(0x2a)
        self.write_data(0x36)
        self.write_data(0x55)
        self.write_data(0x44)
        self.write_data(0x3a)
        self.write_data(0x0b)
        self.write_data(0x06)
        self.write_data(0x11)
        self.write_data(0x20)
        self.write_cmd(0xe1)
        self.write_data(0xd0)
        self.write_data(0x02)
        self.write_data(0x07)
        self.write_data(0x0a)
        self.write_data(0x0b)
        self.write_data(0x18)
        self.write_data(0x34)
        self.write_data(0x43)
        self.write_data(0x4a)
        self.write_data(0x2b)
        self.write_data(0x1b)
        self.write_data(0x1c)
        self.write_data(0x22)
        self.write_data(0x1f)
        self.write_cmd(0x55)
        self.write_data(0xB0)
        self.write_cmd(0x29)

    def show_up(self):

        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x3f)
         
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xef)
                
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
        
    def bl_ctrl(self,duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty>=100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)

    def touch_get(self): 
        if self.irq() == 0:
            self.spi = SPI(1,5_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0,3):
                self.spi.write(bytearray([0XD0]))
                Read_date = self.spi.read(2)
                time.sleep_us(10)
                X_Point=X_Point+(((Read_date[0]<<8)+Read_date[1])>>3)
                
                self.spi.write(bytearray([0X90]))
                Read_date = self.spi.read(2)
                Y_Point=Y_Point+(((Read_date[0]<<8)+Read_date[1])>>3)

            X_Point=X_Point/3
            Y_Point=Y_Point/3
            
            self.tp_cs(1) 
            self.spi = SPI(1,30_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            Result_list = [X_Point,Y_Point]
            #print(Result_list)
            return(Result_list)


async def find_beacon():
    # Scan for 3 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(3000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == 'widmedia.ch':
                    return result
    return None

def my_print(LCD, text:str, end:str="\n"):
    # TODO: display more than one line
    LCD.fill(LCD.BLACK)
    LCD.text(text[0:len(text)-1],2,17,LCD.WHITE) # last character is a newline, LCD.text can't handle that
    LCD.show_up()
    print(text, end=end)


def print_infos(LCD, filehandle, meas:dict):
    shortAddr = meas['addr']
    shortAddr = shortAddr[len(shortAddr)-5:len(shortAddr)]
    txt_csv = "%d, %d, %s, %d, %d\n" % (meas['loopCnt'], meas['timeDiff'], shortAddr, meas['rssi'], meas['rssiAve'])
    my_print(LCD=LCD, text=txt_csv, end ='') # need the newline for the csv write. No additional new line here
    filehandle.write(txt_csv)
    filehandle.flush()

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
def checkCriterias(LCD, laneInfos:list, laneCriterias:dict, loopCnt:int, meas:dict, oldMeas:dict):
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
        my_print(LCD=LCD, text="\n\n*** laneCounter + 1, laneTime: %d ***\n" % (laneTime))
        laneInfos.append(laneTime)
    # else just return
    
    # if someThingChanged:
    #     my_print(LCD=LCD, text="something changed at categorization. Comparing %d and %d" % (meas['rssiAve'], oldMeas['rssiAve']))
    #     my_print(LCD=LCD, text=laneCriterias)
    
    return (laneInfos, laneCriterias, meas.copy())


# main program
async def main():
    LCD = LCD_disp()
    LCD.bl_ctrl(100)
    LCD.fill(LCD.BLACK)
    LCD.show_up()

    loopMax = 20000

    filehandle = open('data.csv', 'a') # append
    txt_csv = "id, time_ms, address, rssi, average\n"
    my_print(LCD=LCD, text=txt_csv, end ='')
    filehandle.write(txt_csv)
    filehandle.flush()

    LCD.text("Schwimm-Messer",90,17,LCD.WHITE)
    LCD.show_up()

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
    
    while loopCnt < loopMax:
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
        print_infos(LCD=LCD, filehandle=filehandle, meas=meas)
        
        ledOnboard.toggle()
        (laneInfos, laneCriterias, oldMeas) = checkCriterias(LCD=LCD, laneInfos=laneInfos, laneCriterias=laneCriterias, loopCnt=loopCnt, meas=meas, oldMeas=oldMeas)
        sleep(LOOP_SLEEP_TIME)
 
    filehandle.close()
    my_print(LCD=LCD, text="\n********\n* done *\n********")
    
    if len(laneInfos) > 0:
        my_print(LCD=LCD, text='time per lane: ')
        my_print(LCD=LCD, text=laneInfos)
    else:
        my_print(LCD=LCD, text=laneCriterias)

asyncio.run(main())
