"""Wifi Widget"""
import caw.widget
import os

class Wifi(caw.widget.Widget):
    """Wifi Widget

    Parameters
    ----------

    adapter : the network adapater to watch
    """

    def __init__(self, adapter="ath0", fg=None, **kwargs):
        """Initializes the Wifi widget"""

        super(Wifi, self).__init__(**kwargs)
        self.adapter = adapter

        self.normal_fg = kwargs.get('normal_fg', fg)
        self.width_hint = 0

    def init(self, parent):
        super(Wifi, self).init(parent)
        path = '/sys/class/net/%s/wireless/link' %self.adapter
        if os.path.isfile(path):
            self.file = open(path, 'r')
            self.update()
        else:
            print "Error: path does not exist.", path

    def update(self):
        self.file.seek(0)
        self.data = int(self.file.read())
        self.width_hint = self.parent.text_width(str(self.data))
        self.parent.schedule(5, self.update)

    def draw(self):
        data = self.data
        self.parent.draw_text(str(data) , self.normal_fg)



