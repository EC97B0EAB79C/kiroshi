from src.panel import Panel

from src.panels.four_panel import FourPanel
from src.panels.horizontal_panel import HorizontalPanel
from src.panels.vertical_panel import VerticalPanel

from src.panels.text_panel import TextPanel
from src.panels.time_panel import TimePanel
from src.panels.picture_panel import PicturePanel
from src.panels.toggl_panel import TogglPanel
from src.panels.calendar_panel import CalendarPanel
from src.panels.github_panel import GithubPanel


def load_panel(panel_spec):
    if panel_spec["type"] == "four":
        inner_panels = [load_panel(spec) for spec in panel_spec["panels"]]
        return FourPanel(
            width=panel_spec.get("width", 0),
            height=panel_spec.get("height", 0),
            settings=panel_spec.get("settings", {}),
            panel1=inner_panels[0] if len(inner_panels) > 0 else None,
            panel2=inner_panels[1] if len(inner_panels) > 1 else None,
            panel3=inner_panels[2] if len(inner_panels) > 2 else None,
            panel4=inner_panels[3] if len(inner_panels) > 3 else None,
        )

    if panel_spec["type"] == "horizontal":
        inner_panels = [load_panel(spec) for spec in panel_spec["panels"]]
        return HorizontalPanel(
            width=panel_spec.get("width", 0),
            height=panel_spec.get("height", 0),
            settings=panel_spec.get("settings", {}),
            panel1=inner_panels[0] if len(inner_panels) > 0 else None,
            panel2=inner_panels[1] if len(inner_panels) > 1 else None,
        )

    if panel_spec["type"] == "vertical":
        inner_panels = [load_panel(spec) for spec in panel_spec["panels"]]
        return VerticalPanel(
            width=panel_spec.get("width", 0),
            height=panel_spec.get("height", 0),
            settings=panel_spec.get("settings", {}),
            panel1=inner_panels[0] if len(inner_panels) > 0 else None,
            panel2=inner_panels[1] if len(inner_panels) > 1 else None,
        )

    panel_classes = {
        "text": TextPanel,
        "time": TimePanel,
        "toggl": TogglPanel,
        "picture": PicturePanel,
        "calendar": CalendarPanel,
        "github": GithubPanel,
    }

    panel_type = panel_spec["type"]
    if panel_type in panel_classes:
        return panel_classes[panel_type](
            width=panel_spec.get("width", 0),
            height=panel_spec.get("height", 0),
            settings=panel_spec.get("settings", {}),
        )

    raise ValueError(f"Unknown panel type: {panel_type}")
