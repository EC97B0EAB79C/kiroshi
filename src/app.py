import asyncio
import logging
import signal
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
        self.running = True
        self._loop = None
        self._stop = None

    def _get_panel(self, panel_id, spec):
        cached = self.panels.get(panel_id)
        if cached is None or cached[0] is not spec:
            epd = self.epd_manager.epd
            panel = load_panel(spec, self.debug, epd.width, epd.height, self.epd_manager.palette)
            self.panels[panel_id] = cached = (spec, panel)
        return cached[1]

    async def _show(self, panel_id, spec, full_refresh=True):
        """Get new data, then draw and display only when something changed."""
        panel = self._get_panel(panel_id, spec)
        await panel.update()

        if not (panel.needs_refresh() or full_refresh):
            logger.debug("Nothing changed, skipping draw")
            return

        image = panel.draw()
        # The display update is slow (blocking SPI); run it in a thread
        await asyncio.to_thread(self.epd_manager.set_panel, image)

    def draw_once(self):
        panel_id, spec, _ = self.settings.get_next_panel()
        asyncio.run(self._show(panel_id, spec))

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        logger.info("Starting application loop")
        self._loop = asyncio.get_running_loop()
        self._stop = asyncio.Event()
        for sig in (signal.SIGINT, signal.SIGTERM):
            self._loop.add_signal_handler(sig, self.stop)

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

                await self._show(panel_id, spec, full_refresh)
                await self._sleep(refresh_interval)
        finally:
            self.epd_manager.cleanup()

    async def _sleep(self, seconds: float):
        """Sleep, but wake up at once on stop()."""
        try:
            await asyncio.wait_for(self._stop.wait(), seconds)
        except asyncio.TimeoutError:
            pass

    def stop(self):
        # Only stop the loop. run() cleans up the display when the loop ends.
        logger.info("Stopping...")
        self.running = False
        if self._loop is not None and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._stop.set)
