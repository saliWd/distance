##
# using aioble library (https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble)
##
# external libraries: do once (or tools -> manage packages -> install (uasyncio is already part of micropython))
# import mip
# mip.install("aioble")

import gc

class BEACON_SIM():
    def __init__(self):
        self.device = '012345678901234567890123456789__65:02'
        self.rssi = -27 # some non-meaningful value
        self.f = open('simInput.csv', 'r')
        self.diffTime = 327
    
    def get_sim_val(self):
        line = self.f.readline()
        if not line or len(line) < 5: # to detect an empty line at the end
            quit() # quit or exit() do not work in micropython. But it throws an error and thus stops, so it still does the job
        val = line.split(',')
        self.rssi = int(val[1])
        self.diffTime = int(val[0])
        return self

beaconSim = BEACON_SIM()

RSSI_OOR = (-600) # What value do I give to out-of-range beacons?

# lane decision constants
MIN_DIFF     = (35)     # [dBm/sec]
RSSI_LOW     = (-90)   # [dBm/sec]
RANGE_WIDTH  = (10000) # [ms] one range is 12 seconds long
MAX_NUM_HIST = (20)    # [num of entries] corresponds to 240 seconds, max duration for a 50m lane

## global variables
f_dataLog = open('logDataLocal.csv', 'w') # append
LOOP_MAX = (20000) # 20k corresponds to at least 2.2h (with 0.4 secs per meas)

def print_infos(meas:list, laneCounter:int):
    txt_csv = "%5d, %6d, %5d, %s, %4d, %4d\n" % (meas[0],int(meas[1] / 1000),meas[2],meas[3],meas[4],laneCounter)
    f_dataLog.write(txt_csv)
    f_dataLog.flush()
    print(txt_csv, end='')

def fill_some_sec(someSecRssi:list, someSecTime:list, histRssi:list, rssi:int, timeDiff:int):
    someSecRssi.append(rssi)
    someSecTime.append(timeDiff)

    timeSum = sum(someSecTime)
    if (timeSum > RANGE_WIDTH): # oldest entry is older than some secs
        rssiSum = sum(someSecRssi) * 1000 # because time is in ms
        average = rssiSum / timeSum # rssi-dbms per second
        someSecRssi.clear()
        someSecTime.clear()
        histRssi.append(average)
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
    
    for i in range((arrLen-2)): # I have enough ranges. Start a search for the 'right conditions'
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
            print("Error. All conditions already fullfilled. i=%d. arrLen=%d" % (i, arrLen))


        if conditionMet:
            laneConditions[condition] = True
            print("condition %d is fullfilled. i=%d. arrLen=%d" % (condition, i, arrLen)) # TODO            
            histRssi.pop(0) # remove the oldest, so it does not trigger again for this condition
            break # break the for loop
        else:
            if i == (arrLen-3): # condition was not fulfilled in the whole for-i loop
                return False

    if laneConditions[0] and laneConditions[1] and laneConditions[2]:
        # print(histRssi) # TODO
        histRssi.clear() # empty the list. Don't want to increase the lane counter on the next value again. TODO: do I really need to do that?       
        # NB: lists are given as a reference, can clear it here
        return True
    
    return False

def down_up_check(a, b, down:bool):
    if down:
        return (a - MIN_DIFF) > b
    else:
        return (a + MIN_DIFF) < b


# main program
def main():
    loopCnt = 0    
    laneCounter = 0
    
    txt_csv = "   id,  t_abs,t_diff,  addr, rssi,  lane\n"
    f_dataLog.write(txt_csv)
    print(txt_csv, end='')

    # NB: be aware of list of lists, might get memAlloc issues
    histRssi = list()     

    someSecRssi:list[int] = list()
    someSecTime:list[int] = list()    
    laneConditions:list[bool] = [False, False, False] # down, below, up
    
    
    while loopCnt < LOOP_MAX:
        result = beaconSim.get_sim_val()
        meas = [
            loopCnt, # 0: a counter
            0,       # 1: timeAbs in milliseconds
            0,       # 2: timeDiff in milliseconds
            'xx:xx', # 3: addr, a string
            RSSI_OOR # 4: rssi in dBm
        ]
        addr = "%s" % result.device # need to get string representation first
        meas[3] = addr[32:37] # only take the MAC part, the last 5 characters
        meas[4] = result.rssi
        meas[2] = result.diffTime
        meas[1] = 27000 # absolute time. Not really nice like this but doesn't matter
        
        
        didCompact = fill_some_sec(someSecRssi=someSecRssi, someSecTime=someSecTime, histRssi=histRssi, rssi=meas[4], timeDiff=meas[2])
        if didCompact:
            if lane_decision(histRssi=histRssi, laneConditions=laneConditions, laneCounter=laneCounter):
                laneCounter += 1
                laneConditions = [False, False, False]
        print_infos(meas=meas, laneCounter=laneCounter)
        
        del meas, result, didCompact # to combat memAlloc issues        
        loopCnt += 1
        gc.collect() # garbage collection
        # loop time is about 300 ms or 800 ms, with some outliers at 1300 ms. OOR measurements however take longer (timeout)
 
    f_dataLog.close()

main()
