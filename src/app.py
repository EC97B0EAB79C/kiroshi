import logging
from time import sleep
from datetime import datetime

from src.setting import Setting
from src.panels.loader import load_panel
from src.display.epd_manager import EPDManager

logger = logging.getLogger(__name__)

class Application:
    def __init__(self, settings_file: str, debug:bool=False):
        self.debug = debug
        self.settings = Setting(settings_file)
        self.epd_manager = EPDManager(self.settings.get_epd_name())

        self.settings.set_epd_settings(self.epd_manager.epd)

        self.panels = {}
        self.running = False

    def run(self):
        logger.info("Starting application loop")
        self.running = True
        last_update = datetime.min
        duration = 0

        while self.running:
            full_refresh = False
            now = datetime.now()

            if (now - last_update).total_seconds() > duration:
                panel_id, current_panel_spec, duration = settings.get_next_panel()
                logger.info(f"Displaying panel {panel_id} for {duration} seconds")
                last_update = now
                FULL_REFRESH = True

                if current_panel_spec.get("refresh", False):
                    refresh_interval = settings.get_refresh_interval()
                else:
                    refresh_interval = duration

            if panel_id not in panels:
                panels[panel_id] = load_panel(current_panel_spec, DEBUG=DEBUG)

            image = panels[panel_id].draw()

            if panels[panel_id].needs_refresh() or FULL_REFRESH:
                set_panel(image, FULL_REFRESH=FULL_REFRESH)
            else:
                logger.debug("Image unchanged, skipping update")

            self._sleep_interruptible(refresh_interval)

    def _sleep_interruptible(self, seconds: int):
            slept = 0
            while slept < seconds and self.running:
                sleep(min(1, seconds - slept))
                slept += 1

        def stop(self):
            self.running = False
            self.epd_manager.cleanup()
