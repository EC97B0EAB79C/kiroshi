# Kiroshi

## TODO

### Bugs
- [ ] `Application`: clear `self.panels` cache when `panels.json` reloads (stale panels shown now)
- [ ] `Application.stop()`: do not call `epd.Clear()` from the signal handler while `display()` runs (race)
- [ ] `TogglPanel`: fix memory leak (clear `debug_boxes` in `_draw`)
- [ ] `TogglPanel`: `time_entries[0]` fails when the list is empty or the API returns an error dict
- [ ] `TogglPanel`: `_get_project_details()` can return `None`, then `.get()` fails
- [ ] `TogglPanel.set_size()`: use `Default.FONT_SIZE["H1"]`, not hard-coded `96`
- [ ] `Panel` and subclasses: replace mutable default `settings={}` / `settings=None` with a safe default
- [ ] `Setting.set_epd_settings()`: `panel["settings"]` fails when a panel has no `settings` key
- [ ] `Setting._parse_time()`: returns `None` on bad input, then `datetime.combine()` fails
- [ ] `CalendarPanel._draw()`: returns without border when there are no events
- [ ] `CalendarPanel`: week change check ignores the year (`isocalendar()` week only)
- [ ] `ical.get_events()`: `filter` argument is not used and shadows the built-in
- [ ] `ical._save_cache()`: fails when `.cache/` does not exist
- [ ] `github.get_github_contributions()`: key `"data"` must be `"date"`
- [ ] `.gitignore` ignores `lib/`, `fonts/`, `icons/`, `example/` but these are tracked

### Refactor
- [ ] Remove duplicate `needs_refresh()` overrides (base `Panel` does the same)
- [ ] Move API cache logic (`_request`, `request_interval`, `cache`) into one shared base class or helper
- [ ] Merge `FourPanel`, `HorizontalPanel`, `VerticalPanel` into one `GridPanel(rows, cols)`
- [ ] Simplify `load_panel()`: one registry dict for all panel types
- [ ] Shared `requests.Session` with `timeout` for all API calls (no timeout now)
- [ ] Toggl API: build the auth header once, not in each function
- [ ] Replace `print()` with `logging` in `helper.py` and `api/github.py`
- [ ] Replace `from src.palette import *` with explicit imports
- [ ] Use paths relative to the project root, not the current directory (fonts, icons, `.cache`)
- [ ] Rename `DEBUG` / `Debug` arguments to one name (`debug`)
- [ ] Remove `main_test.py` and `clear.py`; use `EPDManager` with CLI options (see Features)
- [ ] Remove `if __name__ == "__main__"` demo blocks from `src/api/*`; move to tests
- [ ] Add type hints
- [ ] Ensure consistent logging across all modules

### Performance
- [ ] Font cache in `helper.load_font()` (`functools.lru_cache`)
- [ ] Do not quantize the same image more than one time (quantize once in `Panel.draw()`)
- [ ] Partial refresh support in `EPDManager`
- [ ] Coroutines: `asyncio` main loop and `aiohttp` for API requests

### Robustness
- [ ] Retry with backoff for network requests
- [ ] Keep last good data and show it when the API fails
- [ ] Better error message on the display when an API fails
- [ ] Validate config files with JSON schema; show a clear error message

### Tests and CI
- [ ] Tests for `Setting` (schedule, bedtime, reload)
- [ ] Tests for `ical` (`_divide_event`, `_format_event`)
- [ ] Render tests for each panel with the mock EPD (no network)
- [ ] CI: run all tests (`python -m unittest discover`), add `ruff` lint

### Features
- [ ] CLI: `--once` (draw one time and exit), `--output file.png`, `--clear`
- [ ] Panel setup/teardown lifecycle
- [ ] More e-Paper display models (and their palettes)
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
