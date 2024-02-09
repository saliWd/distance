import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import random
import struct

async def find_temp_sensor():
    # Scan for 5 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if(result.name()): # most are empty...
                if result.name()[0:11] == "widmedia.ch":
                    return result.device
                else:
                    print("did find something but name does not match. Name is: "+result.name())
    return None


async def main():
    device = await find_temp_sensor()
    if not device:
        print("beacon not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return


#     async with connection:
#        try:
#            temp_service = await connection.service(_ENV_SENSE_UUID)
#            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
#        except asyncio.TimeoutError:
#            print("Timeout discovering services/characteristics")
#            return

#        while True:
#            temp_deg_c = _decode_temperature(await temp_characteristic.read())
#            print("Temperature: {:.2f}".format(temp_deg_c))
#            await asyncio.sleep_ms(1000)


asyncio.run(main())