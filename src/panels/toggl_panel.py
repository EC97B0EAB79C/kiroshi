from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper
from src.palette import *
from datetime import datetime, timezone

import src.api.toggl as TogglAPI


class TogglPanel(Panel):
    def __init__(self, width, height, settings=None, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

        # Toggl API settings
        self.auth = f"{settings.get('api_key', '')}:api_token"
        self.api_key_status = TogglAPI.verify_api_key(self.auth)

        # Margin, padding and border settings
        self.padding = settings.get("padding", 10)

        # Toggl Data
        self.projects = TogglAPI.get_workspace_projects(self.auth, self.api_key_status)

    def _draw(self, image):
        if not self.api_key_status:
            image = self._draw_api_invalid(image)
            return image

        current_entry = TogglAPI.get_current_time_entry(self.auth)
        current_project = self._get_project_details(
            current_entry.get("project_id"), current_entry.get("workspace_id")
        )
        print(
            f"{current_entry.get('description')}·{current_project.get('name')}/{current_project.get('color')}"
        )
        start_time = datetime.fromisoformat(current_entry.get("start"))
        local_tz = datetime.now().astimezone().tzinfo
        start_time_local = start_time.astimezone(local_tz)
        formatted_time = start_time_local.strftime("%Y-%m-%d %H:%M:%S")

        print(f"{formatted_time}")

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
