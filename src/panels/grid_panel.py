from PIL import ImageDraw

from src.panel import Panel


class GridPanel(Panel):
    """Layout panel. Puts child panels in a grid of rows x cols cells."""

    def __init__(self, width=800, height=480, settings=None, debug=False, panels=(), rows=1, cols=1):
        super().__init__(width, height, settings, debug)
        self.rows = rows
        self.cols = cols
        self.panels = list(panels)[: rows * cols]
        self._set_panel_size()

    def needs_refresh(self) -> bool:
        # Ask all children, so each child resets its own flag
        children = [panel.needs_refresh() for panel in self.panels if panel]
        return super().needs_refresh() or any(children)

    def set_size(self, width, height):
        super().set_size(width, height)
        self._set_panel_size()

    def get_panel_size(self):
        return (
            (self.width - self.margin * 2) // self.cols - self.padding * 2,
            (self.height - self.margin * 2) // self.rows - self.padding * 2,
        )

    def _cell_origin(self, index):
        row, col = divmod(index, self.cols)
        return (
            self.margin + col * (self.width - self.margin * 2) // self.cols + self.padding,
            self.margin + row * (self.height - self.margin * 2) // self.rows + self.padding,
        )

    def _set_panel_size(self):
        for panel in self.panels:
            if panel:
                panel.set_size(*self.get_panel_size())

    def _draw(self, image):
        for index, panel in enumerate(self.panels):
            if panel:
                image.paste(panel.draw(), self._cell_origin(index))

        return super()._draw(image)

    def _draw_border(self, image):
        draw = ImageDraw.Draw(image)
        line = {"fill": self.border_color, "width": self.border_width}
        for col in range(1, self.cols):
            x = self.margin + col * (self.width - self.margin * 2) // self.cols
            draw.line([(x, self.margin), (x, self.height - self.margin)], **line)
        for row in range(1, self.rows):
            y = self.margin + row * (self.height - self.margin * 2) // self.rows
            draw.line([(self.margin, y), (self.width - self.margin, y)], **line)

        return super()._draw_border(image)

    def _draw_debug(self, image):
        draw = ImageDraw.Draw(image)
        width, height = self.get_panel_size()
        for index in range(self.rows * self.cols):
            x, y = self._cell_origin(index)
            draw.rectangle([(x, y), (x + width, y + height)], outline="blue", width=2)

        return super()._draw_debug(image)
