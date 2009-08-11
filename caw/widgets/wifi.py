import caw.widget
import re
import os

class Wifi(caw.widget.Widget):
    def __init__(self, adapter="ath0", fg_color=None, **kwargs):
        super(Wifi, self).__init__(**kwargs)
        self.adapter = adapter

        self.symbols = {'charging': '^', 'discharging': '_', 'charged': '='}
        self.fg_color = fg_color
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
        self.parent.draw_text(str(data) , self.fg_color)



