from src.panel import Panel
from src.panels.grid_panel import GridPanel
from src.panels.text_panel import TextPanel
from src.panels.time_panel import TimePanel
from src.panels.picture_panel import PicturePanel
from src.panels.toggl_panel import TogglPanel
from src.panels.calendar_panel import CalendarPanel
from src.panels.github_panel import GithubPanel
from src.panels.picture_time_panel import PictureTimePanel

# Layout type: (rows, cols)
GRID_LAYOUTS = {
    "four": (2, 2),
    "horizontal": (1, 2),
    "vertical": (2, 1),
}

PANEL_CLASSES = {
    "text": TextPanel,
    "time": TimePanel,
    "toggl": TogglPanel,
    "picture": PicturePanel,
    "calendar": CalendarPanel,
    "github": GithubPanel,
    "picture_time": PictureTimePanel,
}


def load_panel(panel_spec, debug=False, width=0, height=0, palette=None) -> Panel:
    """Create a panel from its spec. Child panels get the same palette."""
    panel_type = panel_spec["type"]
    settings = dict(panel_spec.get("settings", {}))
    if palette:
        settings["palette"] = palette
    args = {"width": width, "height": height, "settings": settings, "debug": debug}

    if panel_type in GRID_LAYOUTS:
        rows, cols = GRID_LAYOUTS[panel_type]
        children = [
            load_panel(spec, debug, palette=settings.get("palette"))
            for spec in panel_spec.get("panels", [])
        ]
        return GridPanel(**args, panels=children, rows=rows, cols=cols)

    if panel_type in PANEL_CLASSES:
        return PANEL_CLASSES[panel_type](**args)

    raise ValueError(f"Unknown panel type: {panel_type}")
