import logging
from time import sleep
from datetime import datetime

from src.setting import Setting
from src.panels.loader import load_panel
from src.display.epd_manager import EPDManager

logger = logging.getLogger(__name__)


class Application:
    def __init__(self, settings_file: str, debug: bool = False):
        self.debug = debug
        self.settings = Setting(settings_file)
        self.epd_manager = EPDManager(self.settings.get_epd_name())

        # Panel ID -> (spec, panel). A new spec (config reload) makes a new panel.
        self.panels = {}
        self.running = False

    def _get_panel(self, panel_id, spec):
        cached = self.panels.get(panel_id)
        if cached is None or cached[0] is not spec:
            epd = self.epd_manager.epd
            panel = load_panel(spec, self.debug, epd.width, epd.height, self.epd_manager.palette)
            self.panels[panel_id] = cached = (spec, panel)
        return cached[1]

    def draw_once(self):
        panel_id, spec, _ = self.settings.get_next_panel()
        self.epd_manager.set_panel(self._get_panel(panel_id, spec).draw())

    def run(self):
        logger.info("Starting application loop")
        self.running = True
        last_update = datetime.min
        duration = 0

        try:
            while self.running:
                full_refresh = False
                now = datetime.now()

                if (now - last_update).total_seconds() > duration:
                    panel_id, spec, duration = self.settings.get_next_panel()
                    logger.info(f"Displaying panel {panel_id} for {duration} seconds")
                    last_update = now
                    full_refresh = True

                    if spec.get("refresh", False):
                        refresh_interval = self.settings.get_refresh_interval()
                    else:
                        refresh_interval = duration

                panel = self._get_panel(panel_id, spec)
                image = panel.draw()

                if panel.needs_refresh() or full_refresh:
                    self.epd_manager.set_panel(image)
                else:
                    logger.debug("Image unchanged, skipping update")

                self._sleep_interruptible(refresh_interval)
        finally:
            self.epd_manager.cleanup()

    def _sleep_interruptible(self, seconds: float):
        slept = 0
        while slept < seconds and self.running:
            sleep(min(1, seconds - slept))
            slept += 1

    def stop(self):
        # Only set the flag. run() cleans up the display when the loop ends.
        self.running = False
