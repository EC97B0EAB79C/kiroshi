import os

from PIL import ImageDraw

from src.panel import Panel
import src.helper as Helper
import src.default as Default

import src.api.github as GithubAPI


class GithubPanel(Panel):
    def __init__(self, width, height, settings=None, debug=False):
        super().__init__(width, height, settings, debug)

        # GitHub API settings
        self.username = self.settings.get("username")
        self.github_token = self.settings.get("github_token", os.getenv("GITHUB_TOKEN"))

        self.padding_content = self.settings.get("padding_content", Default.PADDING_CONTENT)

    def _draw(self, image):
        spacing = self.padding + self.margin

        contributions = self.cached_request(
            lambda: GithubAPI.get_github_contributions(self.username, self.github_token)
        )
        if contributions is None:
            image = Helper.invalid_image(
                image, self.width, self.height, Helper.error_text("GitHub error", self.error)
            )
            return super()._draw(image)

        graph_location = (spacing, spacing)
        graph_size = (image.width - spacing * 2, image.height - spacing * 2)
        image = self._draw_graph(image, contributions, graph_location, graph_size)

        return super()._draw(image)

    def _draw_graph(self, image, contributions, graph_location, graph_size):
        draw = ImageDraw.Draw(image)

        box_size = (graph_size[1] - self.padding_content * 6) // 7

        x = graph_location[0] + graph_size[0] - box_size
        for week_contribution in reversed(contributions):
            y = graph_location[1]
            for day_contribution in week_contribution["contributionDays"]:
                draw.rectangle(
                    [(x, y), (x + box_size, y + box_size)],
                    fill=day_contribution["color"],
                    outline="black",
                    width=1,
                )
                y += box_size + self.padding_content
            x -= box_size + self.padding_content
            if x < graph_location[0] - box_size:
                break

        draw.rectangle([(0, 0), (graph_location[0], self.height)], fill="white")
        return Helper.quantize_image(image, self.palette_name).convert("RGB")
