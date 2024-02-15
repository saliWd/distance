##
# example taken from https://github.com/micropython/micropython-lib/blob/master/micropython/bluetooth/aioble/examples/temp_client.py 
# (and then changed a lot)
##

import sys

sys.path.append("")

import uasyncio as asyncio # type: ignore (this is a pylance ignore warning directive)
import aioble # type: ignore (this is a pylance ignore warning directive)

async def find_beacon():
    # Scan for 5 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == "widmedia.ch":
                    return result
                else:
                    print("did find something but name does not match. Name is: "+result.name())
    return None


async def main():
    result = await find_beacon()
    device = result.device
    if not device:
        print("beacon not found")
        return

    try:
        print("Connecting to", device)
        print("connection try name: "+result.name())
        print("connection rssi: "+str(result.rssi))
        connection = await device.connect() # does not always work
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        while True:
            print("reached the while-true loop")
            print("Name: "+result.name())
            print("RSSI: "+str(result.rssi)) # no error but value is not updated, stays at a constant value
            await asyncio.sleep_ms(1000)


asyncio.run(main())
