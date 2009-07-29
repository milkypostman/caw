import caw.widget

class Text(caw.widget.Widget):
    def __init__(self, text="undefined", color=None, **kwargs):
        super(Text, self).__init__(**kwargs)
        self.text = text
        self.color = color

    def init(self, parent):
        super(Text, self).init(parent)
        self.width_hint = self.parent.text_width(self.text)

    def draw(self):
        self.parent.draw_text(self.text, self.color, self.x)

