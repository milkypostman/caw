import caw.widget

class Text(caw.widget.Widget):
    def __init__(self, text="undefined", fg_color=None, **kwargs):
        super(Text, self).__init__(**kwargs)
        self.text = text
        self.fg_color = fg_color

    def init(self, parent):
        super(Text, self).init(parent)
        self.width_hint = self.parent.text_width(self.text)

    def draw(self):
        self.parent.draw_text(self.text, self.fg_color, self.x)

