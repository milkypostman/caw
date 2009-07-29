import caw.widget

class Spacer(caw.widget.Widget):
    def __init__(self, width=5):
        super(Spacer, self).__init__()
        self.width_hint = width
