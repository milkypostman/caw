import caw
import re

class Battery(caw.Widget):
    def __init__(self, battery="BAT0", warn_color='#e7e700', low_color='#d70000', fg_color=None ):
        super(Battery, self).__init__()
        self.battery = battery

        self.re = re.compile('(.*):\W*(.*)')
        self.symbols = {'charging': '^', 'discharging': '_', 'charged': '='}
        self.fg_color = fg_color
        self.low_color = low_color
        self.warn_color = warn_color

    def init(self, parent):
        super(Battery, self).init(parent)
        self.file = open('/proc/acpi/battery/%s/state' %self.battery, 'r')
        self._loadinfo()
        self.update()

    def _parse(self, fileobj):
        data = {}
        for line in fileobj:
            m = self.re.match(line)
            if m:
                data[m.group(1)] = m.group(2)
        return data

    def _loadinfo(self):
        file = open('/proc/acpi/battery/%s/info' %self.battery, 'r')
        data = self._parse(file)

        self.capacity = int(data["last full capacity"].split()[0])
        self.warn = int(data["design capacity warning"].split()[0])
        self.low = int(data["design capacity low"].split()[0])

    def update(self):
        self.file.seek(0)
        try:
            data = self.data = self._parse(self.file)
        except IOError:
            self.parent.schedule(60, self.update)
            return

        state = data['charging state']
        remaining = int(data['remaining capacity'].split()[0])
        if state == 'discharging':
            rate = int(data['present rate'].split()[0])
            timeleft = remaining / float(rate)
            hoursleft = int(timeleft)
            minutesleft = (timeleft - hoursleft) * 60
        else:
            hoursleft = 0
            minutesleft = 0

        symbol = self.symbols[state]
        self.width_hint = self.parent.text_width("%2d:%02d %s%2d%s" % (hoursleft, minutesleft, symbol, float(remaining)/self.capacity * 100, symbol))
        self.parent.schedule(60, self.update)

    def draw(self):
        data = self.data
        state = data['charging state']
        remaining = int(data['remaining capacity'].split()[0])
        if state == 'discharging':
            rate = int(data['present rate'].split()[0])
            timeleft = remaining / float(rate)
            hoursleft = int(timeleft)
            minutesleft = (timeleft - hoursleft) * 60
        else:
            hoursleft = 0
            minutesleft = 0

        if remaining < self.warn:
            color = self.warn_color 
        elif remaining < self.low:
            color = self.low_color
        else:
            color = self.fg_color

        symbol = self.symbols[state]
        self.parent.draw_text("%2d:%02d %s%2d%s" % (hoursleft, minutesleft, symbol, float(remaining)/self.capacity * 100, symbol) , color)



