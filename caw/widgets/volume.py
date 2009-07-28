import caw
import operator

try:
    import alsaaudio
except ImportError:
    alsaaudio = None

import ossaudiodev

class Volume(caw.Widget):
    def __init__(self, device='Master', med=30, high=70, step=1, driver='alsa', percent_color=None, **kwargs):
        super(Volume, self).__init__(**kwargs)
        self.device = device
        self.med = med
        self.high = high
        self.step = step
        self.percent_color = percent_color
        if driver == 'alsa' and alsaaudio is None :
            driver = 'oss'

        self.driver = driver

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

    def _update_oss(self):
        vol = self.mixer.get(self.device_mask)
        self.current = reduce(operator.add, vol) / len(vol)
        self.percent = round((float(self.current) / self.max) * 100)

    def _update(self):
        getattr(self, "_update_" + self.driver)()
        self.width_hint = self.parent.text_width("%d%%" % self.percent)
        self.parent.schedule(2, self._update)

    def draw(self):
        fg = self.fglow
        if self.percent > self.high:
            fg = self.fghigh
        elif self.percent > self.med:
            fg = self.fgmed

        self.parent.draw_text("%d" % self.percent, fg, self.x)
        self.parent.draw_text("%", self.percent_color)

    def _set_alsa(self, value):
        alsaaudio.Mixer(self.device).setvolume(value)

    def _set_oss(self, value):
        self.mixer.set(self.device_mask, (value,value))

    def button_press(self, button, x):
        if button == 5:
            newval =  max(self.current-self.step, self.min)
            getattr(self, "_set_" + self.driver)(newval)
            getattr(self, "_update_" + self.driver)()
            self.parent.redraw()
        elif button == 4:
            newval =  min(self.current+self.step, self.max)
            getattr(self, "_set_" + self.driver)(newval)
            getattr(self, "_update_" + self.driver)()
            self.parent.redraw()

