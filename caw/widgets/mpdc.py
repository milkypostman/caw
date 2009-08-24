import caw.widget
import collections
import mpd
import socket

class MPDC(caw.widget.Widget):
    """Widget to display MPD information.

    Parameters
    -----------

    fg : text color of this widget

    play_format : format of the text to display when a song is playing. \
            See the list of possible replacement strings below. \
            (default "%(artist)s - %(title)s")

        valid substitution labels: \

                artist : artist name

                title : song title

                album : album name

                file : filename of the song

                track : current track / total tracks

                date : date of the song

                elapsed_min : minutes elapsed thus far

                elapsed_sec : seconds into the minute elapsed

                total_min : minutes of length

                total_sec : seconds into the minute for total length

    pause_format : format of the text to display when paused. \
            The same formatting strings as 'play_format' are allowed. \
            (default "paused")

    stop_text : text to display when mpd is stopped (default '')

    hostname : hostname to connect to

    port : port to connect to

    There are stuff
    """

    _initialized = False
    _widgets = collections.defaultdict(list)
    _mpd = {}

    def __init__(self, fg=None, play_format="%(artist)s - %(title)s", pause_format='pause', stop_text='', hostname='localhost', port=6600, **kwargs):
        super(MPDC, self).__init__(**kwargs)

        self._data = None

        #constructor initialization
        self.play_format = play_format
        self.hostname = hostname
        self.port = port
        self.fg = fg
        self._mpd = None
        self.pause_format=pause_format
        self.stop_text=stop_text

        self.text = ''
        self.width_hint = 0

        # width_hint tells the parent how much space we want/need.  
        # (-1 means as much as possible)
        self.width_hint = 0

    def init(self, parent):
        super(MPDC, self).init(parent)

        if not MPDC._initialized:
            MPDC._clsinit(self.parent)

        hostname, port = self.hostname, self.port
        if not (hostname, port) in MPDC._mpd:
            MPDC._mpd[(hostname, port)] = mpd.MPDClient()

        self._widgets[(hostname, port)].append(self)

    @classmethod
    def _clsinit(cls, parent):
        cls.parent = parent
        cls._initialized = True
        cls._update(0)

    @classmethod
    def _update(cls, timeout=1):
        for (hostname, port) in cls._mpd:
            #print (hostname, port)
            cli = cls._mpd[(hostname, port)]

            if cli._sock is None:
                try:
                    cli.connect(hostname, port)
                except socket.error:
                    continue

            try:
                data = {}
                status = cli.status()
                data.update(status)
                data.update(cli.currentsong())
                if status['state'] in ('play', 'pause'):
                    elapsed,total = map(int, status['time'].split(':'))
                    data['elapsed_min'] = elapsed / 60
                    data['elapsed_sec'] = elapsed - (data['elapsed_min'] * 60)
                    data['total_min'] = total / 60
                    data['total_sec'] = total - (data['total_min'] * 60)

            except mpd.ConnectionError:
                data = None
                cli.disconnect()

            for widget in cls._widgets[(hostname, port)]:
                widget.data = data

        cls.parent.schedule(timeout, cls._update)

    def _connect(self):
        try:
            self._mpd.connect(self.hostname, self.port)
        except socket.error:
            return False

        return True 

    def button1(self, _):
        try:
            MPDC._mpd[(self.hostname, self.port)].previous()
        except mpd.ConnectionError:
            pass

    def button2(self, _):
        try:
            client = MPDC._mpd[(self.hostname, self.port)]
            state = client.status()['state']
            if state == 'play':
                client.pause()
            else:
                client.play()
        except mpd.ConnectionError:
            pass

    def button3(self, _):
        try:
            MPDC._mpd[(self.hostname, self.port)].next()
        except mpd.ConnectionError:
            pass

    def _get_data(self):
        return self._data

    def _set_data(self, data):
        self._data = data
        if data is None:
            self.text = ''
        else:
            state = data['state']
            if state == 'play':
                self.text = self.play_format % data
            elif state == 'pause':
                self.text = self.pause_format % data
            else:
                self.text = self.stop_text
        self.width_hint = self.parent.text_width(self.text)
        self.parent.update()

    data = property(_get_data, _set_data)

    def draw(self):
        # draw the text for this widget
        self.parent.draw_text(self.text, self.fg)





