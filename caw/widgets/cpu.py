import caw
import collections
import re
import itertools
import operator
import math

class CPU(caw.Widget):
    _initialized = False
    _widgets = collections.defaultdict(list)

    def __init__(self, cpu=0, fg_color=None, med_color=0xffff00, high_color=0xff0000, med_threshold=40, high_threshold=80, percent_color=None):
        super(CPU, self).__init__()
        self.cpu = cpu
        self.fg_color = fg_color
        self.med_color = med_color
        self.high_color = high_color
        self.med_threshold = med_threshold
        self.high_threshold = high_threshold
        self.percent_color = percent_color

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
        for line in cls._file:
            if cls._re.match(line):
                info = cls._sep.split(line)
                active = reduce(operator.add, itertools.imap(int, info[1:4]))
                total = active + int(info[4])

                try:
                    difftotal = total - cls._cache[i]['total']
                    diffactive = active - cls._cache[i]['active']
                    cls._cache[i]['usage'] = math.floor((float(diffactive) / difftotal) * 100)
                except KeyError:
                    cls._cache[i] = {}
                except ZeroDivisionError:
                    cls._cache[i]['usage'] = 0

                cls._cache[i]['total'] = total
                cls._cache[i]['active'] = active

                for w in cls._widgets.get(i, []):
                    w.data = cls._cache[i]
                    w.parent.update()

                i += 1

        cls._parent.schedule(timeout, cls._update)

    def _get_data(self):
        return self._data

    def _set_data(self, data):
        self._data = data
        self.width_hint = self.parent.text_width("%d%%" % self._data['usage'])

    data = property(_get_data, _set_data)

    def draw(self):
        val = self._data['usage']
        color = self.fg_color
        if val > self.high_threshold:
            color = self.high_color
        elif val > self.med_threshold:
            color = self.med_color
        self.parent.draw_text("%d" % self._data['usage'], color=color)
        self.parent.draw_text("%", color=self.percent_color)



