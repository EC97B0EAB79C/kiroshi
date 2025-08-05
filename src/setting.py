from src.helper import load_json


class Setting:
    def __init__(self, settings_file="example/setting.json"):
        # Load JSON files
        self.settings_file = settings_file
        self.settings = load_json(self.settings_file)
        if not self.settings:
            raise ValueError(f"Failed to load settings from {self.settings_file}")

        self.panels = load_json(self.settings.get("panel_spec", "example/panels.json"))
        if not self.panels:
            raise ValueError(
                f"Failed to load panels from {self.settings.get('panel_spec', 'example/panels.json')}"
            )

        # Set default values
        if self.settings.get("width", 0) <= 0 or self.settings.get("height", 0) <= 0:
            raise ValueError("Width or height is not set or invalid")
        for panel in self.panels:
            panel["width"] = self.settings.get("width", 0)
            panel["height"] = self.settings.get("height", 0)

        if "palette" not in self.settings:
            raise ValueError("Palette not found in settings")
        if self.settings["palette"] not in ["6_colors", "gray"]:
            raise ValueError(
                f"Invalid palette: {self.settings['palette']}. Expected '6_colors' or 'gray'."
            )
        for panel in self.panels:
            panel["settings"]["palette"] = self.settings["palette"]

        # Load schedule
        self.schedule = self.settings.get("schedule", [])
        if not self.schedule:
            raise ValueError("No schedule found in settings")

        self.schedule_length = len(self.schedule)
        if self.schedule_length == 0:
            raise ValueError("Schedule is empty")

        #
        self.current_panel_index = 0

    def get_next_panel(self):
        current_panel_spec = self.schedule[self.current_panel_index]
        panel_id = current_panel_spec.get("id", 0)
        panel_duration = current_panel_spec.get("duration", 5)

        self.current_panel_index = (self.current_panel_index + 1) % self.schedule_length

        return self.panels[panel_id], panel_duration
