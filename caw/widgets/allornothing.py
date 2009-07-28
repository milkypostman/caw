import caw

class AllOrNothing(caw.Widget):
    def __init__(self, *widgets):
        super(AllOrNothing, self).__init__()
        self.widgets = widgets

    def init(self, parent):
        self.parent = parent
        self.varcount = 0
        self.default_total = 0
        for w in self.widgets:
            if w.width_hint < 0:
                self.varcount += 1
                self.default_total = -float('inf')
            w.init(parent)

    def _get_width_hint(self):
        total = self.default_total
        for w in self.widgets:
            mw = w.width_hint
            if mw == 0:
                return 0

            total += mw

        return total

    width_hint = property(_get_width_hint)

    def _get_parent(self):
        return self._parent

    def _set_parent(self, parent):
        self._parent = parent
        for w in self.widgets:
            w.parent = parent

    parent = property(_get_parent, _set_parent)

    def button_press(self, button, x):
        print "ALL OR NOTHING BUTTON"
        left = 0
        right = len(self.widgets)
        while left < right:
            mid = (left + right) / 2
            w = self.widgets[mid]
            if x < w.x:
                right = mid
            elif x >= w.x+w.width:
                left = mid+1
            else:
                w.button_press(button, x)
                break

    def draw(self):
        varspace = self.width
        for w in self.widgets:
            ww = w.width_hint
            if ww == 0:
                return

            if ww > 0:
                varspace -= ww

        if self.varcount > 0:
            varspace /= self.varcount

        curx = self.x
        for w in self.widgets:
            ww = w.width_hint
            if ww < 0:
                varspace = ww
            w.x = curx
            w.width = ww
            w.draw()
            curx += ww

