from PIL import Image, ImageDraw, ImageFont

from src.panel import Panel
import src.helper as Helper
from src.palette import *

import src.api.github as GithubAPI


class GithubPanel(Panel):
    def __init__(self, width, height, settings, DEBUG=False):
        super().__init__(width, height, settings, DEBUG)

        # Text settings
        self.font = settings.get("font")
        self.font_size = settings.get("font_size", 10)

        # GitHub API settings
        self.username = settings.get("username")
        self.github_token = settings.get("github_token")

        # Margin, padding and border settings
        self.padding = settings.get("padding", 5)

    def _draw(self, image):
        draw = ImageDraw.Draw(image)

        spacing = self.padding + self.margin

        contributions = GithubAPI.get_github_contributions(
            self.username, self.github_token
        )

        if contributions is None:
            image = self._draw_api_invalid(image)
            return super()._draw(image)

        graph_location = (spacing, spacing)
        graph_size = (
            image.width - spacing * 2,
            image.height - spacing * 2,
        )

        image = self._draw_graph(image, contributions, graph_location, graph_size)

        return super()._draw(image)

    def _draw_graph(self, image, contributions, graph_location, graph_size):
        draw = ImageDraw.Draw(image)

        box_size = (graph_size[1] - self.padding * 6) // 7

        box_location = (graph_location[0] + graph_size[0] - box_size, graph_location[1])
        for week_contribution in reversed(contributions):
            for day_contribution in week_contribution["contributionDays"]:
                draw.rectangle(
                    [
                        box_location,
                        (box_location[0] + box_size, box_location[1] + box_size),
                    ],
                    fill=day_contribution["color"],
                    outline="black",
                    width=1,
                )
                box_location = (
                    box_location[0],
                    box_location[1] + box_size + self.padding,
                )
            box_location = (
                box_location[0] - box_size - self.padding,
                graph_location[1],
            )
            if box_location[0] < graph_location[0] - box_size:
                break

        draw.rectangle(
            [(0, 0), (graph_location[0], self.height)],
            fill="white",
        )
        return Helper.quantize_image(image, self.palette_name)

    def _draw_api_invalid(self, image):
        draw = ImageDraw.Draw(image)
        font = Helper.load_font("fonts/roboto_mono/static/RobotoMono-Regular.ttf", 24)

        text = "GitHub API Error:\nInvalid Username or Token"
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

        draw.text((text_x, text_y), text, fill="black", font=font, align="center")

        return image
