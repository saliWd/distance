from time import sleep
from random import randint

class BEACON_SIM():
    def __init__(self):
        self.device = '012345678901234567890123456789__01:23'
        self.rssi = -27

    def get_sim_val(self, usePredefined:bool, loopCnt:int):
        SIMULATE_TIME_SHORT = 0.1 # 0.2 is comparable to normal mode
        SIMULATE_TIME_LONG  = 0.0 # 2.8 is comparable to normal mode
        sleep(SIMULATE_TIME_SHORT)
        if usePredefined:
            SIM_VALS = [-80, -80, -80, -80, -80, -80, -80, -80, -80, -80,
                        -90, -90, -90, -90, -90, -90, -90, -90, -90, -90,
                        -120,-120,-120,-120,-120,-120,-120,-120,-120,-120,
                        -90, -90, -90, -90, -90, -90, -90, -90, -90, -90,
                        -80, -80, -80, -80, -80, -80, -80, -80, -80, -80]
            self.rssi = SIM_VALS[(loopCnt-1) % len(SIM_VALS)]
            return self
        else:
            randNum = randint(0,1)
            if randNum == 0:
                sleep(SIMULATE_TIME_LONG) # simulating time out
                return None
            else:
                self.rssi = randint(-100,-80)
                return self
