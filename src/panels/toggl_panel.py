import requests
from base64 import b64encode

from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper
from src.palette import *


class TogglPanel(Panel):
    def __init__(self, width, height, settings=None, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

        # Toggl API settings
        self.api_key = settings.get("api_key", "")
        self.api_key_status = self._verify_api_key()
        print(self.api_key_status)

        # Margin, padding and border settings
        self.padding = settings.get("padding", 10)

    def _verify_api_key(self):
        try:
            auth = f"{self.api_key}:api_token"
            data = requests.get(
                "https://api.track.toggl.com/api/v9/me",
                headers={
                    "content-type": "application/json",
                    "Authorization": "Basic %s"
                    % b64encode(auth.encode("ascii")).decode("ascii"),
                },
            )
            return True if data.status_code == 200 else False
        except Exception as e:
            print(f"Error verifying API key: {e}")
            return False

    def _draw(self, image):
        if not self.api_key_status:
            image = self._draw_api_invalid(image)

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
