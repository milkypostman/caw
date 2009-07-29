import caw.widget
import time

class Clock(caw.widget.Widget):
    def __init__(self, format="%Y.%m.%d %H:%M:%S", color=None):
        super(Clock, self).__init__()
        self.format = format
        self.color = color

    def init(self, parent):
        super(Clock, self).init(parent)
        self.update()

    def update(self):
        self.text = time.strftime(self.format)
        self.width_hint = self.parent.text_width(self.text)
        self.parent.update();
        self.parent.schedule(1, self.update)

    def draw(self):
        self.parent.draw_text(self.text, color=self.color)

