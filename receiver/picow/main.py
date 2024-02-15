##
# example taken from https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble/examples/temp_client.py 
# (and then changed a lot)
##

from time import sleep

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)

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

def print_infos(loopvar, device, result, filehandle, write_to_file):
    name = result.name()[0:11]
    addr = "%s" % device # need to get string representation first...
    addr = addr[20:37]
    txt_csv = "%d, %s, %s, %d\n" % (loopvar, name, addr, result.rssi)
    print (txt_csv, end ="") # need the newline for the csv write. No additional new line here

    if write_to_file:
        filehandle.write(txt_csv)

async def main():
    filehandle = open('data.csv', 'w')
    filehandle.write('id, name, address, rssi\n')

    loopvar = 0

    # while True:
    while loopvar < 5:
        loopvar = loopvar + 1
        result = await find_beacon(debug_info=False)
        device = result.device
        if not device:
            print("beacon not found")
            return
        print_infos(loopvar=loopvar, device=device, result=result, filehandle=filehandle, write_to_file=True)
        sleep(0.5)
 
    filehandle.close()

    print("outputting the file contents\n")
    filehandle = open('data.csv')
    print(filehandle.read())
    filehandle.close()



asyncio.run(main())
