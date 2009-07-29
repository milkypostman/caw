import caw.widget
import collections
import re
import itertools
import operator
import math

class CPU(caw.widget.Widget):
    """
    CPU widget for getting statistics of processor time

    This is an example of a widget that has a global updator rather than a single one.  In other
    words, the class functions update all interfaces and then set the values of class instances
    based on what interface has been updated.  This way the file is read once per update rather
    than mulitple times per update.
    """

    _initialized = False
    _widgets = collections.defaultdict(list)

    def __init__(self, cpu=0, fg_color=None, med_color=0xffff00, high_color=0xff0000, med_threshold=40, high_threshold=80, show_percent=False):
        super(CPU, self).__init__()
        self.cpu = cpu
        self.fg_color = fg_color
        self.med_color = med_color
        self.high_color = high_color
        self.med_threshold = med_threshold
        self.high_threshold = high_threshold
        self.show_percent = show_percent

    def init(self, parent):
        super(CPU, self).init(parent)
        self.data = collections.defaultdict(int)

        if not CPU._initialized:
            CPU._clsinit(self.parent)

        CPU._widgets[self.cpu].append(self)

    @classmethod
    def _clsinit(cls, parent):
        cls._re = re.compile('^cpu')
        cls._sep = re.compile('[ *]*')
        cls._file = open('/proc/stat', 'r')
        cls._cache = {}
        cls._parent = parent

        cls._update(0)

        cls._initialized = True

    @classmethod
    def _update(cls, timeout=3):
        cls._file.seek(0)
        i = 0
        cache = cls._cache
        for line in cls._file:
            if cls._re.match(line):
                info = cls._sep.split(line)
                active = reduce(operator.add, itertools.imap(int, info[1:4]))
                total = active + int(info[4])

                try:
                    difftotal = total - cache[i]['total']
                    diffactive = active - cache[i]['active']
                    cache[i]['usage'] = math.floor((float(diffactive) / difftotal) * 100)
                except KeyError:
                    cache[i] = {}
                except ZeroDivisionError:
                    cache[i]['usage'] = 0

                cache[i]['total'] = total
                cache[i]['active'] = active

                for w in cls._widgets.get(i, []):
                    w.data = cache[i]
                    w.parent.update()

                i += 1

        cls._parent.schedule(timeout, cls._update)

    def _get_data(self):
        return self._data

    def _set_data(self, data):
        self._data = data
        if self.show_percent:
            self.width_hint = self.parent.text_width("%d%%" % self._data['usage'])
        else:
            self.width_hint = self.parent.text_width("%d" % self._data['usage'])

    data = property(_get_data, _set_data)

    def draw(self):
        val = self._data['usage']
        color = self.fg_color
        if val > self.high_threshold:
            color = self.high_color
        elif val > self.med_threshold:
            color = self.med_color

        if self.show_percent:
            self.parent.draw_text("%d%%" % self._data['usage'], color=color)
        else:
            self.parent.draw_text("%d" % self._data['usage'], color=color)



