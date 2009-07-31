import caw.widget
import operator

try:
    import alsaaudio
except ImportError:
    alsaaudio = None

import ossaudiodev

class Volume(caw.widget.Widget):
    def __init__(self, device='Master', med=30, high=70, step=1, driver='alsa', show_percent=False, **kwargs):
        super(Volume, self).__init__(**kwargs)
        self.device = device
        self.med = med
        self.high = high
        self.step = step
        self.show_percent = show_percent
        if driver == 'alsa' and alsaaudio is None :
            driver = 'oss'

        self.driver = driver

        # set default button arguments
        self.buttons[4] = self.buttons.get(4, self.button4)
        self.buttons[5] = self.buttons.get(5, self.button5)

    def init(self, parent):
        super(Volume, self).init(parent)
        getattr(self, '_init_' + self.driver)()
        self.min = 0
        self.max = 100

        self.fglow = 0xcccccc
        self.fgmed = 0x00cc00
        self.fghigh = 0xcc0000
        self._update()

    def _init_oss(self):
        self.device_mask = getattr(ossaudiodev, "SOUND_MIXER_%s" % self.device.upper(), None)
        if self.device_mask is None:
            self.device_mask = ossaudiodev["SOUND_MIXER_VOLUME"]

        self.mixer = ossaudiodev.openmixer()

    def _init_alsa(self):
        self.mixer = alsaaudio.Mixer(self.device)
        self.min, self.max = self.mixer.getrange()

    def _update_alsa(self):
        vol = alsaaudio.Mixer(self.device).getvolume()
        self.current = reduce(operator.add, vol) / len(vol)
        self.percent = round((float(self.current) / self.max) * 100)
        self._update_width()

    def _update_oss(self):
        vol = self.mixer.get(self.device_mask)
        self.current = reduce(operator.add, vol) / len(vol)
        self.percent = round((float(self.current) / self.max) * 100)
        self._update_width()

    def _update_width(self):
        if self.show_percent:
            self.width_hint = self.parent.text_width("%d%%" % self.percent)
        else:
            self.width_hint = self.parent.text_width("%d" % self.percent)

    def _update(self):
        getattr(self, "_update_" + self.driver)()
        self._update_width()
        self.parent.update(self)
        self.parent.schedule(2, self._update)

    def draw(self):
        fg = self.fglow
        if self.percent > self.high:
            fg = self.fghigh
        elif self.percent > self.med:
            fg = self.fgmed

        self.parent.draw_text("%d" % self.percent, fg, self.x)
        if self.show_percent:
            self.parent.draw_text("%", fg)

    def _set_alsa(self, value):
        alsaaudio.Mixer(self.device).setvolume(value)

    def _set_oss(self, value):
        self.mixer.set(self.device_mask, (value,value))

    def redraw(self):
        if self.width_hint == self.width:
            #print "immediate redraw"
            self.parent.clear(self.x, 0, self.width, self.parent.height)
            self.draw()
        else:
            #print "parent redraw"
            self.parent.redraw()

    def button5(self, x):
        newval =  max(self.current-self.step, self.min)
        getattr(self, "_set_" + self.driver)(newval)
        getattr(self, "_update_" + self.driver)()
        self.redraw()

    def button4(self, x):
        newval =  min(self.current+self.step, self.max)
        getattr(self, "_set_" + self.driver)(newval)
        getattr(self, "_update_" + self.driver)()
        self.redraw()

