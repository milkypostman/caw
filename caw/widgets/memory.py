import caw.widget
import time
import re

class Memory(caw.widget.Widget):
    """ Display memory usage using /proc/meminfo"""
    def __init__(self, fg=None, **kwargs):
        super(Memory, self).__init__(**kwargs)
        self.fg = fg

    def init(self, parent):
        super(Memory, self).init(parent)
        self.update()

    def update(self):
        self.fetch_update_memory()
        self.width_hint = self.parent.text_width(self.text)
        self.parent.update(self);
        self.parent.schedule(1, self.update)

    def draw(self):
        self.parent.draw_text(self.text, fg=self.fg)

    def fetch_update_memory(self):
        memlines = open('/proc/meminfo', 'r').read()
        mfree = re.search('memfree:\s*(\d+)', memlines, re.IGNORECASE)
        mtotal = re.search('memtotal:\s*(\d+)', memlines, re.IGNORECASE)
        if mtotal and mfree:
           usage = ((float(mtotal.group(1)) - int(mfree.group(1)))/int(mtotal.group(1))) * 100
           self.text = "%s%%"%int(usage)
        else:
           self.text = 'n/a'
