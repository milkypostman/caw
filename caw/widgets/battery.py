import caw.widget
import re

class Battery(caw.widget.Widget):
    """

    Parameters
    ------------

    format : alias for all formats: charging_format, discharging_format, charged_format \
            (default "%(hours remaining)d:%(minutes remaining)02d %(symbol)s%(percent remaining)02d%(symbol)s")

        String format replacement keys are provided by the system and can be found by look at items in
        ''/proc/acpi/battery/BAT0/info'' and ''/proc/acpi/battery/BAT0/state''.
        (e.g. cat /proc/acpi/battery/BAT0/info /proc/acpi/battery/BAT0/state)

        This module also provides the following additional information:

            hours remaining : the hours remaining until fully discharged / charged

            minutes remaining : the minutes past the hour remaining until fully discharged / charged

            percent remaining : the percentage of battery life remaining

            symbol : a symbol representing the current state (charging : ^, discharging : _, charged : =)


    charging_format : the format to used when charging (see 'format' for string replacment keys)

    discharging_format : the format to use when discharging (see 'format' for string replacment keys)

    charged_format : the format to used when the battery is charged (see 'format' for string replacment keys)
    """

    def __init__(self, battery="BAT0", fg=None, warn_fg=0xe7e700, low_fg=0xd70000, format="%(hours remaining)d:%(minutes remaining)02d %(symbol)s%(percent remaining)02d%(symbol)s", **kwargs):
        super(Battery, self).__init__(**kwargs)
        self.battery = battery

        self.re = re.compile('(.*):\W*(.*)')
        self.symbols = {'charging': '^', 'discharging': '_', 'charged': '='}
        self.format = dict()
        self.format['charging'] = kwargs.get('charging_format', format)
        self.format['discharging'] = kwargs.get('discharging_format', format)
        self.format['charged'] = kwargs.get('charged_format', format)
        self.normal_fg = kwargs.get('normal_fg', fg)
        self.low_fg = low_fg
        self.warn_fg = warn_fg
        self.data = dict()

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
        data = self.data
        self.data.update(self._parse(file))

        self.capacity = int(data["last full capacity"].split()[0])
        self.warn = int(data["design capacity warning"].split()[0])
        self.low = int(data["design capacity low"].split()[0])

    def update(self):
        self.file.seek(0)
        try:
            data = self.data
            data.update(self._parse(self.file))
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

        elif state == 'charging':
            rate = int(data['present rate'].split()[0])
            timeleft = (self.capacity - remaining) / float(rate)
            hoursleft = int(timeleft)
            minutesleft = (timeleft - hoursleft) * 60
        else:
            hoursleft = 0
            minutesleft = 0

        data['hours remaining'] = hoursleft
        data['minutes remaining'] = minutesleft
        data['percent remaining'] = float(remaining) / self.capacity * 100
        data['symbol'] = self.symbols[state]
        self.text = self.format[state] % data
        self.width_hint = self.parent.text_width(self.text)
        self.parent.schedule(60, self.update)

    def draw(self):
        remaining = int(self.data['remaining capacity'].split()[0])
        if remaining < self.warn:
            color = self.warn_fg 
        elif remaining < self.low:
            color = self.low_fg
        else:
            color = self.normal_fg

        self.parent.draw_text(self.text , color)



