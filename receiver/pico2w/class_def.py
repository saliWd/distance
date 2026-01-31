# 
from pimoroni import RGBLED  # type: ignore (included in uf2 file)
from time import sleep_ms

class RgbLed(object):
    def __init__(self):
        self.led_rgb = RGBLED(26, 27, 28)
        self.color = (0,0,0)
        self.led_rgb.set_rgb(*(self.color))

    def toggle(self): # toggles between green and red
        if self.color == (255,0,0): # red
            self.color = (0,255,0) # green
        else:
            self.color = (255,0,0)
        

class BEACON_SIM():
    def __init__(self,CONFIG:dict):
        self.device = '012345678901234567890123456789__%s' % CONFIG['mac_addr_short'] # only the last 5 characters matter
        self.rssi = -27 # some non-meaningful value
        self.f = open('simInput.csv', 'r')
        self.sim_speedup = CONFIG['sim_speedup']
        self.diffTime = 327
    
    def get_sim_val(self):
        line = self.f.readline()
        if not line or len(line) < 5: # to detect an empty line at the end
            quit() # quit or exit() do not work in micropython. But it throws an error and thus stops, so it still does the job
        val = line.split(',')
        if not self.sim_speedup:
            sleep_ms(int(val[0]))
        self.rssi = int(val[1])
        self.diffTime = int(val[0])
        return self
