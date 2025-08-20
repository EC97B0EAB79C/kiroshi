import sys
import os


libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in3e

if __name__ == "__main__":
    epd = epd7in3e.EPD()
    epd.init()
    epd.Clear()
    epd.sleep()
