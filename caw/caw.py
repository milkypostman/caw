import select
import collections
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
    def __init__(self, **kwargs): 
        self.connection_c = cawc.xcb_connect()
        self.screen_c = cawc.xcb_screen(self.connection_c)
        self.visualtype_c = cawc.xcb_visualtype(self.screen_c)

        self.connection = xcb.wrap(self.connection_c)
        self.screen = self.connection.get_setup().roots[0]

        self.border_width = kwargs.get('border_width', 2)
        self.height = kwargs.get('height', 10) + 2*self.border_width
        self.width = kwargs.get('width', self.screen.width_in_pixels)
        self.x = 0
        if kwargs.get('edge', 1):
            self.y = self.screen.height_in_pixels - self.height
        else:
            self.y = 0

        self.fg_color = kwargs.get('fg_color', 0x000000)
        self.bg_color = kwargs.get('bg_color', 0xd6d6d6)
        self.border_color = kwargs.get('border_color', 0x606060)
        self.shading = kwargs.get('shading', 100)

        self.font_face = kwargs.get('font_face', 'Terminus')
        self.font_size = kwargs.get('font_size', 8)

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

        cawc.cairo_select_font_face(self.cairo_c, self.font_face)
        cawc.cairo_set_font_size(self.cairo_c, self.font_size)
        self._font_height = cawc.cairo_font_height(self.cairo_c)

    def _init_atoms(self):
        a = self.get_atoms([
                "_NET_WM_WINDOW_TYPE", 
                "_NET_WM_WINDOW_TYPE_DOCK", 
                "_NET_WM_DESKTOP",
                "_NET_WM_STATE",
                "_NET_WM_STATE_SKIP_PAGER",
                "_NET_WM_STATE_SKIP_TASKBAR",
                "_NET_WM_STATE_STICKY",
                "_NET_WM_STATE_ABOVE",
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
                xcb.XA_PIXMAP, 0, 10)

        rep = cookie.reply()
        if len(rep.value.buf()) < 4:
            return
        return struct.unpack_from("I", rep.value.buf())[0]

    def _set_properties(self):
        conn = self.connection
        scr = self.screen
        win = self.window

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, xcb.XA_WM_NAME, xcb.XA_STRING, 8, len("CAW!"), "CAW!")

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, xcb.XA_WM_CLASS, xcb.XA_STRING, 8, len("caw\0CAW\0"), "caw\0CAW\0")

        cawc.set_hints(self.connection_c, self.window, self.x, self.y, self.width, self.height);

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._NET_WM_DESKTOP, xcb.XA_CARDINAL, 32, 1, struct.pack("I",0xffffffff))

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._WIN_STATE, xcb.XA_CARDINAL, 32, 1, struct.pack("I",1))

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._NET_WM_WINDOW_TYPE, xcb.XA_ATOM, 32, 1, struct.pack("I",self._NET_WM_WINDOW_TYPE_DOCK))

        conn.core.ChangeWindowAttributes(scr.root,
                xproto.CW.EventMask, 
                [xproto.EventMask.PropertyChange|xproto.EventMask.StructureNotify])

        conn.core.ChangeProperty(xproto.PropMode.Replace, win, self._NET_WM_STATE, xcb.XA_ATOM, 32, 4, struct.pack("IIII",self._NET_WM_STATE_SKIP_TASKBAR, self._NET_WM_STATE_SKIP_PAGER, self._NET_WM_STATE_STICKY, self._NET_WM_STATE_ABOVE))


    def _update_struts(self):
        cawc.update_struts(self.connection_c, self.window,
                self.x, self.y, self.width, self.height)

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

        r = (self.bg_color >> 16) / 255.
        g = ((self.bg_color >> 8) & 0xff) / 255.
        b = (self.bg_color & 0xff) / 255.
        a = self.shading / 255.
        cawc.cairo_set_source_rgba(self._back_cairo_c, r, g, b, a)
        cawc.cairo_rectangle(self._back_cairo_c, 0, 0, self.width, self.height);
        cawc.cairo_fill(self._back_cairo_c)

        i = 0
        r = (self.border_color >> 16) / 255.
        g = ((self.border_color >> 8) & 0xff) / 255.
        b = (self.border_color & 0xff) / 255.
        cawc.cairo_set_source_rgb(self._back_cairo_c, r, g, b)
        while i < self.border_width:
            cawc.cairo_rectangle(self._back_cairo_c, i, i, self.width-2*i, self.height-2*i);
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
                #print "OpCode:", event.type
                #print "Window:", getattr(event, 'window', None)
                if event.type == 161:
                    event = xproto.ClientMessageEvent(event)
                for func in self.events[type(event)]:
                    func(event)
            except xcb.xproto.BadWindow as e:
                # FIXME: not sure why i have to ignore this
                # it is a fix for the system tray crashing
                print "Bad Window:", (e.args[0].bad_value), e.args[0].major_opcode
            except IOError:
                break


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
                conn.flush()
            elif self._dirty_widgets:
                #print "only updating dirty widgets"
                y = (self.height + self._font_height)/2
                for dw in self._dirty_widgets:
                    self.clear(dw.x, 0, dw.width, self.height)
                    cawc.cairo_move_to(self.cairo_c, dw.x, y)
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
                sys.exit(5)

            conn.flush()

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
        y =  (self.height + self._font_height)/2
        for w in self.widgets:
            ww = w.width_hint
            if ww < 0:
                ww = varspace
            w.x = x
            w.width = ww
            cawc.cairo_move_to(self.cairo_c, w.x, y)
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
            if x < w.x:
                right = mid
            elif x >= w.x+w.width:
                left = mid+1
            else:
                #print w
                w.button_press(e.detail, e.event_x)
                break

    def _property_notify(self, e):
        #print "************ PROPERTY NOTIFY ************"
        #print "Atom:",e.atom
        for func in self.atoms[e.atom]:
            #print "Found functions"
            func(e)

    def draw_text(self, text, color=None, x=None):
        if color is None:
            color = self.fg_color

        r = (float(color >> 16)/0xff)
        g = (float(color >> 8 & 0xff)/0xff)
        b = (float(color & 0xff)/0xff)

        cawc.cairo_set_source_rgb(self.cairo_c, r, g, b);

        if x is not None:
            y =  (self.height + self._font_height)/2
            cawc.cairo_move_to(self.cairo_c, x, y)

        cawc.cairo_show_text(self.cairo_c, text);

    def text_width(self, text):
        return cawc.cairo_text_width(self.cairo_c, text)
