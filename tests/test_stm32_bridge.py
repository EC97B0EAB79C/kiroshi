"""Run the epd7in3e driver through the STM32 bridge on localhost (no hardware)."""
import importlib
import importlib.util
import os
import socket
import sys
import threading
import types
import unittest
from unittest.mock import patch

from PIL import Image

import src.default as Default


class FakePin:
    OUT, IN = 1, 0

    def __init__(self, name, mode, value=1):
        self.value = value  # BUSY stays 1 (idle)

    def __call__(self, value=None):
        if value is None:
            return self.value
        self.value = value


class FakeSPI:
    def __init__(self, *args, **kwargs):
        self.data = bytearray()

    def write(self, buf):
        self.data += buf


def load_firmware():
    machine = types.ModuleType("machine")
    machine.Pin, machine.SPI = FakePin, FakeSPI
    with patch.dict(sys.modules, machine=machine, network=types.ModuleType("network")):
        spec = importlib.util.spec_from_file_location("bridge", Default.ROOT / "firmware/stm32/main.py")
        bridge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bridge)
    bridge.time = types.SimpleNamespace(sleep_ms=lambda ms: None)
    return bridge


class TestSTM32Bridge(unittest.TestCase):
    def test_display(self):
        bridge = load_firmware()
        server = socket.create_server(("127.0.0.1", 0))
        self.addCleanup(server.close)

        def board():
            conn, _ = server.accept()
            # MicroPython socket API: readinto() reads all bytes
            bridge.serve(types.SimpleNamespace(readinto=conn.makefile("rb").readinto, write=conn.sendall))
            conn.close()

        thread = threading.Thread(target=board, daemon=True)
        thread.start()

        sys.path.insert(0, str(Default.ROOT / "lib"))
        with patch.dict(os.environ, EPD_HOST=f"127.0.0.1:{server.getsockname()[1]}"):
            from waveshare_epd import epdconfig, epd7in3e
            importlib.reload(epdconfig)
        self.assertIsInstance(epdconfig.implementation, epdconfig.STM32)

        epd = epd7in3e.EPD()
        epd.init()
        epd.display(epd.getbuffer(Image.new("RGB", (epd.width, epd.height), "white")))
        epd.sleep()
        thread.join(10)

        # Command 0x10, then all pixels white (0x11: two pixels in one byte)
        self.assertIn(b"\x10" + b"\x11" * (epd.width * epd.height // 2), bridge.spi.data)
        # RST, DC, CS, BUSY, PWR at the end: power is off
        self.assertEqual([pin() for pin in bridge.PINS], [0, 0, 1, 1, 0])


if __name__ == "__main__":
    unittest.main()
