##
# functions used in different files 
# 
# using aioble library (https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble)
# external libraries: do once (or tools -> manage packages -> install (uasyncio is already part of micropython))
# import mip
# mip.install("aioble")

import array
from micropython import const #type: ignore

import aioble # type: ignore (this is a pylance ignore warning directive)

# files on file system
from lcd import LCD_disp # import the display class

import my_config
CONFIG = my_config.get_config() # which device address do I look for and debug stuff like beacon simulation variables

# LCD calls the framebuf module, see https://docs.micropython.org/en/latest/library/framebuf.html
LCD = LCD_disp() # 240px high, 320px wide, see https://www.waveshare.com/wiki/Pico-ResTouch-LCD-2.8

async def find_beacon():
    # async with aioble.scan(duration_ms=5000) as scanner: # scan for 5s in passive mode. NB: active mode may generete memAlloc issues
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner: # Scan for 5 seconds, in active mode, with very low interval/window (to maximise detection rate).
        async for result in scanner:
            if result.name() and result.name()[0:11] == CONFIG['beacon_name']: # most are empty...
                addr = "%s" % result.device # need to get string representation first
                if addr[32:37] == CONFIG['mac_addr_short']: # last 5 characters of MAC_ADDR
                    return result
    return None

def load_background():
    LCD.bl_ctrl(100)
    LCD.fill(LCD.BLACK)
    LCD.show_up() # the code below takes some time, have it black from start onwards
    
    BG_IMAGE_SIZE_BYTE = const(60*320*2) # I don't load the full image, it's too big/slow. Only part of it and the rest is constant color
    BUF_SIZE = const(256) # make sure the image size and the buffer size are nicely arranged
    with open ('background.bin', "rb") as file:
        for bufPos in range(0, BG_IMAGE_SIZE_BYTE, BUF_SIZE):
            buffer = array.array('b', file.read(BUF_SIZE)) # file read command itself is taking long
            for arrPos in range(0, BUF_SIZE):
                LCD.buffer[bufPos+arrPos] = buffer[arrPos]
    file.close()
    LCD.show_up()
