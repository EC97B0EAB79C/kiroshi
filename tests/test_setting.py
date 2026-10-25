import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

from src.setting import Setting

PANELS = [{"type": "text", "settings": {"text": "a"}}, {"type": "time"}, {"type": "text"}]


class TestSetting(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.panels_file = os.path.join(self.dir.name, "panels.json")
        self.settings_file = os.path.join(self.dir.name, "setting.json")
        self.write(self.panels_file, PANELS)
        self.write_settings()

    def tearDown(self):
        self.dir.cleanup()

    def write(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f)

    def write_settings(self, **extra):
        settings = {
            "panel_spec": self.panels_file,
            "schedule": [{"id": 0, "duration": 2}, {"id": 1, "duration": 1}],
            **extra,
        }
        self.write(self.settings_file, settings)

    def test_schedule_rotates(self):
        setting = Setting(self.settings_file)
        ids = [setting.get_next_panel()[0] for _ in range(3)]
        self.assertEqual(ids, [0, 1, 0])

    def test_panel_duration_in_seconds(self):
        setting = Setting(self.settings_file)
        self.assertEqual(setting.get_next_panel()[2], 120)

    def test_invalid_panel_id(self):
        self.write_settings(schedule=[{"id": 5}])
        with self.assertRaisesRegex(ValueError, "Invalid panel ID: 5"):
            Setting(self.settings_file)

    def test_schema_error_message(self):
        self.write_settings(schedule=[{"duration": 1}])
        with self.assertRaisesRegex(ValueError, "schedule/0.*'id' is a required property"):
            Setting(self.settings_file)

    def test_unknown_panel_type(self):
        self.write(self.panels_file, [{"type": "unknown"}])
        self.write_settings(schedule=[{"id": 0}])
        with self.assertRaisesRegex(ValueError, "Invalid config"):
            Setting(self.settings_file)

    def test_bad_bedtime_format(self):
        self.write_settings(bedtime={"start": "late", "end": "06:00", "id": 2})
        with self.assertRaisesRegex(ValueError, "bedtime/start"):
            Setting(self.settings_file)

    def test_bedtime(self):
        self.write_settings(bedtime={"start": "22:00", "end": "06:00", "id": 2})
        setting = Setting(self.settings_file)
        with patch("src.setting.datetime") as mock_datetime:
            mock_datetime.strptime = datetime.strptime
            mock_datetime.combine = datetime.combine
            mock_datetime.now.return_value = datetime(2026, 1, 1, 23, 0)
            self.assertTrue(setting.is_bedtime())
            panel_id, _, duration = setting.get_next_panel()
            self.assertEqual(panel_id, 2)
            self.assertEqual(duration, 7 * 3600)

            mock_datetime.now.return_value = datetime(2026, 1, 1, 12, 0)
            self.assertFalse(setting.is_bedtime())
            # Panel time is cut at bedtime start
            self.assertEqual(setting.get_panel_duration({"duration": 1000}), 10 * 3600)

    def test_reload(self):
        setting = Setting(self.settings_file)
        old_spec = setting.panels[0]
        self.write(self.panels_file, [{"type": "time"}] * 2)
        os.utime(self.panels_file, (0, 0))
        _, spec, _ = setting.get_next_panel()
        self.assertEqual(spec, {"type": "time"})
        self.assertIsNot(spec, old_spec)

    def test_bad_reload_keeps_old_config(self):
        setting = Setting(self.settings_file)
        with open(self.panels_file, "w") as f:
            f.write("not json")
        os.utime(self.panels_file, (0, 0))
        _, spec, _ = setting.get_next_panel()
        self.assertEqual(spec, PANELS[0])


if __name__ == "__main__":
    unittest.main()
