class Widget(object):
    width = 0
    x = 0
    width_hint = 0
    parent = None

    def __init__(self, **kwargs):
        super(Widget, self).__init__()

    def button_press(self, button, x):
        pass

    def init(self, parent):
        self.parent = parent
        pass

    def draw(self):
        pass

