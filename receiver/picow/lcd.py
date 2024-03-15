###
# LCD driver from waveshare, slightly adapted
### 

from machine import Pin,SPI,PWM #type: ignore

import framebuf # type: ignore (this is a micropython internal module)
from time import sleep_ms, sleep_us

LCD_SCK  = 10 # used in init and in touch sensor
LCD_MOSI = 11
LCD_MISO = 12

"""
screen layout (approximative)
                                  320                                     
    _____________________240__________________________________80____________
    |                                                                        |
 40 |                         -LOGO-                                         |   40
    |                                                                        |
 20 |   csv header                                         00        1111    |
    |                                                     0  0      11 11    |
    |   -------------------------------------------      0    0    11  11    |
    |   |  csv text-box                           |      0    0        11    |        240
    |   |                                         |      0    0        11    |
160 |   |                                         |      0    0 lane   11    |  200
    |   |                                         |      0    0        11    |
    |   |                                         |      0    0        11    |
    |   -------------------------------------------       0  0         11    | 
 20 |                                                      00          11    |
    _________________________________________________________________________

"""

class LCD_disp(framebuf.FrameBuffer):

    def __init__(self):
        self.RED   =   0x07E0
        self.GREEN =   0x001f
        self.BLUE  =   0xf800
        self.WHITE =   0xffff
        self.BLACK =   0x0000
        
        self.width = 320
        self.height = 240
            
        self.cs = Pin(9,Pin.OUT)
        self.rst = Pin(15,Pin.OUT)
        self.dc = Pin(8,Pin.OUT)
        
        self.tp_cs =Pin(16,Pin.OUT)
        self.irq = Pin(17,Pin.IN)
        
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
        self.spi.write(bytearray([buf]))
        self.cs(1)


    def init_display(self):
        # Initialize display
        self.rst(1)
        sleep_ms(5)
        self.rst(0)
        sleep_ms(10)
        self.rst(1)
        sleep_ms(5)
        
        self.write_cmd(0x11)
        sleep_ms(100)
        
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
        pwm = PWM(Pin(13))
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
                sleep_us(10)
                X_Point=X_Point+(((Read_date[0]<<8)+Read_date[1])>>3)
                
                self.spi.write(bytearray([0X90]))
                Read_date = self.spi.read(2)
                Y_Point=Y_Point+(((Read_date[0]<<8)+Read_date[1])>>3)

            X_Point=X_Point/3
            Y_Point=Y_Point/3
            
            self.tp_cs(1) 
            self.spi = SPI(1,30_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            Result_list = [X_Point,Y_Point]
            return(Result_list)
