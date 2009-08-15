import caw.widget
import collections
import time
import math

class Net(caw.widget.Widget):
    """
    Net widget for getting statistics of various interfaces.

    This is an example of a widget that has a global updator rather than a single one.  In other
    words, the class functions update all interfaces and then set the values of class instances
    based on what interface has been updated.  This way the file is read once per update rather
    than mulitple times per update.

    Parameters
    ----------

    iface : network interface to monitor

    stat : stat to show [ up | down ]

    fg : alias for normal_fg

    normal_fg : normal foreground

    medium_fg : color when network speed exceeds 'medium'

    high_fg : color when network speed exceeds 'high'
    """

    _initialized = False
    _widgets = collections.defaultdict(list)

    def __init__(self, iface='eth0', stat='down', fg=None, medium_fg=0xffff00, high_fg=0xff0000, medium=100, high=500, **kwargs):
        super(Net, self).__init__(**kwargs)
        self.iface = iface
        self.stat = stat
        self.normal_fg = kwargs.get('normal_fg', fg)
        self.medium_fg = medium_fg
        self.high_fg = high_fg
        self.medium = medium
        self.high = high
        self._data = collections.defaultdict(int)

    def init(self, parent):
        super(Net, self).init(parent)

        # intialize our class cache updator
        if not Net._initialized:
            Net._clsinit(self.parent)

        self.width_hint = self.parent.text_width("0")

        Net._widgets[self.iface].append(self)

    @classmethod
    def _clsinit(cls, parent):
        cls._file = open('/proc/net/dev', 'r')
        cls._cache = dict(all=dict(up=0, down=0))
        cls._parent = parent

        cls._update()

        cls._initialized = True

    @classmethod
    def _update(cls, timeout=3):
        cls._file.seek(0)
        i = 0
        cache = cls._cache
        for line in cls._file:
            split = line.split(':')
            if len(split) < 2: continue

            net = split[0].strip()

            if not (net.startswith('wifi') or net.startswith('lo')):
                data = split[1].split()
                rx = int(data[0])
                tx = int(data[8])

                if not net in cache:
                    cache[net] = dict(time=time.time(), down=0, up=0)
                else:
                    interval = time.time() - cache[net]['time']
                    cache[net]['time'] = time.time()

                    down = (rx - cache[net]['rx'])/interval
                    up = (tx - cache[net]['tx']) / interval

                    cache[net]['down'] = math.floor(down/1025*10)/10
                    cache[net]['up'] = math.floor(up/1025*10)/10

                cache[net]['rx'] = rx
                cache[net]['tx'] = tx

                cache['all']['down'] += cache[net]['down']
                cache['all']['up'] += cache[net]['up']

                for w in cls._widgets[net]:
                    w.data = cache[net]

        cls._parent.schedule(timeout, cls._update)

    def _get_data(self):
        return self._data

    def _set_data(self, data):
        self._data = data
        self.width_hint = self.parent.text_width("%d" % self._data[self.stat])

    data = property(_get_data, _set_data)

    def draw(self):
        val = self._data[self.stat]
        fg = self.normal_fg
        if val > self.high:
            fg = self.high_fg
        elif val > self.medium:
            fg = self.medium_fg

        self.parent.draw_text("%d" % self._data[self.stat], fg=fg)



