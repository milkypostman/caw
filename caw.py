#!/usr/bin/python

import cawc
import xcb
import xcb.xproto as xproto

class Caw:
    def __init__(self):
        self.c_connection = cawc.connect()

        self.connection = xcb.wrap(self.c_connection)
        print self.connection.has_error()
        print self.connection.pref_screen
        self.screen = self.connection.get_setup().roots[0]
        print self.screen.width_in_pixels
        print self.screen.height_in_pixels
        print self.connection.generate_id()
        print self.connection.generate_id()

        self.height = 10
        self.width = self.screen.width_in_pixels
        self.x = 0
        self.y = self.screen.height_in_pixels - self.height

        self._init_window()

    def get_atoms(self, atoms):
        conn = self.connection

        # get all the atoms we need
        cookies = []
        for a in atoms:
            cookies.append(conn.core.InternAtom(False,len(a),a))

        ret = {}

        # get the replies (properly)
        for c,a in zip(cookies, atoms):
            ret[a] = c.reply().atom

        return ret

    def _init_window(self):
        conn = self.connection
        scr = self.screen
        self._back_pixmap = conn.generate_id()
        conn.core.CreatePixmap(scr.root_depth,
                self._back_pixmap, scr.root,
                self.width, self.height)

        self.window = conn.generate_id()
        conn.core.CreateWindow(scr.root_depth,
                self.window, scr.root,
                self.x, self.y,
                self.width, self.height,
                0,
                xproto.WindowClass.InputOutput,
                scr.root_visual,
                xproto.CW.BackPixmap | xproto.CW.EventMask,
                [self._back_pixmap, 
                    xproto.EventMask.Exposure |
                    xproto.EventMask.KeyPress |
                    xproto.EventMask.EnterWindow |
                    xproto.EventMask.ButtonRelease]
                )

        self._gc = conn.generate_id()
        conn.core.CreateGC(self._gc, self.window,
                xproto.GC.Foreground | xproto.GC.Background,
                [scr.white_pixel, scr.black_pixel])

if __name__ == '__main__':
    caw = Caw()

