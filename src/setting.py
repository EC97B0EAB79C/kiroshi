import logging

from src.helper import load_json
from src.palette import EPD_PALETTE_MAP
import src.default as Default

from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class Setting:
    def __init__(self, settings_file=Default.SETTINGS_FILE):
        # Load JSON files
        logger.debug(f"Loading settings from {settings_file}")
        self.settings_file = settings_file
        self.settings = load_json(self.settings_file)
        self._verify_settings()

        # Load panels
        panel_spec = self.settings.get("panel_spec", Default.PANEL_SPEC_FILE)
        logger.debug(f"Loading panels from {panel_spec}")
        self.panels = load_json(panel_spec)

        # Load schedule
        self.schedule = self.settings.get("schedule", [])
        if not self.schedule:
            raise ValueError("No schedule found in settings")

        self.schedule_length = len(self.schedule)
        if self.schedule_length == 0:
            raise ValueError("Schedule is empty")

        self.bedtime = self.settings.get("bedtime", None)

        # Initialize current panel index
        self.current_panel_index = 0

        # Verify
        self._verify_panels()

    def _verify_settings(self):
        if not self.settings:
            raise ValueError(f"Failed to load settings from {self.settings_file}")

    def _verify_panels(self):
        if not self.panels:
            raise ValueError(f"Failed to load panels")
        logger.info(f"Loaded {len(self.panels)} panels")

        for s in self.schedule:
            panel_id = s.get("id", 0)
            if (
                not isinstance(panel_id, int)
                or panel_id < 0
                or panel_id >= len(self.panels)
            ):
                raise ValueError(
                    f"Invalid panel ID: {panel_id}. Must be an integer between 0 and {len(self.panels) - 1}."
                )

    def set_epd_settings(self, epd):
        for panel in self.panels:
            panel["width"] = epd.width
            panel["height"] = epd.height

        epd_name = self.get_epd_name()
        palette = EPD_PALETTE_MAP.get(epd_name, None)
        if palette is None:
            raise ValueError(f"Unsupported e-Paper display: {epd_name}")

        for panel in self.panels:
            panel["settings"]["palette"] = palette

    def get_next_panel(self):
        if self.is_bedtime():
            logger.info("Starting bedtime mode")
            bedtime_panel = self.bedtime.get("id", 0)
            panel_duration = self.get_bedtime_duration()
            return bedtime_panel, self.panels[bedtime_panel], panel_duration

        current_panel_spec = self.schedule[self.current_panel_index]
        panel_id = current_panel_spec.get("id", 0)
        panel_duration = self.get_panel_duration(current_panel_spec)

        self.current_panel_index = (self.current_panel_index + 1) % self.schedule_length

        return panel_id, self.panels[panel_id], panel_duration

    def get_refresh_interval(self):
        return self.settings.get("refresh", Default.DURATION_REFRESH)

    def get_epd_name(self):
        return self.settings.get("epd", "mock")

    def get_panel_duration(self, current_panel_spec):
        duration = current_panel_spec.get("duration", Default.DURATION_PANEL) * 60

        if not self.bedtime:
            return duration

        return min(duration, self.get_time_to_bedtime())

    def get_time_to_bedtime(self):
        start_time = self._parse_time(self.bedtime["start"])
        duration = self._calculate_duration(start_time)

        return duration

    def get_bedtime_duration(self):
        end_time = self._parse_time(self.bedtime["end"])
        duration = self._calculate_duration(end_time)

        return duration

    def is_bedtime(self):
        if not self.bedtime:
            return False

        now = datetime.now()
        start_time = self._parse_time(self.bedtime["start"])
        end_time = self._parse_time(self.bedtime["end"])

        if start_time < end_time:
            return start_time <= now.time() < end_time
        else:
            return now.time() >= start_time or now.time() < end_time

    def _parse_time(self, time_str):
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            logger.error(f"Invalid time format: {time_str}. Expected format is HH:MM.")
            return None

    def _calculate_duration(self, time):
        now = datetime.now()
        target_time = datetime.combine(now.date(), time)

        if target_time < now:
            target_time += timedelta(days=1)

        duration = target_time - now

        return duration.total_seconds()
