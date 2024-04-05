from lcd import LCD_disp # import the display class
LCD = LCD_disp() # 240px high, 320px wide, see https://www.waveshare.com/wiki/Pico-ResTouch-LCD-2.8

 
# main program
def main():
    import io
    length = 16 # 16 bytes, 8 pixel
    file1 = io.BytesIO(b'\x00\x01\x02\x03\x04\x05\x06\x07\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F')
    file2 = io.BytesIO(b'\x00\x01\x02\x03\x04\x05\x06\x07\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F')

    position = 0
    while position < length:
        # 'golden model', this one works
        b0 = int.from_bytes(file1.read(1), 'big') # big or little does not matter when reading only one byte
        b1 = int.from_bytes(file1.read(1), 'big')
        LCD.buffer[position] = b1
        LCD.buffer[position+1] = b0
        position += 2
    print("golden model: ")
    print (LCD.buffer[0:15])

    
    position = 0
    import array
    while position < length:
        buffer = array.array('b', file2.read(2))
        LCD.buffer[position] = buffer[1]
        LCD.buffer[position+1] = buffer[0]
        position += 2


    print("trial model: ")
    print (LCD.buffer[0:15])
    
 
main()

