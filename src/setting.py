import logging

from src.helper import load_json
from src.palette import EPD_PALETTE_MAP

from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class Setting:
    def __init__(self, settings_file="example/setting.json"):
        # Load JSON files
        logger.debug(f"Loading settings from {settings_file}")
        self.settings_file = settings_file
        self.settings = load_json(self.settings_file)
        self._verify_settings()

        # Load panels
        panel_spec = self.settings.get("panel_spec", "example/panels.json")
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
            bedtime_panel = self.bedtime.get("id", 0)
            panel_duration = self.get_bedtime_duration()
            return bedtime_panel, self.panels[bedtime_panel], panel_duration

        current_panel_spec = self.schedule[self.current_panel_index]
        panel_id = current_panel_spec.get("id", 0)
        panel_duration = self.get_panel_duration(current_panel_spec)

        self.current_panel_index = (self.current_panel_index + 1) % self.schedule_length

        return panel_id, self.panels[panel_id], panel_duration

    def get_refresh_interval(self):
        return self.settings.get("refresh", 60)

    def get_epd_name(self):
        return self.settings.get("epd", "mock")

    def get_panel_duration(self, current_panel_spec):
        duration = current_panel_spec.get("duration", 5)

        if not self.bedtime:
            return duration

        return min(duration, self.get_time_to_bedtime().total_seconds() // 60)

    def get_time_to_bedtime(self):
        now = datetime.now()
        start_time = datetime.strptime(self.bedtime["start"], "%H:%M").time()

        if now.time() < start_time:
            return datetime.combine(now.date(), start_time) - now
        else:
            return datetime.combine(now.date() + timedelta(days=1), start_time) - now

    def get_bedtime_duration(self):
        now = datetime.now()
        end_time = datetime.strptime(self.bedtime["end"], "%H:%M").time()

        if now.time() < end_time:
            return datetime.combine(now.date(), end_time) - now
        else:
            return datetime.combine(now.date() + timedelta(days=1), end_time) - now

    def is_bedtime(self):
        if not self.bedtime:
            return False

        now = datetime.now()
        start_time = datetime.strptime(self.bedtime["start"], "%H:%M").time()
        end_time = datetime.strptime(self.bedtime["end"], "%H:%M").time()

        if start_time < end_time:
            return start_time <= now.time() < end_time
        else:
            return now.time() >= start_time or now.time() < end_time
