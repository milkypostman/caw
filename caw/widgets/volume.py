import caw.widget
import operator

try:
    import alsaaudio
except ImportError:
    alsaaudio = None

import ossaudiodev

class Volume(caw.widget.Widget):
    """Volume Widgets

    Parameters
    ----------

    device : audio device

    medium : medium volume threshold

    high : high volume threshold

    fg : alias for low_fg

    low_fg : color when volume is lower than 'medium'

    medium_fg : color when the volume widget exceeds 'medium'

    high_fg : color when the volume widget exceeds 'high'

    show_percent : bool denoting whether to show the percentage symbol
    """

    def __init__(self, device='Master', medium=30, high=70, step=1, driver='alsa', show_percent=False, **kwargs):
        super(Volume, self).__init__(**kwargs)
        self.device = device
        self.medium = medium
        self.high = high
        self.step = step

        self.low_fg = kwargs.get('low_fg', 0xcccccc)
        self.med_fg = kwargs.get('med_fg', 0x00cc00)
        self.high_fg = kwargs.get('high_fg', 0xcc0000)

        self.show_percent = show_percent
        if driver == 'alsa' and alsaaudio is None :
            driver = 'oss'

        self.driver = driver

        # set default button arguments
        #self.buttons[4] = self.buttons.get(4, self.button4)
        #self.buttons[5] = self.buttons.get(5, self.button5)

    def init(self, parent):
        super(Volume, self).init(parent)
        getattr(self, '_init_' + self.driver)()
        self.min = 0
        self.max = 100

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
        fg = self.low_fg
        if self.percent > self.high:
            fg = self.high_fg
        elif self.percent > self.medium:
            fg = self.med_fg

        self.parent.draw_text("%d" % self.percent, fg, self.x)
        if self.show_percent:
            self.parent.draw_text("%", fg)

    def _set_alsa(self, value):
        alsaaudio.Mixer(self.device).setvolume(value)

    def _set_oss(self, value):
        self.mixer.set(self.device_mask, (value,value))

    #def redraw(self):
    #    if self.width_hint == self.width:
    #        #print "immediate redraw"
    #        self.parent.clear(self.x, 0, self.width, self.parent.height)
    #        self.draw()
    #    else:
    #        #print "parent redraw"
    #        self.parent.redraw()

    def button5(self, _):
        newval =  max(self.current-self.step, self.min)
        getattr(self, "_set_" + self.driver)(newval)
        getattr(self, "_update_" + self.driver)()
        self.parent.update(self)

    def button4(self, _):
        newval =  min(self.current+self.step, self.max)
        getattr(self, "_set_" + self.driver)(newval)
        getattr(self, "_update_" + self.driver)()
        self.parent.update(self)

