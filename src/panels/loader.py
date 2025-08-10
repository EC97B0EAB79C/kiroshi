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


def load_panel(panel_spec, DEBUG=False) -> Panel:
    if panel_spec["type"] == "four":
        inner_panels = [load_panel(spec, DEBUG=DEBUG) for spec in panel_spec["panels"]]
        inner_panels += [None] * (4 - len(inner_panels))
        return FourPanel(
            width=panel_spec.get("width", 0),
            height=panel_spec.get("height", 0),
            settings=panel_spec.get("settings", {}),
            panel1=inner_panels[0],
            panel2=inner_panels[1],
            panel3=inner_panels[2],
            panel4=inner_panels[3],
            DEBUG=DEBUG,
        )

    elif panel_spec["type"] == "horizontal":
        inner_panels = [load_panel(spec, DEBUG=DEBUG) for spec in panel_spec["panels"]]
        inner_panels += [None] * (2 - len(inner_panels))
        return HorizontalPanel(
            width=panel_spec.get("width", 0),
            height=panel_spec.get("height", 0),
            settings=panel_spec.get("settings", {}),
            panel1=inner_panels[0],
            panel2=inner_panels[1],
            DEBUG=DEBUG,
        )

    elif panel_spec["type"] == "vertical":
        inner_panels = [load_panel(spec, DEBUG=DEBUG) for spec in panel_spec["panels"]]
        inner_panels += [None] * (2 - len(inner_panels))
        return VerticalPanel(
            width=panel_spec.get("width", 0),
            height=panel_spec.get("height", 0),
            settings=panel_spec.get("settings", {}),
            panel1=inner_panels[0],
            panel2=inner_panels[1],
            DEBUG=DEBUG,
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
            DEBUG=DEBUG,
        )

    raise ValueError(f"Unknown panel type: {panel_type}")
