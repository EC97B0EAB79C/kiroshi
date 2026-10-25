"""Kiroshi e-Paper bridge for the STM32 NUCLEO-F429ZI board (MicroPython).

The computer that runs Kiroshi sends GPIO, SPI and delay commands over
Ethernet. This board does them on the display. The other side is the
STM32 class in lib/waveshare_epd/epdconfig.py.
"""

import socket
import struct
import time

import network
from machine import SPI, Pin

PORT = 5000

# The order is the pin ID: RST, DC, CS, BUSY, PWR (same as the STM32 class)
PINS = [
    Pin("PF12", Pin.OUT),  # RST  (D8)
    Pin("PD15", Pin.OUT),  # DC   (D9)
    Pin("PD14", Pin.OUT, value=1),  # CS (D10)
    Pin("PF13", Pin.IN),  # BUSY (D7)
    Pin("PE9", Pin.OUT),  # PWR  (D6)
]
spi = SPI(1, baudrate=4000000)  # CLK PB3 (D23), DIN PB5 (D22)
buf = bytearray(4096)


def serve(conn):
    """Do the commands until the computer closes the connection.

    A command is: op (1 byte), pin (1 byte), value (4 bytes, big-endian).
    """
    head = bytearray(6)
    while conn.readinto(head) == 6:
        op, pin, value = struct.unpack(">BBI", head)
        op = chr(op)
        if op == "W":  # Set a pin
            PINS[pin](value)
        elif op == "R":  # Read a pin
            conn.write(bytes([PINS[pin]()]))
        elif op == "D":  # Wait "value" ms
            time.sleep_ms(value)
        elif op == "S":  # Write the next "value" bytes to SPI
            while value:
                chunk = memoryview(buf)[: min(value, len(buf))]
                if conn.readinto(chunk) != len(chunk):
                    return
                spi.write(chunk)
                value -= len(chunk)


def main():
    lan = network.LAN()
    lan.active(True)
    # DHCP gives the address. For a fixed address, remove "#" and change it:
    # lan.ifconfig(("192.168.1.50", "255.255.255.0", "192.168.1.1", "192.168.1.1"))
    while not lan.isconnected():
        time.sleep_ms(100)
    print("Kiroshi bridge on", lan.ifconfig()[0], "port", PORT)

    server = socket.socket()
    server.bind(("0.0.0.0", PORT))
    server.listen(1)
    while True:
        conn, _ = server.accept()
        conn.settimeout(60)
        try:
            serve(conn)
        except Exception as e:
            print("Error:", e)
        conn.close()


if __name__ == "__main__":
    main()
