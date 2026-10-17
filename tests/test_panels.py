"""Draw each panel with the mock display data. No network."""
import unittest
from unittest.mock import patch

import requests
from PIL import Image

from src.panels.loader import load_panel

SIZE = (800, 480)

TOGGL_ENTRIES = [
    {"description": "Work", "project_id": 1, "workspace_id": 9, "start": "2026-01-01T10:00:00+00:00", "duration": -1},
    {"description": "Old", "project_id": 1, "workspace_id": 9, "start": "2026-01-01T08:00:00+00:00", "duration": 3600},
]
TOGGL_PROJECTS = {1: {"name": "Project", "color": "#ff0000"}}
GITHUB_WEEKS = [{"contributionDays": [{"color": "#40c463", "date": "2026-01-01"}] * 7}] * 53


def draw(spec):
    panel = load_panel(spec, width=SIZE[0], height=SIZE[1], palette="6_colors")
    return panel, panel.draw()


class TestPanels(unittest.TestCase):
    def assertDrawn(self, image):
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, SIZE)

    def test_text_and_time(self):
        for spec in [{"type": "text", "settings": {"text": "Hello world"}}, {"type": "time"}]:
            panel, image = draw(spec)
            self.assertDrawn(image)
            self.assertTrue(panel.needs_refresh())
            panel.draw()
            self.assertFalse(panel.needs_refresh())

    def test_picture(self):
        _, image = draw({"type": "picture", "settings": {"picture": "icons/error_72dp.png"}})
        self.assertDrawn(image)

    def test_grid_layouts(self):
        child = {"type": "text", "settings": {"text": "x"}}
        for layout in ["four", "horizontal", "vertical"]:
            panel, image = draw({"type": layout, "panels": [child, {"type": "time"}]})
            self.assertDrawn(image)
            self.assertEqual(panel.panels[0].palette_name, "6_colors")

    @patch("src.api.toggl.get_workspace_projects", return_value=TOGGL_PROJECTS)
    @patch("src.api.toggl.get_time_entries", return_value=TOGGL_ENTRIES)
    def test_toggl(self, *_):
        panel, image = draw({"type": "toggl", "settings": {"api_key": "x"}})
        self.assertDrawn(image)
        boxes = len(panel.debug_boxes)
        panel.draw()
        self.assertEqual(len(panel.debug_boxes), boxes)

    @patch("src.api.toggl.get_time_entries", return_value=[])
    def test_toggl_no_entries(self, _):
        self.assertDrawn(draw({"type": "toggl", "settings": {"api_key": "x"}})[1])

    @patch("src.api.github.get_github_contributions", return_value=GITHUB_WEEKS)
    def test_github(self, _):
        self.assertDrawn(draw({"type": "github", "settings": {"username": "x"}})[1])

    @patch("src.api.ical.get_events", return_value=[])
    def test_calendar_empty(self, _):
        self.assertDrawn(draw({"type": "calendar", "settings": {"ical_urls": []}})[1])

    def test_api_error_keeps_last_data(self):
        with patch("src.api.github.get_github_contributions", return_value=GITHUB_WEEKS):
            panel, _ = draw({"type": "github", "settings": {"username": "x"}})
        with patch("src.api.github.get_github_contributions", side_effect=requests.HTTPError("down")):
            panel.draw()
        self.assertEqual(panel.cache, GITHUB_WEEKS)
        self.assertIsNotNone(panel.error)

    def test_api_error_without_data(self):
        with patch("src.api.github.get_github_contributions", side_effect=requests.HTTPError("down")):
            panel, image = draw({"type": "github", "settings": {"username": "x"}})
        self.assertDrawn(image)
        self.assertIsNone(panel.cache)


if __name__ == "__main__":
    unittest.main()
