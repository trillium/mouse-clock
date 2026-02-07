"""Mock canvas for testing rendering code without Talon runtime."""


class MockStyle:
    FILL = "fill"
    STROKE = "stroke"


class MockPaint:
    Style = MockStyle

    def __init__(self):
        self.color = "000000ff"
        self.style = MockStyle.STROKE
        self.stroke_width = 2
        self.textsize = 16

    def snapshot(self):
        return {
            "color": self.color,
            "style": self.style,
            "stroke_width": self.stroke_width,
            "textsize": self.textsize,
        }

    def measure_text(self, text):
        """Approximate text measurement."""
        return (len(text) * self.textsize * 0.6, self.textsize)


class MockRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class MockCanvas:
    """Records all draw calls for assertion in tests."""

    def __init__(self, width=1920, height=1080):
        self.drawings = []
        self.rect = MockRect(0, 0, width, height)
        self.paint = MockPaint()

    def draw_circle(self, x, y, r):
        self.drawings.append(("circle", x, y, r, self.paint.snapshot()))

    def draw_line(self, x1, y1, x2, y2):
        self.drawings.append(("line", x1, y1, x2, y2, self.paint.snapshot()))

    def draw_text(self, text, x, y):
        self.drawings.append(("text", text, x, y, self.paint.snapshot()))

    def draw_rect(self, rect):
        self.drawings.append(("rect", rect, self.paint.snapshot()))

    def save(self):
        pass

    def restore(self):
        pass

    def translate(self, x, y):
        pass

    def scale(self, sx, sy):
        pass

    def circles(self):
        """Get all circle draw calls."""
        return [d for d in self.drawings if d[0] == "circle"]

    def lines(self):
        """Get all line draw calls."""
        return [d for d in self.drawings if d[0] == "line"]

    def texts(self):
        """Get all text draw calls."""
        return [d for d in self.drawings if d[0] == "text"]
