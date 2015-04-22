import select
import collections
try:
    import xcffib as xcb
    import xcffib.xproto as xproto
except:
    import xcb
    import xcb.xproto as xproto
import struct
import array
import sys
import widget

# our module needs to be loaded after the xcb module
import cawc as cawc

import os
import time
import re
import math
import operator
import itertools
import heapq
import socket


class Caw:
    """CAW! is a Python taskbar, systemtray, infobar allowing mouse interactions and extensibility through Python.

    Parameters
    ----------

    xoffset : offset in the x direction.  Values < 1 are interpreted as fractions of \
            the screen width.  (ie. .5 would mean to offset by half of the screen)

    yoffset : pixel offset in the y direction.

    height : pixel height of the panel

    width : width of the panel.  Values < 1 are intpreted as fractions of the screen width. \
            (ie. .5 means to reduce the width to 50% of the total screen width).

    edge : [0|1] edge to position the panel on. 0 = top edge, 1 = bottom edge.

    fg : integer value for the default foreground color of the panel.  \
            Can be written in hex (eg. 0xff0000 being red)

    bg : integer value for the default background color of the panel.

    border : integer value for the border color of the panel.

    border_width : width of the panel border

    shading : [0-255] level of shading to apply to the panel.  \
            0 is a psudo-transparent, 255 is opaque.

    above : *bool* representing if the panel should be above all other \
            windows.  This option is ignored if the panel is not touching \
            an edge.

    font_face : font face to use.

    font_size : *int* given the point size of the font

    dpi : manually set the font dpi setting for cairo/pango
    """

    def __init__(self, **kwargs):
        """ Initialize the main Caw class."""

        self.connection_c = cawc.xcb_connect()
        self.screen_c = cawc.xcb_screen(self.connection_c)
        self.visualtype_c = cawc.xcb_visualtype(self.screen_c)

        self.connection = xcb.wrap(self.connection_c)
        self.screen = self.connection.get_setup().roots[0]

        self.border_width = kwargs.get('border_width', 2)
        self.xoffset = kwargs.get('xoffset', 0)
        if 0 < self.xoffset < 1:
            self.xoffset = int(self.screen.width_in_pixels * self.xoffset)
        self.yoffset = kwargs.get('yoffset', 0)
        self.x = self.xoffset
        self.height = kwargs.get('height', 10) + 2*self.border_width
        self.width = kwargs.get('width', self.screen.width_in_pixels)
        if self.width < 0:
            self.width += self.screen.width_in_pixels
        elif self.width < 1:
            self.width = int(self.screen.width_in_pixels * self.width)

        self.edge = kwargs.get('edge', 1)
        if self.edge:
            self.y = self.yoffset + self.screen.height_in_pixels - self.height
        else:
            self.y = self.yoffset

        self.above = kwargs.get('above', True)
        self.fg = kwargs.get('fg', 0x000000)
        self.bg = kwargs.get('bg', 0xd6d6d6)
        self.border = kwargs.get('border', 0x606060)
        self.shading = kwargs.get('shading', 100)

        self.font_face = kwargs.get('font_face', 'Terminus')
        self.font_bold = kwargs.get('font_bold', False)
        self.font_size = kwargs.get('font_size', 8)
        self.font_yoffset = kwargs.get('font_yoffset', 0)
        self.dpi = kwargs.get('dpi', -1)

        self.widgets = kwargs.get('widgets', [])
        self._mtime = os.path.getmtime(sys.argv[0])
        #print self.widgets
        #print '----'
        #print kwargs
        self._timers = []
        self.events = collections.defaultdict(list)
        self.atoms = collections.defaultdict(list)
        self._dirty = False
        self._dirty_widgets = []

        # poll object for polling file descriptors
        self._poll = select.poll()
        self._fdhandlers = {}

        self._init_window()
        self._init_atoms()
        self._init_cairo()
        self._init_pango()

        print "Window:", self.window
        print "X:", self.x
        print "Y:", self.y
        print "Width:", self.width
        print "Height:", self.height
        self._set_properties()
        self._update_struts()
        self._update_background()

        self.connection.core.MapWindow(self.window)
        self.connection.flush()

        self.events[xproto.ExposeEvent].append(self.redraw)
        self.events[xproto.PropertyNotifyEvent].append(self._property_notify)
        self.events[xproto.ButtonPressEvent].append(self._button_press)
        self.atoms[self._XROOTPMAP_ID].append(self._update_background)


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
        self.back_pixmap = conn.generate_id()
        conn.core.CreatePixmap(scr.root_depth,
                self.back_pixmap, scr.root,
                self.width, self.height)

        self.window = conn.generate_id()
        conn.core.CreateWindow(scr.root_depth,
                self.window, scr.root,
                self.x, self.y,
                self.width, self.height,
                0,
                xproto.WindowClass.InputOutput,
                scr.root_visual,
                #xproto.CW.BackPixmap | xproto.CW.BackPixel | xproto.CW.EventMask,
                #[self.back_pixmap, self.screen.black_pixel,
                xproto.CW.BackPixmap | xproto.CW.EventMask,
                [self.back_pixmap,
                    xproto.EventMask.Exposure |
                    xproto.EventMask.EnterWindow |
                    xproto.EventMask.ButtonPress |
                    xproto.EventMask.ButtonRelease]
                )

        self._gc = conn.generate_id()
        conn.core.CreateGC(self._gc, self.window,
                xproto.GC.Foreground | xproto.GC.Background,
                [scr.white_pixel, scr.black_pixel])

    def _init_cairo(self):
        self._back_cairo_c = cawc.cairo_create(
                self.connection_c,
                self.back_pixmap,
                self.visualtype_c,
                self.width,
                self.height)

        self.cairo_c = cawc.cairo_create(
                self.connection_c,
                self.window,
                self.visualtype_c,
                self.width,
                self.height)

        cawc.cairo_select_font_face(self.cairo_c, self.font_face, self.font_bold)
        cawc.cairo_set_font_size(self.cairo_c, self.font_size)
        #self._text_height = cawc.cairo_text_height(self.cairo_c, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890')
        #print "Text Height:", self._text_height
        #self._font_height = cawc.cairo_font_height(self.cairo_c)
        # this translates to ascent - descent
        #self._font_height = self._font_height[0] - self._font_height[1]

    def _init_pango(self):
        self.layout_c = cawc.pango_cairo_create_layout(self.cairo_c)

        if self.dpi > 0:
            cawc.pango_cairo_layout_set_resolution(self.layout_c, self.dpi)

        self.fontdesc_c = cawc.pango_font_description_from_string(self.font_face + ' ' + str(self.font_size))
        cawc.pango_layout_set_font_description(self.layout_c, self.fontdesc_c)
        _, self._font_height = cawc.pango_layout_get_pixel_size(self.layout_c)
        print "Font Height:", self._font_height

    def _init_atoms(self):
        a = self.get_atoms([
                "_NET_WM_WINDOW_TYPE",
                "_NET_WM_WINDOW_TYPE_DOCK",
                "_NET_WM_WINDOW_TYPE_DESKTOP",
                "_NET_WM_DESKTOP",
                "_NET_WM_STATE",
                "_NET_WM_STATE_SKIP_PAGER",
                "_NET_WM_STATE_SKIP_TASKBAR",
                "_NET_WM_STATE_STICKY",
                "_NET_WM_STATE_ABOVE",
                "_NET_WM_STATE_BELOW",
                "_NET_WM_STRUT",
                "_NET_WM_STRUT_PARTIAL",
                "_WIN_STATE",
                "_XROOTPMAP_ID",
                ])
        for key,val in a.iteritems():
            setattr(self, key, val)

    def _root_pixmap(self):
        conn = self.connection
        scr = self.screen
        cookie = conn.core.GetProperty(False, scr.root, self._XROOTPMAP_ID,
                xproto.Atom.PIXMAP, 0, 10)

        rep = cookie.reply()
        if len(rep.value.buf()) < 4:
            return
        return struct.unpack_from("I", rep.value.buf())[0]

    def _set_properties(self):
        conn = self.connection
        scr = self.screen
        win = self.window

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, xproto.Atom.WM_NAME, xproto.Atom.STRING, 8, len("CAW!"), "CAW!")

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, xproto.Atom.WM_CLASS, xproto.Atom.STRING, 8, len("caw\0CAW\0"), "caw\0CAW\0")

        cawc.set_hints(self.connection_c, self.window, self.x, self.y, self.width, self.height);

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._NET_WM_DESKTOP, xproto.Atom.CARDINAL, 32, 1, struct.pack("I",0xffffffff))

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._WIN_STATE, xproto.Atom.CARDINAL, 32, 1, struct.pack("I",1))


        conn.core.ChangeWindowAttributes(scr.root,
                xproto.CW.EventMask,
                [xproto.EventMask.PropertyChange|xproto.EventMask.StructureNotify])

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._NET_WM_WINDOW_TYPE, xproto.Atom.ATOM, 32, 1, struct.pack("I",self._NET_WM_WINDOW_TYPE_DOCK))
        if self.above:
            conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._NET_WM_STATE, xproto.Atom.ATOM, 32, 4, struct.pack("IIII",self._NET_WM_STATE_SKIP_TASKBAR, self._NET_WM_STATE_SKIP_PAGER, self._NET_WM_STATE_STICKY, self._NET_WM_STATE_ABOVE))
        else:
            conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._NET_WM_STATE, xproto.Atom.ATOM, 32, 4, struct.pack("IIII",self._NET_WM_STATE_SKIP_TASKBAR, self._NET_WM_STATE_SKIP_PAGER, self._NET_WM_STATE_STICKY, self._NET_WM_STATE_BELOW))


    def _update_struts(self):
        if self.above and (self.y == 0 or self.y == self.screen.height_in_pixels - self.height):
            print "updating struts"
            cawc.update_struts(self.connection_c, self.window, self.x, self.y, self.width, self.height,  self.edge)

    def rgb(self, color):
        r = (color >> 16) / 255.
        g = ((color >> 8) & 0xff) / 255.
        b = (color & 0xff) / 255.

        return (r,g,b)

    def set_source(self, cairo, color, shading, height):
        a = shading / 255.
        if isinstance(color, tuple) or isinstance(color, list):
            pattern = cawc.cairo_pattern_create_linear(0,0,0,height)
            step = float(height) / (len(color) - 1)
            cur = 0
            for color in self.bg:
                r,g,b = self.rgb(color)
                cawc.cairo_pattern_add_color_stop_rgba(pattern, cur, r, g, b, a)
                cur += step
            cawc.cairo_set_source(cairo, pattern)
            cawc.cairo_pattern_destroy(pattern)
        else:
            r,g,b = self.rgb(color)
            cawc.cairo_set_source_rgba(cairo, r, g, b, a)

    def _update_background(self, *_):
        #print "updating background"
        conn = self.connection
        rp = self._root_pixmap()
        if rp is not None:
            conn.core.CopyArea(rp,
                self.back_pixmap,
                self._gc,
                self.x, self.y,
                0,0,
                self.width, self.height)

        self.set_source(self._back_cairo_c, self.bg, self.shading, self.height)
        cawc.cairo_set_line_width(self._back_cairo_c, 4)
        cawc.cairo_rectangle(self._back_cairo_c, 0, 0, self.width, self.height);
        cawc.cairo_fill(self._back_cairo_c)

        i = 0
        r,g,b = self.rgb(self.border)
        cawc.cairo_set_line_width(self._back_cairo_c, 1.0)
        cawc.cairo_set_source_rgba(self._back_cairo_c, r, g, b, 1.0)
        while i < self.border_width:
            cawc.cairo_rectangle(self._back_cairo_c, i, i, self.width-2*i-1, self.height-2*i-1);
            cawc.cairo_stroke(self._back_cairo_c)
            i+=1

    def _init_widgets(self):
        for w in self.widgets:
            w.init(self)

    def registerfd(self, fd, func, eventmask=select.POLLIN):
        if hasattr(fd, 'fileno'):
            fd = fd.fileno()
        self._poll.register(fd, eventmask)
        self._fdhandlers[fd] = func

    def unregisterfd(self, fd):
        if hasattr(fd, 'fileno'):
            fd = fd.fileno()
        self._poll.unregister(fd)
        del self._fdhandlers[fd]

    def _process_xevents(self, eventmask):
        while True:
            try:
                event = self.connection.poll_for_event()
                #print "Event:", type(event)
                #print "OpCode:", event.response_type
                #print "Window:", getattr(event, 'window', None)
                if event.response_type == 161:
                    event = xproto.ClientMessageEvent(event)
                for func in self.events[type(event)]:
                    func(event)
            except xcb.xproto.BadWindow as e:
                # FIXME: not sure why i have to ignore this
                # it is a fix for the system tray crashing
                print "Bad Window:", (e.args[0].bad_value), e.args[0].major_opcode
            except xcb.xproto.BadMatch as e:
                print "Bad Match:", (e.args[0].bad_value), e.args[0].major_opcode
            except (IOError, AttributeError):
                break

            #self.connection.flush()


    def mainloop(self):
        conn = self.connection

        self._init_widgets()
        self.registerfd(conn.get_file_descriptor(), self._process_xevents)

        self._update_background()
        conn.flush()

        timeout = 0
        while True:
            if self._dirty:
                #print "updating all"
                self.redraw()
                self._dirty = False
                self._dirty_widgets = []
            elif self._dirty_widgets:
                #print "only updating dirty widgets"
                for dw in self._dirty_widgets:
                    self.clear(dw.x, 0, dw.width, self.height)
                    self._pangox = dw.x
                    dw.draw()
                self._dirty_widgets = []

            conn.flush()
            readfds = self._poll.poll(timeout*1000)
            for (fd, eventmask) in readfds:
                self._fdhandlers[fd](eventmask)

            if len(self._timers) > 0:
                now = time.time()
                while self._timers[0][0] <= now:
                    timeout, func = heapq.heappop(self._timers)
                    func()

                timeout = max(self._timers[0][0] - time.time(), 1)
            else:
                timeout = -1


            #if self._mtime is not None and self._mtime < os.path.getmtime(self.config_file):
            if os.path.getmtime(sys.argv[0]) > self._mtime:
                os.execl(sys.executable, sys.executable, *sys.argv)
                sys.exit(5)

    def schedule(self, timeout, func):
        heapq.heappush(self._timers, (timeout + int(time.time()), func))

    def clear(self, x, y, w, h):
        self.connection.core.ClearArea(0, self.window, x, y, w, h)

    def update(self, client=None, *args):
        if client is not None:
            if client.width_hint == client.width or client.width_hint < 0:
                #print "adding to dirty list", client
                self._dirty_widgets.append(client)
                return

        self._dirty = True

    def redraw(self, *_):
        #print "********** REDRAW **********"
        conn = self.connection
        #if self._background_needs_update:
        #    self._update_background()
        #    self._background_needs_update -= 1
        self.clear(0, 0, self.width, self.height)
        varspace = self.width-self.border_width*2
        varcount = 0

        for w in self.widgets:
            if w.width_hint < 0:
                varcount += 1
            else:
                varspace -= w.width_hint

        if varcount > 0:
            varspace /= varcount

        x = self.border_width
        y = (self.height - self._font_height)/2 + self.font_yoffset
        for w in self.widgets:
            ww = w.width_hint
            if ww < 0:
                ww = varspace
            w.x = x
            w.width = ww
            self._pangox = x
            w.draw()
            x += ww

    def _button_press(self, e):
        #print "************ BUTTON NOTIFY ************"
        x = e.event_x
        left = 0
        right = len(self.widgets)
        while left < right:
            mid = (left + right) / 2
            w = self.widgets[mid]
            #print w, w.x, w.width
            if x < w.x:
                right = mid
            elif x >= w.x+w.width:
                left = mid+1
            else:
                #print w
                w.button_press(e.detail, e.event_x)
                break

    def send_event(self, win, type, d1, d2=0, d3=0, d4=0, d5=0):
        event = struct.pack('BBHII5I', 33, 32, 0, win, type, d1, d2, d3, d4, d5)
        return self.connection.core.SendEvent(0, win, 0xffffff, event)

    def send_event_checked(self, win, type, d1, d2=0, d3=0, d4=0, d5=0):
        event = struct.pack('BBHII5I', 33, 32, 0, win, type, d1, d2, d3, d4, d5)
        return self.connection.core.SendEventChecked(0, win, 0xffffff, event)

    def _property_notify(self, e):
        #print "************ PROPERTY NOTIFY ************"
        #print "Atom:",e.atom
        for func in self.atoms[e.atom]:
            #print "Found functions"
            func(e)

    def draw_text(self, text, fg=None, x=None, width=None, align=0, ellipsize=3):
        if fg is None:
            fg = self.fg

        r,g,b = self.rgb(fg)

        cawc.cairo_set_source_rgb(self.cairo_c, r, g, b);

        y = (self.height - self._font_height)/2 + self.font_yoffset
        if x is None:
            x = self._pangox
        else:
            self._pangox = x

        cawc.cairo_move_to(self.cairo_c, x, y)

        if width is not None and width > 0:
            cawc.pango_layout_set_text(self.layout_c, text, width, align, ellipsize)
        else:
            cawc.pango_layout_set_text(self.layout_c, text)

        cawc.pango_cairo_update_show_layout(self.cairo_c, self.layout_c)
        self._pangox += self.text_width(text)
        #cawc.cairo_show_text(self.cairo_c, text);

    def text_width(self, text):
        cawc.pango_layout_set_text(self.layout_c, text)
        width, _ = cawc.pango_layout_get_pixel_size(self.layout_c)
        return width
        #return cawc.cairo_text_width(self.cairo_c, text)

    def draw_rectangle(self, x, y, w, h, color=None, shading=None, line_width=1):
        if color is not None:
            if shading is None:
                shading = self.shading
            self.set_source(self.cairo_c, color, shading, h)


        cawc.cairo_set_line_width(self.cairo_c, line_width)
        cawc.cairo_rectangle(self.cairo_c, x, y, w, h)
        cawc.cairo_stroke(self.cairo_c)

    def draw_rectangle_filled(self, x, y, w, h, color=None, shading=None):
        if color is not None:
            if shading is None:
                shading = self.shading
            self.set_source(self.cairo_c, color, shading, h)


        cawc.cairo_set_line_width(self.cairo_c, 1)
        cawc.cairo_rectangle(self.cairo_c, x, y, w, h);
        cawc.cairo_fill(self.cairo_c)
