import utime
import picodisplay

# Initialise Picodisplay with a bytearray display buffer
buf = bytearray(picodisplay.get_width() * picodisplay.get_height() * 2)
picodisplay.init(buf)
picodisplay.set_backlight(1.0)

picodisplay.set_pen(255, 0, 0)                    # Set a red pen
picodisplay.clear()                               # Clear the display buffer
picodisplay.set_pen(255, 255, 255)                # Set a white pen
picodisplay.text("widmer", 10, 10, 240, 6)        # Add some text
picodisplay.update()                              # Update the display with our changes

picodisplay.set_led(255, 0, 0)   # Set the RGB LED to red
utime.sleep(1)                   # Wait for a second
picodisplay.set_led(0, 255, 0)   # Set the RGB LED to green
utime.sleep(1)                   # Wait for a second
picodisplay.set_led(0, 0, 255)   # Set the RGB LED to blue

while picodisplay.is_pressed(picodisplay.BUTTON_A) == False:
    pass

picodisplay.set_led(0, 255, 0)  # Set the RGB LED to green