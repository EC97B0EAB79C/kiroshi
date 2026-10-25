import logging
from datetime import datetime, timedelta, time

import jsonschema

import src.helper as Helper
import src.default as Default
from src.schema import SETTINGS_SCHEMA, PANELS_SCHEMA

logger = logging.getLogger(__name__)


def _validate(data, schema, file_path):
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        where = "/".join(str(p) for p in e.absolute_path) or "(root)"
        raise ValueError(f"Invalid config {file_path} at {where}: {e.message}") from None


def _parse_time(time_str) -> time:
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Expected format is HH:MM.")


class Setting:
    def __init__(self, settings_file=Default.SETTINGS_FILE):
        self.settings_file = settings_file
        self.current_panel_index = 0
        self._load()

    def _load(self):
        """Load and check both files. Change nothing when a file is not valid."""
        logger.debug(f"Loading settings from {self.settings_file}")
        settings_update = Helper.get_file_modified_time(self.settings_file)
        settings = Helper.load_json(self.settings_file)
        _validate(settings, SETTINGS_SCHEMA, self.settings_file)

        panel_spec = settings.get("panel_spec", Default.PANEL_SPEC_FILE)
        logger.debug(f"Loading panels from {panel_spec}")
        panels_update = Helper.get_file_modified_time(panel_spec)
        panels = Helper.load_json(panel_spec)
        _validate(panels, PANELS_SCHEMA, panel_spec)

        bedtime = settings.get("bedtime")
        ids = [s["id"] for s in settings["schedule"]] + ([bedtime["id"]] if bedtime else [])
        for panel_id in ids:
            if panel_id >= len(panels):
                raise ValueError(
                    f"Invalid panel ID: {panel_id}. Must be an integer between 0 and {len(panels) - 1}."
                )
        if bedtime:
            bedtime = {**bedtime, "start": _parse_time(bedtime["start"]), "end": _parse_time(bedtime["end"])}

        self.settings, self.panels, self.bedtime = settings, panels, bedtime
        self.schedule = settings["schedule"]
        self.setting_update, self.panels_update = settings_update, panels_update
        self.current_panel_index %= len(self.schedule)
        logger.info(f"Loaded {len(self.panels)} panels")

    def _update(self):
        try:
            panel_spec = self.settings.get("panel_spec", Default.PANEL_SPEC_FILE)
            changed = (
                Helper.get_file_modified_time(self.settings_file) != self.setting_update
                or Helper.get_file_modified_time(panel_spec) != self.panels_update
            )
            if changed:
                logger.info("Config file updated, reloading")
                self._load()
        except (ValueError, RuntimeError) as e:
            logger.error(f"Reload failed, keeping the old config: {e}")

    def get_next_panel(self):
        self._update()
        if self.is_bedtime():
            logger.info("Starting bedtime mode")
            bedtime_panel = self.bedtime["id"]
            return bedtime_panel, self.panels[bedtime_panel], self.get_bedtime_duration()

        current_panel_spec = self.schedule[self.current_panel_index]
        panel_id = current_panel_spec["id"]
        panel_duration = self.get_panel_duration(current_panel_spec)

        self.current_panel_index = (self.current_panel_index + 1) % len(self.schedule)

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
        return self._calculate_duration(self.bedtime["start"])

    def get_bedtime_duration(self):
        return self._calculate_duration(self.bedtime["end"])

    def is_bedtime(self):
        if not self.bedtime:
            return False

        now = datetime.now().time()
        start_time, end_time = self.bedtime["start"], self.bedtime["end"]

        if start_time < end_time:
            return start_time <= now < end_time
        return now >= start_time or now < end_time

    def _calculate_duration(self, target):
        now = datetime.now()
        target_time = datetime.combine(now.date(), target)

        if target_time < now:
            target_time += timedelta(days=1)

        return (target_time - now).total_seconds()
