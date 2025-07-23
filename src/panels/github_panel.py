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

        graph_location = (spacing, spacing)
        graph_size = (
            image.width - spacing * 2,
            image.height - spacing * 2,
        )

        image = self._draw_graph(image, contributions, graph_location, graph_size)

        return image

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
        return image
