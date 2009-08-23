import caw.widget
import urllib
import time
import thread
import logging
log = logging.getLogger('caw.weather')

try:
    import xml.etree.ElementTree as ElementTree
except ImportError:
    import elementtree.ElementTree as ElementTree

WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?p=%s&u=%s'
WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'

class Weather(caw.widget.Widget):
    """Weather Widget

    Parameters
    ------------

    zipcode : location zipcode

    units : units to display (default 'f')

    hot_fg : hot foreground color

    cold_fg : cold foreground color

    threshold : temperature threshold
    """

    def __init__(self, zipcode=52245, units='f', hot_fg=0xc51102, cold_fg=0x3a4ebe, show_units=True, threshold=60, **kwargs):
        super(Weather, self).__init__(**kwargs)
        self.zipcode = zipcode
        self.available = False
        self.data = {}
        self.fg = None
        self.hot_fg = hot_fg
        self.cold_fg = cold_fg
        self.threshold = threshold
        self.show_units = show_units
        self.units = units

    def init(self, parent):
        super(Weather, self).init(parent)

        thread.start_new_thread(self.update, ())
        self.data['temp'] = 'n/a'
        self.data['units'] = ''
        self.width_hint = self.parent.text_width(self.data['temp'])

    def update(self):
        while True:
            log.debug("updating...")
            url = WEATHER_URL % (self.zipcode, self.units)
            try:
                log.debug("retrieving url...")
                rss = ElementTree.parse(urllib.urlopen(url)).getroot()
            except IOError:
                log.debug("IOError when retrieving url, retrying in 30 seconds.")
                self.data['temp'] = 'n/a'
                self.data['units'] = ''
                self.width_hint = self.parent.text_width(self.data['temp'])
                time.sleep(30)
                continue
            #forecasts = []
            #for element in rss.findall('channel/item/{%s}forecast' % WEATHER_NS):
                #forecasts.append({
                    #'date': element.get('date'),
                    #'low': element.get('low'),
                    #'high': element.get('high'),
                    #'condition': element.get('text')
                #})
            #print url
            self.data['temp'] = rss.find('channel/item/{%s}condition' % WEATHER_NS).get('temp')
            self.data['units'] = rss.find('channel/{%s}units' % WEATHER_NS).get('temperature')

            if int(self.data['temp']) >= self.threshold:
                self.fg = self.hot_fg
            else:
                self.fg = self.cold_fg

            self.parent.update()
            if self.show_units:
                self.width_hint = self.parent.text_width(self.data['temp'] + self.data['units'])
            else:
                self.width_hint = self.parent.text_width(self.data['temp'])

            time.sleep(60)

    def draw(self):
            if self.show_units:
                self.parent.draw_text(self.data['temp'] + self.data['units'], self.fg)
            else:
                self.parent.draw_text(self.data['temp'], self.fg)

