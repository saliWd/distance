##
# example taken from https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble/examples/temp_client.py 
# (and then changed a lot)
##

from time import sleep, ticks_ms, ticks_diff

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)

LOOP_MAX = 500
startTime = ticks_ms()

async def find_beacon(debug_info):
    # Scan for 5 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == "widmedia.ch":
                    return result
                else:
                    if debug_info: print("did find something but name does not match. Name is: "+result.name())
    return None

def print_infos(loopvar, timeStamp, device, result, filehandle):
    name = result.name()[0:11]
    addr = "%s" % device # need to get string representation first...
    addr = addr[20:37]
    txt_csv = "%d, %d, %s, %s, %d\n" % (loopvar, timeStamp, name, addr, result.rssi)
    print (txt_csv, end ="") # need the newline for the csv write. No additional new line here
    filehandle.write(txt_csv)

async def main():
    filehandle = open('data.csv', 'a') # append
    filehandle.write('id, time_ms, name, address, rssi\n')

    loopvar = 0

    # while True:
    while loopvar < LOOP_MAX:
        loopvar = loopvar + 1
        result = await find_beacon(debug_info=False)
        if result:
            device = result.device
            timeStamp = ticks_diff(ticks_ms(), startTime)
            print_infos(loopvar=loopvar, timeStamp=timeStamp, device=device, result=result, filehandle=filehandle)
        else: # it's not a error, just beacon out of range
            print("Loopvar %d: no beacon found" % loopvar)
        sleep(0.5)
 
    filehandle.close()

    print("outputting the file contents\n")
    filehandle = open('data.csv')
    print(filehandle.read())
    filehandle.close()



asyncio.run(main())
