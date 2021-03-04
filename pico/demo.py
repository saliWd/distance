# Boilerplate code which will be needed for any program using the Pimoroni Display Pack
# Import the module containing the display code
import picodisplay as display
import time, random


def widmerWrite():
    display.set_pen(makeRed)
    display.text("widmer:",10,10,64,6)

    display.set_pen(makeBlue)
    display.rectangle(5,50,width-10, height-20)

    display.update

# Get the width of the display, in pixels
width = display.get_width()
# Get the height of the display, in pixels
height = display.get_height()

# Use the above to create a buffer for the screen.  It needs to be 2 bytes for every pixel.
display_buffer = bytearray(width * height * 2)

# Start the display!
display.init(display_buffer)

widmerWrite()
