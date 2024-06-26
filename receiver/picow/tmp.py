import array
from math import floor
from micropython import const #type: ignore

# files on file system
from lcd import LCD_disp # import the display class

RSSI_OOR = const(-120) # What value do I give to out-of-range beacons?

## global variables
# LCD calls the framebuf module, see https://docs.micropython.org/en/latest/library/framebuf.html
LCD = LCD_disp() # 240px high, 320px wide, see https://www.waveshare.com/wiki/Pico-ResTouch-LCD-2.8

def print_lcd_dbg(meas:dict, laneCounter:int):
    X = const(10)
    y = 80
    LINE = const(15)
    LCD.fill_rect(X,y,114,6*LINE,LCD.BLACK) # clear the area
    
    LCD.text("Loop:     %4d" % meas['loopCnt'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("Timediff: %4d" % meas['timeDiff'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("Address: %s"  % meas['addr'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("RSSI:     %4d" % meas['rssi'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("RSSI ave: %4d" % meas['rssiAve'],X,y,LCD.WHITE)
    y += LINE
    LCD.text("Lane:     %4d" % laneCounter,X,y,LCD.WHITE)
    LCD.show_up()


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
    BUF_SIZE = const(256) # make sure the image size and the buffer size are nicely arranged
    with open ('background.bin', "rb") as file:
        for bufPos in range(0, BG_IMAGE_SIZE_BYTE, BUF_SIZE):
            buffer = array.array('b', file.read(BUF_SIZE)) # file read command itself is taking long
            for arrPos in range(0, BUF_SIZE):
                LCD.buffer[bufPos+arrPos]   = buffer[arrPos]            
    
    file.close()
    LCD.show_up()

# main program
load_background()
update_lane_disp(78)

meas = {
    'loopCnt':27, # a counter
    'timeDiff':227,      # in milliseconds
    'addr':'xx:xx',    # string
    'rssi':RSSI_OOR,   # in dBm
    'rssiAve':-27      # in dBm
}
            
print_lcd_dbg(meas=meas, laneCounter=0)
      
# rectangle around dbg output      
coord = array.array('I', [0,0, 114,0, 114,90, 0,90])
LCD.poly(8, 76, coord, LCD.WHITE, False)
LCD.show_up()

# 0xa554 grey 
# 0xce99 bright grey

coord = array.array('I', [0,0, 116,0, 116,92, 0,92])
LCD.poly(7, 75, coord, 0xa554, False)
LCD.show_up()

coord = array.array('I', [0,0, 118,0, 118,94, 0,94])
LCD.poly(6, 74, coord, 0xce99, False)
LCD.show_up()

