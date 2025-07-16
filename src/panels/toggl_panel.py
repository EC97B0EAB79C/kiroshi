from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone, timedelta

from src.panel import Panel
import src.helper as Helper
from src.palette import *

import src.api.toggl as TogglAPI


class TogglPanel(Panel):
    def __init__(self, width, height, settings=None, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

        # Text settings
        self.font = settings.get("font")
        self.font_size = 96 / 480 * self.height

        # Toggl API settings
        self.auth = f"{settings.get('api_key', '')}:api_token"
        self.api_key_status = TogglAPI.verify_api_key(self.auth)

        # Margin, padding and border settings
        self.padding = settings.get("padding", 10)

        # Toggl Data
        self.projects = TogglAPI.get_workspace_projects(self.auth, self.api_key_status)

        # Debug settings
        self.debug_boxes = []

    def _draw(self, image):
        if not self.api_key_status:
            image = self._draw_api_invalid(image)
            return image

        time_entries = TogglAPI.get_time_entries(
            self.auth, (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        )
        current_entry = time_entries[0]
        image = self._draw_current_entry(image, current_entry)
        image = self._draw_summary(image, time_entries)

        image = Helper.quantize_image(image, self.palette_name)

        return image

    def _get_project_details(self, project_id, workspace_id=None):
        if not project_id:
            return None
        if project_id in self.projects:
            return self.projects[project_id]

        if workspace_id is None:
            return None
        self.projects = TogglAPI.get_workspace_projects(self.auth, workspace_id)
        return self.projects.get(project_id, None)

    def _draw_current_entry(self, image, entry):
        draw = ImageDraw.Draw(image)

        spacing = self.margin + self.padding
        content_width = self.width - spacing * 2
        content_height = self.height - spacing * 2

        # Draw description
        # Set content
        if not entry:
            text_description = "No current\ntime entry"
        else:
            text_description = entry.get("description", "")
            text_description = Helper.truncate_text(
                text_description, font, content_width
            )
        # Draw content
        font = Helper.load_font(self.font, self.font_size)
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), text_description, font=font, align="left"
        )
        position = Helper.position(bbox, content_width, content_height / 4, spacing)
        position = (spacing, position[1] - bbox[1] + spacing)
        draw.text(position, text_description, fill="black", font=font, align="left")
        self.debug_boxes.append((position, bbox))

        if not entry:
            return image

        # Draw project name and color
        # Set content
        text_project = ""
        color_project = "#000000"
        if entry.get("project_id"):
            current_project = self._get_project_details(
                entry.get("project_id"), entry.get("workspace_id")
            )
            text_project = current_project.get("name", "")
            color_project = current_project.get("color", "#000000")
        # Draw content
        font = Helper.load_font(self.font, self.font_size * 0.8)
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), text_project, font=font, align="left"
        )
        position = Helper.position(bbox, content_width, content_height / 4, spacing)
        position = (spacing, position[1] - bbox[1] + spacing + content_height / 4)
        draw.circle(
            (
                position[0] + bbox[0] + (bbox[3] - bbox[1]) / 2,
                position[1] + bbox[1] + (bbox[3] - bbox[1]) / 2,
            ),
            radius=(bbox[3] - bbox[1]) / 3,
            fill=color_project,
        )
        self.debug_boxes.append(
            (
                (position[0] + bbox[0], position[1] + bbox[1]),
                (0, 0, bbox[3] - bbox[1], bbox[3] - bbox[1]),
            )
        )
        position = (position[0] + (bbox[3] - bbox[1]), position[1])
        draw.text(
            position,
            text_project,
            fill="black",
            font=font,
            align="left",
        )
        self.debug_boxes.append((position, bbox))

        # Draw time
        # Set content
        local_tz = datetime.now().astimezone().tzinfo
        start_time = datetime.fromisoformat(entry.get("start"))
        text_start = f"{start_time.astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S')}"
        duration = entry.get("duration", -1)
        text_end = ""
        if duration > 0:
            end_time = start_time + timedelta(seconds=duration)
            text_end = f"{end_time.astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            text_end = "-"
        # Draw content
        ## From
        font = Helper.load_font(self.font, self.font_size * 0.6)
        bbox_from = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), "From: ", font=font, align="left"
        )
        position_from = Helper.position(
            bbox_from, content_width, content_height / 6, spacing
        )
        position_from = (
            spacing,
            content_height / 2 + position_from[1] - bbox_from[1] + spacing,
        )
        draw.text(position_from, "From: ", fill="black", font=font, align="left")
        self.debug_boxes.append((position_from, bbox_from))
        ## Start time
        bbox_start = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), text_start, font=font, align="left"
        )
        position_start = Helper.position(
            bbox_start, content_width, content_height / 6, spacing
        )
        position_start = (
            spacing + bbox_from[2] - bbox_from[0],
            content_height / 2 + position_start[1] - bbox_start[1] + spacing,
        )
        draw.text(position_start, text_start, fill="black", font=font, align="left")
        self.debug_boxes.append((position_start, bbox_start))
        ## To
        bbox_to = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), "To: ", font=font, align="left"
        )
        position_to = Helper.position(
            bbox_to, content_width, content_height / 4, spacing
        )
        position_to = (
            spacing,
            content_height / 3 * 2 + position_to[1] - bbox_to[1] + spacing,
        )
        draw.text(position_to, "To: ", fill="black", font=font, align="left")
        self.debug_boxes.append((position_to, bbox_to))
        ## End time
        bbox_end = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox(
            (0, 0), text_end, font=font, align="left"
        )
        position_end = Helper.position(
            bbox_end, content_width, content_height / 4, spacing
        )
        position_end = (
            spacing + bbox_from[2] - bbox_from[0],
            content_height / 3 * 2 + position_end[1] - bbox_end[1] + spacing,
        )
        draw.text(position_end, text_end, fill="black", font=font, align="left")
        self.debug_boxes.append((position_end, bbox_end))

        return image

    def _draw_summary(self, image, time_entries):
        draw = ImageDraw.Draw(image)

        spacing = self.margin
        content_width = self.width - spacing * 2
        content_height = (self.height - spacing * 2) / 10

        summary = {}
        total_duration = 0
        for entry in time_entries:
            project_id = entry.get("project_id")
            if not project_id:
                continue
            if entry.get("duration", -1) < 0:
                continue
            summary[project_id] = summary.get(project_id, 0) + entry.get("duration", 0)
            total_duration += entry.get("duration", 0)
        summary = sorted(summary.items(), key=lambda x: x[1], reverse=True)

        if total_duration == 0:
            return image

        current_x = spacing
        for project_id, duration in summary:
            length = content_width * (duration / total_duration)
            draw.rectangle(
                [
                    (current_x, self.height - spacing - content_height),
                    (
                        current_x + length,
                        self.height - spacing,
                    ),
                ],
                fill=self._get_project_details(project_id).get("color", "#000000"),
            )
            current_x += length

        return image

    def _draw_api_invalid(self, image):
        draw = ImageDraw.Draw(image)
        font = Helper.load_font("fonts/roboto_mono/static/RobotoMono-Regular.ttf", 24)

        text = "Toggl API key is invalid"
        text_size = draw.textbbox((0, 0), text, font=font)

        try:
            # Load error icon
            icon_path = "icons/error_72dp.png"
            error_icon = Image.open(icon_path).convert("RGBA")
            transparent_bg = Image.new("RGBA", error_icon.size, (255, 255, 255, 0))
            error_icon = Image.alpha_composite(transparent_bg, error_icon)

            # Icon positioning
            spacing = 20
            combined_height = error_icon.height + spacing + text_size[3]
            start_y = (self.height - combined_height) // 2
            icon_x = (self.width - error_icon.width) // 2
            icon_y = start_y
            image.paste(error_icon, (icon_x, icon_y))

            # Text positioning
            text_x = (self.width - text_size[2]) // 2
            text_y = start_y + error_icon.height + spacing

        except Exception as e:
            print(f"Error loading icon: {e}")
            # Fallback to center text only if icon fails
            text_x = (self.width - text_size[2]) // 2
            text_y = (self.height - text_size[3]) // 2

        draw.text((text_x, text_y), text, fill="black", font=font)

        return image

    def _draw_border(self, image):

        return super()._draw_border(image)

    def _draw_debug(self, image):
        draw = ImageDraw.Draw(image)
        spacing = self.margin + self.padding
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
