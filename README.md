# Kiroshi

## Install on a Raspberry Pi

1. Write Raspberry Pi OS Lite to the SD card with Raspberry Pi Imager.
   In the OS customisation settings, set the user, Wi-Fi and SSH.
   Use the 32-bit version for the Pi 2 Model B (it has no Wi-Fi: use Ethernet or a USB Wi-Fi adapter).
2. Connect to the Pi with SSH and run:

   ```sh
   git clone https://github.com/EC97B0EAB79C/kiroshi && sudo kiroshi/install.sh
   ```

   The script installs the packages, enables SPI, makes the config,
   draws one test panel and starts the `kiroshi` service.
   Add `--auto-update` to update one time each week.
3. Change the config in `~/.config/kiroshi/` (`setting.json`, `panels.json`).
   The service reloads it automatically.
4. Add your API keys to `/etc/kiroshi/env`, then run `sudo systemctl restart kiroshi`.

| Task | Command |
| --- | --- |
| See the log | `journalctl -u kiroshi -f` |
| Update | `sudo ~/kiroshi/install.sh --update` |
| Test one panel | `~/kiroshi/.venv/bin/python ~/kiroshi/main.py --once -s ~/.config/kiroshi/setting.json` |
| Stop | `sudo systemctl stop kiroshi` |

Run `install.sh` again at any time to repair the install. It keeps your config.

The 3D-printable case is in [`hardware/`](hardware/README.md).

## Use an STM32 NUCLEO-F429ZI board

The STM32 board cannot run Kiroshi alone. It has no Linux and only 256 KB of RAM.
Kiroshi runs on a computer (for example a Linux server).
The computer sends the display commands over Ethernet to the board.
The board sends them to the display. All panels operate as on a Pi.

1. Connect the e-Paper HAT to the board with the 9-pin cable:

   | e-Paper | VCC | GND | DIN | CLK | CS | DC | RST | BUSY | PWR |
   | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
   | Board pin | 3V3 | GND | PB5 (D22) | PB3 (D23) | PD14 (D10) | PD15 (D9) | PF12 (D8) | PF13 (D7) | PE9 (D6) |

2. Download the MicroPython firmware for
   [NUCLEO_F429ZI](https://micropython.org/download/NUCLEO_F429ZI/).
   Connect the ST-LINK USB port to your computer and write the firmware:

   ```sh
   st-flash --format ihex write firmware.hex
   ```

3. Get Kiroshi and copy the bridge to the board:

   ```sh
   git clone https://github.com/EC97B0EAB79C/kiroshi
   pip install mpremote
   mpremote cp kiroshi/firmware/stm32/main.py :main.py + reset
   ```

4. Connect the board to your network with an Ethernet cable.
   The board gets its address from DHCP.
   To see the address, run `mpremote repl` and push the black RESET button.
   Give the board a fixed address in your router,
   or set it in `firmware/stm32/main.py`.
5. On the computer, install Kiroshi with the address of the board:

   ```sh
   sudo EPD_HOST=192.168.1.50 kiroshi/install.sh
   ```

   The script sets `"epd": "epd7in3e"` and writes `EPD_HOST` to `/etc/kiroshi/env`.
   If you do not use `install.sh`, set `"epd": "epd7in3e"` in `setting.json`
   run `pip install -r requirements.txt`,
   then run `EPD_HOST=192.168.1.50 python main.py -s setting.json`.

## TODO

### Bugs
- [x] `Application`: clear `self.panels` cache when `panels.json` reloads (stale panels shown now)
- [x] `Application.stop()`: do not call `epd.Clear()` from the signal handler while `display()` runs (race)
- [x] `TogglPanel`: fix memory leak (clear `debug_boxes` in `_draw`)
- [x] `TogglPanel`: `time_entries[0]` fails when the list is empty or the API returns an error dict
- [x] `TogglPanel`: `_get_project_details()` can return `None`, then `.get()` fails
- [x] `TogglPanel.set_size()`: use `Default.FONT_SIZE["H1"]`, not hard-coded `96`
- [x] `Panel` and subclasses: replace mutable default `settings={}` / `settings=None` with a safe default
- [x] `Setting.set_epd_settings()`: `panel["settings"]` fails when a panel has no `settings` key
- [x] `Setting._parse_time()`: returns `None` on bad input, then `datetime.combine()` fails
- [x] `CalendarPanel._draw()`: returns without border when there are no events
- [x] `CalendarPanel`: week change check ignores the year (`isocalendar()` week only)
- [x] `ical.get_events()`: `filter` argument is not used and shadows the built-in
- [x] `ical._save_cache()`: fails when `.cache/` does not exist
- [x] `github.get_github_contributions()`: key `"data"` must be `"date"`
- [x] `.gitignore` ignores `lib/`, `fonts/`, `icons/`, `example/` but these are tracked

### Refactor
- [x] Remove duplicate `needs_refresh()` overrides (base `Panel` does the same)
- [x] Move API cache logic (`_request`, `request_interval`, `cache`) into one shared base class or helper
- [x] Merge `FourPanel`, `HorizontalPanel`, `VerticalPanel` into one `GridPanel(rows, cols)`
- [x] Simplify `load_panel()`: one registry dict for all panel types
- [x] Shared `requests.Session` with `timeout` for all API calls (no timeout now)
- [x] Toggl API: build the auth header once, not in each function
- [x] Replace `print()` with `logging` in `helper.py` and `api/github.py`
- [x] Replace `from src.palette import *` with explicit imports
- [x] Use paths relative to the project root, not the current directory (fonts, icons, `.cache`)
- [x] Rename `DEBUG` / `Debug` arguments to one name (`debug`)
- [x] Remove `main_test.py` and `clear.py`; use `EPDManager` with CLI options (see Features)
- [x] Remove `if __name__ == "__main__"` demo blocks from `src/api/*`; move to tests
- [x] Add type hints
- [x] Ensure consistent logging across all modules

### Performance
- [x] Font cache in `helper.load_font()` (`functools.lru_cache`)
- [x] Do not quantize the same image more than one time (quantize once in `Panel.draw()`)
- [ ] Partial refresh support in `EPDManager` (not possible on `epd7in3e`: the Waveshare driver has full refresh only)
- [x] Coroutines: `asyncio` main loop; API requests run at the same time (in worker threads, with the existing `requests` retry, not `aiohttp`)
- [x] Draw only when data or time changed; parse a calendar only when it changed

### Robustness
- [x] Retry with backoff for network requests
- [x] Keep last good data and show it when the API fails
- [x] Better error message on the display when an API fails
- [x] Validate config files with JSON schema; show a clear error message

### Tests and CI
- [x] Tests for `Setting` (schedule, bedtime, reload)
- [x] Tests for `ical` (`_divide_event`, `_format_event`)
- [x] Render tests for each panel with the mock EPD (no network)
- [x] CI: run all tests (`python -m unittest discover`), add `ruff` lint

### Features
- [x] CLI: `--once` (draw one time and exit), `--clear`
- [ ] CLI: `--output file.png`
- [ ] Panel setup/teardown lifecycle
- [ ] More e-Paper display models (and their palettes)
- [x] STM32 NUCLEO-F429ZI board drives the display over Ethernet
- [ ] Weather panel (for example Open-Meteo, no API key)
- [ ] Picture slideshow panel (folder or URL)
- [ ] Quote / RSS / news text panel
- [ ] QR code panel (for example Wi-Fi login)
- [ ] Settings for date/time format and time zone
- [ ] Local web page to preview the current image and change settings
- [ ] Home Assistant / MQTT panel
- [ ] Dockerfile for development without hardware

### Done
- [x] Implement Mock EPD Library
  - [x] Modify EPD lib search mechanism
- [x] Modify `main.py`
