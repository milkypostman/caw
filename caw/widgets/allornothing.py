import caw.widget

class AllOrNothing(caw.widget.Widget):
    """
    AllOrNothing widget which shows all child widgets as long as all of them have some length.

    This is an example of a container widget that basically takes other widgets as an argument.
    Because of the way the taskbar handles widgets, this widget acts like any other widget
    but is assigned a width that is the widths of the children widgets.  If any widget has a
    length of 0 then none of the widgets are shown.  This is for widgets that come and go
    (such as the systray) but other widgets may not want to be displayed during this time.
    """

    def __init__(self, *widgets):
        self.widgets = widgets
        super(AllOrNothing, self).__init__()

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

    def _set_width_hint(self, val):
        pass

    width_hint = property(_get_width_hint, _set_width_hint)

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

