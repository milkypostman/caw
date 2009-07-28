import caw
import xcb
import struct

class Desktop(caw.Widget):
    def __init__(self, current_fg=None, fg=None, showall=False):
        self.desktops = []
        self.current = 0
        self.fg = fg
        self.current_fg = current_fg
        self.fg = fg
        self.showall = showall

    def init(self, parent):
        super(Desktop, self).init(parent)
        a = self.parent.get_atoms([
            "_NET_CURRENT_DESKTOP",
            "_NET_WM_DESKTOP",
            "_NET_DESKTOP_NAMES",
            "UTF8_STRING",
            "_NET_NUMBER_OF_DESKTOPS"])

        for key,val in a.iteritems():
            setattr(self, key, val)

        self.parent.atoms[self._NET_WM_DESKTOP].append(self._update)
        self.parent.atoms[self._NET_CURRENT_DESKTOP].append(self._update)
        self.parent.atoms[self._NET_DESKTOP_NAMES].append(self._get_desktops)
        self.parent.atoms[self._NET_NUMBER_OF_DESKTOPS].append(self._get_desktops)
        self._get_desktops()
        #if self.fg is None:
        #    self.fg = self.parent.fg
        #if self.current_fg is None:
        #    self.current_fg = self.parent.fg

        #if self.current_bg is not None or self.bg is not None:
        #    self.gc = self.parent.root.create_gc()

    def _get_desktops(self, *args):
        conn = self.parent.connection
        scr = self.parent.screen
        totalc = conn.core.GetProperty(0,
                scr.root,
                self._NET_NUMBER_OF_DESKTOPS,
                xcb.XA_CARDINAL,
                0,
                12)

        namesc = conn.core.GetProperty(0,
                scr.root,
                self._NET_DESKTOP_NAMES,
                self.UTF8_STRING,
                0,
                32)

        totalr = totalc.reply()
        self.num_desktops = struct.unpack_from("I", totalr.value.buf())[0]

        namesr = namesc.reply()
        self.desktops = struct.unpack_from("%ds" % namesr.value_len, 
                namesr.value.buf())[0].strip("\x00").split("\x00")

        self._update()

    def _output(self):
        if self.showall:
            return ' '.join(self.desktops[:self.num_desktops])
        else:
            return self.desktops[self.current]


    def _update(self, event=None):
        conn = self.parent.connection
        scr = self.parent.screen
        currc = conn.core.GetProperty(0, scr.root, self._NET_CURRENT_DESKTOP,
                xcb.XA_CARDINAL, 0, 12)
        currp = currc.reply()
        self.current = struct.unpack_from("I", currp.value.buf())[0]
        self.width_hint = self.parent.text_width(self._output())
        self.parent.update()


    def draw(self):
        color = self.fg
        if self.showall:
            for i, name in enumerate(self.desktops[:self.num_desktops]):
                if i == self.current:
                    color = self.current_fg
                else:
                    color = self.fg

                if i != 0:
                    self.parent.draw_text(' ')
                self.parent.draw_text(name, color)

        else:
            self.parent.draw_text(self.desktops[self.current], self.current_fg)

