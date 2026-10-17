import os
from datetime import datetime, timedelta

from PIL import ImageDraw

from src.panel import Panel
import src.helper as Helper
import src.default as Default

import src.api.toggl as TogglAPI


class TogglPanel(Panel):
    def __init__(self, width, height, settings=None, debug=False):
        super().__init__(width, height, settings, debug)

        # Text settings
        self.font = self.settings.get("font", Default.FONT_EMOJI)
        self.set_size(width, height)

        # Toggl API settings
        api_key = self.settings.get("api_key", os.getenv("TOGGL_API_KEY"))
        self.auth = f"{api_key}:api_token"

        # Toggl Data (loaded when needed)
        self.projects = {}

        # Debug settings
        self.debug_boxes = []

    def set_size(self, width, height):
        super().set_size(width, height)
        self.font_size = Default.FONT_SIZE["H1"] / 480 * self.height

    def _fetch(self):
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        return TogglAPI.get_time_entries(self.auth, start)

    def _draw(self, image):
        self.debug_boxes = []

        time_entries = self.cached_request(self._fetch)
        if time_entries is None:
            image = Helper.invalid_image(
                image, self.width, self.height, Helper.error_text("Toggl error", self.error)
            )
            return super()._draw(image)

        current_entry = time_entries[0] if time_entries else None
        image = self._draw_current_entry(image, current_entry)
        image = self._draw_summary(image, time_entries)

        image = Helper.quantize_image(image, self.palette_name).convert("RGB")

        return super()._draw(image)

    def _get_project_details(self, project_id, workspace_id=None) -> dict:
        if not project_id:
            return {}
        if project_id not in self.projects and workspace_id is not None:
            try:
                self.projects = TogglAPI.get_workspace_projects(self.auth, workspace_id)
            except Exception:
                pass
        return self.projects.get(project_id) or {}

    def _text(self, draw, xy, text, font, area_height, offset_y):
        """Draw text, centered in a row of area_height that starts at offset_y."""
        spacing = self.margin + self.padding
        bbox = Helper.text_bbox(text, font)
        y = Helper.position(bbox, self.width - spacing * 2, area_height, spacing)[1]
        position = (xy, y - bbox[1] + spacing + offset_y)
        draw.text(position, text, fill="black", font=font, align="left")
        self.debug_boxes.append((position, bbox))
        return position, bbox

    def _draw_current_entry(self, image, entry):
        draw = ImageDraw.Draw(image)

        spacing = self.margin + self.padding
        content_width = self.width - spacing * 2
        content_height = self.height - spacing * 2

        # Draw description
        font = Helper.load_font(self.font, self.font_size)
        if not entry:
            text_description = "No current\ntime entry"
        else:
            text_description = Helper.truncate_text(
                entry.get("description") or "", font, content_width
            )
        self._text(draw, spacing, text_description, font, content_height / 4, 0)

        if not entry:
            return image

        # Draw project name and color
        project = self._get_project_details(
            entry.get("project_id"), entry.get("workspace_id")
        )
        font = Helper.load_font(self.font, self.font_size * 0.8)
        bbox = Helper.text_bbox(project.get("name", ""), font)
        dot = bbox[3] - bbox[1]
        position, _ = self._text(
            draw, spacing + dot, project.get("name", ""), font, content_height / 4, content_height / 4
        )
        center = (spacing + bbox[0] + dot / 2, position[1] + bbox[1] + dot / 2)
        draw.circle(center, radius=dot / 3, fill=project.get("color", "#000000"))
        self.debug_boxes.append(((spacing + bbox[0], position[1] + bbox[1]), (0, 0, dot, dot)))

        # Draw time
        start_time = datetime.fromisoformat(entry.get("start"))
        text_start = start_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        duration = entry.get("duration", -1)
        text_end = "-"
        if duration > 0:
            end_time = start_time + timedelta(seconds=duration)
            text_end = end_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")

        font = Helper.load_font(self.font, self.font_size * 0.6)
        label = Helper.text_bbox("From: ", font)
        value_x = spacing + label[2] - label[0]
        rows = [
            ("From: ", text_start, content_height / 6, content_height / 2),
            ("To: ", text_end, content_height / 4, content_height / 3 * 2),
        ]
        for label_text, value_text, area_height, offset_y in rows:
            self._text(draw, spacing, label_text, font, area_height, offset_y)
            self._text(draw, value_x, value_text, font, area_height, offset_y)

        return image

    def _draw_summary(self, image, time_entries):
        draw = ImageDraw.Draw(image)

        spacing = self.margin
        content_width = self.width - spacing * 2
        content_height = (self.height - spacing * 2) / 10

        summary = {}
        workspaces = {}
        for entry in time_entries:
            project_id = entry.get("project_id")
            duration = entry.get("duration", -1)
            if project_id and duration >= 0:
                summary[project_id] = summary.get(project_id, 0) + duration
                workspaces[project_id] = entry.get("workspace_id")
        total_duration = sum(summary.values())

        if total_duration == 0:
            return image

        current_x = spacing
        for project_id, duration in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            length = content_width * (duration / total_duration)
            draw.rectangle(
                [
                    (current_x, self.height - spacing - content_height),
                    (current_x + length, self.height - spacing),
                ],
                fill=self._get_project_details(project_id, workspaces[project_id]).get(
                    "color", "#000000"
                ),
            )
            current_x += length

        return image

    def _draw_debug(self, image):
        draw = ImageDraw.Draw(image)
        for position, bbox in self.debug_boxes:
            draw.rectangle(
                [
                    bbox[0] + position[0],
                    bbox[1] + position[1],
                    bbox[2] + position[0],
                    bbox[3] + position[1],
                ],
                outline="red",
                width=2,
            )

        return super()._draw_debug(image)
