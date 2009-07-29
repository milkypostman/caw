class Widget(object):

    def __init__(self, **kwargs):
        super(Widget, self).__init__()
        self.buttons = {}
        self.x = 0
        self.width = 0
        self.width_hint = 0
        self.parent = None

        for key in kwargs:
            if key.startswith('button') and callable(kwargs[key]):
                try:
                    button = int(key[6:])
                    self.buttons[button] = kwargs[key]
                except ValueError:
                    pass

    def button_press(self, button, x):
        func = self.buttons.get(button)
        if callable(func):
            func(x)

    def init(self, parent):
        self.parent = parent
        pass

    def draw(self):
        pass

