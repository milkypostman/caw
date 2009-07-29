import caw.widget

class Spacer(caw.widget.Widget):
    def __init__(self, width=5, **kwargs):
        super(Spacer, self).__init__(**kwargs)
        self.width_hint = width
