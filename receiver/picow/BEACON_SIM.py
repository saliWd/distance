from time import sleep_ms
from random import randint

class BEACON_SIM():
    def __init__(self,REAL_LIFE_SPEED:bool):
        self.device = '012345678901234567890123456789__01:23' # only the last 5 characters matter
        self.rssi = -27 # some non-meaningful values        
        self.f = open('simInput.csv', 'r')
        self.REAL_LIFE_SPEED = REAL_LIFE_SPEED
    
    def get_sim_val(self, mode:str, loopCnt:int):
        if mode == 'predefined':
            if self.REAL_LIFE_SPEED:sleep_ms(100) # 200 is comparable to normal mode
            SIM_VALS = [-80,-80,-80,-80,-80,-80,-80,-80,-80,-80,
                        -90,-90,-90,-90,-90,-90,-90,-90,-90,-90,
                        -120,-120,-120,-120,-120,-120,-120,-120,-120,-120,
                        -90,-90,-90,-90,-90,-90,-90,-90,-90,-90,
                        -80,-80,-80,-80,-80,-80,-80,-80,-80,-80]
            self.rssi = SIM_VALS[(loopCnt-1) % len(SIM_VALS)]
            return self
        elif mode == 'random':            
            randNum = randint(0,1)
            if randNum == 0:
                if self.REAL_LIFE_SPEED:sleep_ms(2800) # 2800 is comparable (simulating time-out)
                return None
            else:
                self.rssi = randint(-100,-80)
                return self
        elif mode == 'fieldTest':
            line = self.f.readline()
            if not line or len(line) < 5: # to detect an empty line at the end
                self.rssi = -27
                return self
            val = line.split(',')
            if int(val[0]) > 200: # minus 200 because the normal loop sleep time is 0.2 sec
                if self.REAL_LIFE_SPEED:sleep_ms(int(val[0])-200) 
            self.rssi = int(val[1])
            return self
        else: # should never happen
            return None