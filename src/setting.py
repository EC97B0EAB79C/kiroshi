import logging

from src.helper import load_json
from src.palette import EPD_PALETTE_MAP

logger = logging.getLogger(__name__)


class Setting:
    def __init__(self, settings_file="example/setting.json"):
        # Load JSON files
        logger.debug(f"Loading settings from {settings_file}")
        self.settings_file = settings_file
        self.settings = load_json(self.settings_file)
        if not self.settings:
            raise ValueError(f"Failed to load settings from {self.settings_file}")

        # Load panels
        panel_spec = self.settings.get("panel_spec", "example/panels.json")
        logger.debug(f"Loading panels from {panel_spec}")
        self.panels = load_json(panel_spec)
        if not self.panels:
            raise ValueError(f"Failed to load panels from {panel_spec}")
        logger.info(f"Loaded {len(self.panels)} panels from {panel_spec}")

        # Load schedule
        self.schedule = self.settings.get("schedule", [])
        if not self.schedule:
            raise ValueError("No schedule found in settings")

        self.schedule_length = len(self.schedule)
        if self.schedule_length == 0:
            raise ValueError("Schedule is empty")

        # Initialize current panel index
        self.current_panel_index = 0

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
        current_panel_spec = self.schedule[self.current_panel_index]
        panel_id = current_panel_spec.get("id", 0)
        panel_duration = current_panel_spec.get("duration", 5)

        self.current_panel_index = (self.current_panel_index + 1) % self.schedule_length

        if (
            not isinstance(panel_id, int)
            or panel_id < 0
            or panel_id >= len(self.panels)
        ):
            raise ValueError(
                f"Invalid panel ID: {panel_id}. Must be an integer between 0 and {len(self.panels) - 1}."
            )
        return panel_id, self.panels[panel_id], panel_duration

    def get_refresh_interval(self):
        return self.settings.get("refresh", 60)

    def get_epd_name(self):
        return self.settings.get("epd", "epd7in3e")
