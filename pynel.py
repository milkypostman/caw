#!/usr/bin/python

from ppmodule import ppinit, ppshade, ppicon, ppfont, ppfontsize, ppclear
import Xlib
import Xlib.display
import Xlib.error
import Xlib.protocol.event
import collections
import heapq
import select
import time
import re
import operator
import itertools
import math
from Xlib import Xatom, Xutil, X

FONT = "Terminus-8"

class Widget(object):
    def __init__(self):
        super(Widget, self).__init__()
        self.width = 0
        self.min_width = 0
        self.x = 0
        self.parent = None

    def setup(self):
        """ reimplement in subclass """

    def draw(self):
        """ reimplement in subclass """
        pass

class Desktop(Widget):
    def __init__(self, current_fg=None, fg=None, current_bg=None, bg=None):
        self.desktops = []
        self.current = 0
        self.fg = fg
        self.current_fg = current_fg
        self.current_bg = current_bg
        self.bg = bg
        self.current_bg = 0x00ff00

    def setup(self):
        self._NET_CURRENT_DESKTOP = self.parent.display.intern_atom("_NET_CURRENT_DESKTOP")
        self._NET_WM_DESKTOP = self.parent.display.intern_atom("_NET_WM_DESKTOP")
        self._NET_DESKTOP_NAMES = self.parent.display.intern_atom("_NET_DESKTOP_NAMES")
        self._NET_NUMBER_OF_DESKTOPS = self.parent.display.intern_atom("_NET_NUMBER_OF_DESKTOPS")
        self.parent.atoms[self._NET_WM_DESKTOP].append(self._update)
        self.parent.atoms[self._NET_CURRENT_DESKTOP].append(self._update)
        self._get_desktops()
        if self.fg is None:
            self.fg = self.parent.fg
        if self.current_fg is None:
            self.current_fg = self.parent.fg

        if self.current_bg is not None or self.bg is not None:
            self.gc = self.parent.root.create_gc()

        self._update()

    def _get_desktops(self):
        total = self.parent.root.get_full_property(self._NET_NUMBER_OF_DESKTOPS, 0).value[0]
        names = self.parent.root.get_full_property(self._NET_DESKTOP_NAMES, 0)
        if hasattr(names, "value"):
            names = names.value.strip("\x00").split("\x00")
        else:
            names = []
            for x in range(desktop.total):
                names.append(str(x))

        self.desktops = names

        self.min_width = self.parent.text_width(self._output())

    def _output(self):
        out = ""
        for i, name in enumerate(self.desktops):
            if i == self.current:
                out += "<"
            else:
                out += " "

            out += name

            if i == self.current:
                out += ">"
            else:
                out += " "

        return out


    def _update(self, event=None):
        if event is None:
            self.current = self.parent.root.get_full_property(self._NET_CURRENT_DESKTOP, Xatom.CARDINAL).value[0]

        if hasattr(event, "window"):
            try:
                self.current = event.window.get_full_property(self._NET_CURRENT_DESKTOP, Xatom.CARDINAL).value[0]
            except:
                try:
                    self.current = event.window.get_full_property(self._BLACKBOX, 0).value[2]
                except:
                    self.current = 0

        self.parent.update()


    def draw(self):
        color = self.fg
        curx = self.x
        for i, name in enumerate(self.desktops):
            if i == self.current:
                out = "<" + name + ">"
                color = self.current_fg
                width = self.parent.text_width(out)
                print width
                #if self.current_bg is not None:
                    #self.gc.change(foreground=self.current_bg)
                    #print curx, curx+width-1
                    #cfillrectangle(self.parent.window.id, self.current_bg, curx, self.parent.border, width-1, self.parent.height - self.parent.border*2)
            else:
                out = " " + name + " "
                color = self.fg
                width = self.parent.text_width(out)
                #if self.bg is not None:
                    #self.gc.change(foreground=self.bg)
                    #print curx, curx+width
                    #self.parent.window.fill_rectangle(self.gc, curx, self.parent.border, width-1, self.parent.height - self.parent.border*2)
                    #cfillrectangle(self.parent.window.id, self.bg, curx, self.parent.border, width-1, self.parent.height - self.parent.border*2)

            self.parent.draw_text(curx, out, color)
            curx += self.parent.text_width(out)



class Systray(Widget):
    def setup(self, icon_size=None):
        self.icon_size = icon_size
        if icon_size is None:
            if self.parent.height >= 24:
                self.icon_size = 24
            elif self.parent.height >= 16:
                self.icon_size = 16
            else:
                self.icon_size = self.parent.height

        self.error_handler = Xlib.error.CatchError()
        self.parent.events[X.ClientMessage].append(self._clientmessage)
        self.parent.events[X.ConfigureNotify].append(self._configurenotify)
        self.parent.events[X.DestroyNotify].append(self._destroynotify)

        # create a system tray selection owner window
        dsp = self.parent.display
        self._NET_SYSTEM_TRAY_OPCODE = dsp.intern_atom("_NET_SYSTEM_TRAY_OPCODE")
        manager = dsp.intern_atom("MANAGER")
        selection = dsp.intern_atom("_NET_SYSTEM_TRAY_S%d" % dsp.get_default_screen())

        self._window = self.parent.root.create_window(-1, -1, 1, 1, 0, self.parent.screen.root_depth)
        self._window.set_selection_owner(selection, X.CurrentTime)
        self.parent.send_event(self.parent.root, manager, [X.CurrentTime, selection, self._window.id], (X.StructureNotifyMask))

        self.tasks = {}

    def _destroynotify(self, event):
        if event.window.id in self.tasks:
            del self.tasks[event.window.id]
            self.min_width=self.icon_size*len(self.tasks)
            self.parent.update()

    def _clientmessage(self, event):
        print "********* CLIENT MESSAGE **************"
        if event.window == self._window:
            data = event.data[1][1] # opcode
            task = event.data[1][2] # taskid
            if event.client_type == self._NET_SYSTEM_TRAY_OPCODE and data == 0:
                taskwin = self.parent.display.create_resource_object("window", task)
                taskwin.reparent(self.parent.window.id, 0, 0)
                taskwin.change_attributes(event_mask=(X.ExposureMask|X.StructureNotifyMask))
                self.tasks[task] = dict(window=taskwin, x=0, y=0, width=self.icon_size, height=self.icon_size)
                self.min_width=self.icon_size*len(self.tasks)
                self.parent.update()

    def _configurenotify(self, event):
        print "********* CONFIGURE NOTIFY **************"
        if event.window.id in self.tasks:
            task = self.tasks[event.window.id]
            task['window'].configure(onerror=self.error_handler, width=task['width'], height=task['height'])

    def draw(self):
        curx = self.x
        print "x:", self.x
        for task in self.tasks:
            print "drawing task:",task
            t = self.tasks[task]
            t['x'] = curx
            t['y'] = (self.parent.height - t['height'])/2
            t['window'].configure(onerror=self.error_handler, x=t['x'], y=t['y'], width=t['width'], height=t['height'])
            t['window'].map(onerror=self.error_handler)
            curx += t['width']



class Text(Widget):
    def __init__(self, text="undefined", color=None):
        super(Text, self).__init__()
        self.text = text
        self.color = color

    def setup(self):
        self.min_width = self.parent.text_width(self.text)

    def draw(self):
        self.parent.draw_text(self.x, self.text, self.color)


class CPU(Widget):
    _initialized = False
    _widgets = collections.defaultdict(list)

    def __init__(self, cpu=0):
        super(CPU, self).__init__()
        self.cpu = cpu

    def setup(self):
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
        self.min_width = self.parent.text_width("%d%%" % self._data['usage'])

    data = property(_get_data, _set_data)

    def draw(self):
        self.parent.draw_text(self.x, "%d%%" % self._data['usage'])

class Clock(Widget):
    def __init__(self, format="%Y.%m.%d %H:%M:%S"):
        super(Clock, self).__init__()
        self.format = format

    def setup(self):
        self.update()

    def update(self):
        self.text = time.strftime(self.format)
        self.min_width = self.parent.text_width(self.text)
        self.parent.update();
        self.parent.schedule(1, self.update)

    def draw(self):
        self.parent.draw_text(self.x, self.text, 0xffffff)


class Pynel(object):
    def __init__(self):
        super(Pynel, self).__init__()
        self.display = Xlib.display.Display()
        self.screen = self.display.screen()
        self.root = self.screen.root

        self.events = collections.defaultdict(list)
        self.atoms = collections.defaultdict(list)
        self._timers = []

        self.width = self.screen.width_in_pixels
        self.height = 10
        self.border = 2

        self.height += self.border *2
        self.x = 0
        self.y = self.screen.height_in_pixels - self.height

        self.bg = 0xffffff
        self.fg = 0x000000
        self.shade = 50

        self.left = []
        self.right = []

        self.root_map = None

        self.window = self.screen.root.create_window(self.x, self.y,
            self.width, self.height,
            0, self.screen.root_depth, window_class=X.InputOutput,
            visual=X.CopyFromParent, colormap=X.CopyFromParent,
            event_mask=(X.ExposureMask|X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask))

        ppinit(self.window.id, FONT)

        self._set_props()
        self._update_struts()
        self.root.change_attributes(event_mask=(X.PropertyChangeMask))
        self.window.map()
        self.display.flush()

        self.events[X.Expose].append(self._redraw)
        self.events[X.PropertyNotify].append(self._property_notify)
        self.atoms[self._XROOTPMAP_ID].append(self._update_background)

    def _property_notify(self, e):
        for func in self.atoms[e.atom]:
            func(e)

    def _set_props(self):
        """ Set necessary X atoms and panel window properties """
        self._WIN_STATE = self.display.intern_atom("_WIN_STATE")
        self._XROOTPMAP_ID = self.display.intern_atom("_XROOTPMAP_ID")
        self._NET_WM_NAME = self.display.intern_atom("_NET_WM_NAME")
        self._NET_WM_DESKTOP = self.display.intern_atom("_NET_WM_DESKTOP")
        self._NET_WM_WINDOW_TYPE = self.display.intern_atom("_NET_WM_WINDOW_TYPE")
        self._NET_WM_WINDOW_TYPE_DOCK = self.display.intern_atom("_NET_WM_WINDOW_TYPE_DOCK")
        self._NET_WM_STATE = self.display.intern_atom("_NET_WM_STATE")
        self._NET_WM_STATE_STICKY = self.display.intern_atom("_NET_WM_STATE_STICKY")
        self._NET_WM_STATE_SKIP_PAGER = self.display.intern_atom("_NET_WM_STATE_SKIP_PAGER")
        self._NET_WM_STATE_SKIP_TASKBAR = self.display.intern_atom("_NET_WM_STATE_SKIP_TASKBAR")
        self._NET_WM_STATE_ABOVE = self.display.intern_atom("_NET_WM_STATE_ABOVE")
        self._NET_WM_STRUT = self.display.intern_atom("_NET_WM_STRUT")
        self._NET_WM_STRUT_PARTIAL = self.display.intern_atom("_NET_WM_STRUT_PARTIAL")

        self._MOTIF_WM_HINTS = self.display.intern_atom("_MOTIF_WM_HINTS")

        self.window.set_wm_name("Pynel")
        self.window.set_wm_class("pynel","Pynel") 

        self.window.set_wm_hints(flags=(Xutil.InputHint|Xutil.StateHint),
            input=0, initial_state=1)

        self.window.set_wm_normal_hints(flags=(
            Xutil.PPosition|Xutil.PMaxSize|Xutil.PMinSize),
            min_width=10, min_height=self.height,
            max_width=self.width, max_height=self.height)

        self.window.change_property(self._NET_WM_DESKTOP, Xatom.CARDINAL, 32,
                [0xffffffffL])
        self.window.change_property(self._NET_WM_NAME, Xatom.STRING, 8, 
                "Pynel\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0")

        self.window.change_property(self._WIN_STATE, Xatom.CARDINAL, 32, [1])

        self.window.change_property(self._NET_WM_WINDOW_TYPE,
            Xatom.ATOM, 32, [self._NET_WM_WINDOW_TYPE_DOCK])

        self.window.change_property(self._NET_WM_STATE, Xatom.ATOM, 32,
                [1, self._NET_WM_STATE_STICKY])

        #self.window.change_property(self._MOTIF_WM_HINTS,
        #        self._MOTIF_WM_HINTS, 32, [0x2, 0x0, 0x0, 0x0, 0x0])

        self.window.change_property(self._NET_WM_STATE, Xatom.ATOM, 32,
                [1, self._NET_WM_STATE_SKIP_PAGER])
        self.window.change_property(self._NET_WM_STATE, Xatom.ATOM, 32,
                [1, self._NET_WM_STATE_SKIP_TASKBAR])
        self.window.change_property(self._NET_WM_STATE, Xatom.ATOM, 32,
                [1, self._NET_WM_STATE_ABOVE])

    def _update_struts(self):
        self.window.change_property(self._NET_WM_STRUT, Xatom.CARDINAL, 32,
                [0, 0, self.height, 0])
        self.window.change_property(self._NET_WM_STRUT_PARTIAL, Xatom.CARDINAL, 32,
                [0, 0, 0, self.height, 0, 0, 0, 0, 0, 0, 0, self.width])

    def send_event(self, win, ctype, data, mask=None):
        data = (data+[0]*(5-len(data)))[:5]
        ev = Xlib.protocol.event.ClientMessage(window=win, client_type=ctype, data=(32,(data)))

        if not mask:
            mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
        self.root.send_event(ev, event_mask=mask)


    def schedule(self, timeout, func):
        heapq.heappush(self._timers, (timeout + int(time.time()), func))

    def _init_widgets(self):
        for w in self.left:
            w.parent = self
            w.setup()

        for w in self.right:
            w.parent = self
            w.setup()

    def mainloop(self):
        self._init_widgets()
        self._update_background()

        poll = select.poll()
        poll.register(self.display.display.socket, select.POLLIN)

        timeout = 0
        while True:
            if self._update:
                self._redraw()
                self._update = False

            p = poll.poll(timeout*1000)
            if p:
                while self.display.pending_events():
                    e = self.display.next_event()
                    print e
                    for func in self.events[e.type]:
                        func(e)

            if len(self._timers) > 0:
                now = time.time()
                while self._timers[0][0] <= now:
                    timeout, func = heapq.heappop(self._timers)
                    func()

                timeout = max(self._timers[0][0] - time.time(), 1)
            else:
                timeout = -1


    def _update_background(self, *_):
        """ Check and update the panel background if necessary """
        root_map = self.root.get_full_property(self._XROOTPMAP_ID, Xatom.PIXMAP)

        if hasattr(root_map, "value"):
            root_map = root_map.value[0]
        else:
            root_map = self.root.id

        if self.root_map != root_map:
            self.root_map = root_map
            r = self.bg >> 16
            g = (self.bg >> 8) & 0xff
            b = self.bg & 0xff
            ppshade(self.window.id, root_map, 
                    self.x, self.y, self.width, self.height,
                    r, g, b, self.shade)
        self.update()

    def _redraw(self, *_):
        print "drawing"
        self.clear(0, 0, self.width, self.height)
        space = self.width
        leftx = 0
        for w in self.left:
            wh = w.min_width
            print "left:", wh
            w.x = leftx
            w.width = wh
            w.draw()
            leftx += wh
            space -= wh

        rightx = self.width
        for w in self.right:
            wh = w.min_width
            w.x = rightx - wh
            w.width = wh
            w.draw()
            rightx -= wh
            space -= wh

    def clear(self, x1, y1, x2, y2):
        ppclear(self.window.id, x1, y1, x2, y2)

    def draw_text(self, x, text, color=None):
        if color is None:
            color = self.fg
        ppfont(self.window.id, color, x, self.height, 0, text)

    def text_width(self, text):
        return ppfontsize(text)

    def update(self):
        """ set the flag so that we redraw """
        self._update = True


if __name__ == "__main__":
    pynel = Pynel()

    pynel.left.append(Desktop(0xff0000))
    pynel.left.append(Systray())
    pynel.right.append(Clock())
    pynel.right.append(Text(" | ", 0x00dd00))
    pynel.right.append(CPU(2))
    pynel.right.append(Text(" / ", 0x000000))
    pynel.right.append(CPU(1))

    pynel.mainloop()

