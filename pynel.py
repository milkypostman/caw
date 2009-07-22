#!/usr/bin/python -OO

#from cpynel import cinit, cshade, cicon, cfont, cfontsize, cclear, cflush, crectangle, cfillrectangle
import ctypes
#import Xlib
#import Xlib.display
#import Xlib.error
#import Xlib.protocol.event
import const
import collections
import heapq
import select
import time
import re
import operator
import itertools
import math

FONT            = "bitstream vera sans-8"
FONT            = "terminus-8"
class Widget(object):
    def __init__(self):
        super(Widget, self).__init__()
        self.width = 0
        self.x = 0
        self.min_width = 0
        self.parent = None

    def setup(self):
        pass

    def draw(self):
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
        print "setup"
        a = self.parent.get_atoms([
            "_NET_CURRENT_DESKTOP",
            "_NET_WM_DESKTOP",
            "_NET_DESKTOP_NAMES",
            "UTF8_STRING",
            "STRING",
            "_NET_NUMBER_OF_DESKTOPS"])

        for key,val in a.iteritems():
            setattr(self, key, val)

        self.parent.atoms[self._NET_WM_DESKTOP].append(self._update)
        self.parent.atoms[self._NET_CURRENT_DESKTOP].append(self._update)
        self._get_desktops()
        #if self.fg is None:
        #    self.fg = self.parent.fg
        #if self.current_fg is None:
        #    self.current_fg = self.parent.fg

        #if self.current_bg is not None or self.bg is not None:
        #    self.gc = self.parent.root.create_gc()

        self._update()

    def _get_desktops(self):
        print "get desk"
        totalc = xcb.xcb_get_property(self.parent.connection, 0,
                self.parent.screen.root,
                self._NET_NUMBER_OF_DESKTOPS,
                const.CARDINAL,
                0,
                32)
        namesc = xcb.xcb_get_property(self.parent.connection, 0,
                self.parent.screen.root,
                self._NET_DESKTOP_NAMES,
                self.UTF8_STRING,
                0,
                32)

        print self.STRING
        print self.UTF8_STRING

        totalrp = xcb.xcb_get_property_reply(self.parent.connection, totalc, None)
        namesrp = xcb.xcb_get_property_reply(self.parent.connection, namesc, None)

        total = ctypes.cast(xcb.xcb_get_property_value(totalrp),
                ctypes.POINTER(ctypes.c_uint32 * xcb.xcb_get_property_value_length(totalrp))).contents[0]


        names = ''.join(ctypes.cast(xcb.xcb_get_property_value(namesrp),
            ctypes.POINTER(ctypes.c_char*xcb.xcb_get_property_value_length(namesrp))).contents).strip("\x00").split("\x00")
        self.desktops = names

        xcb.free(totalrp)
        xcb.free(namesrp)

        self.min_width = len(self._output())

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
        currc = xcb.xcb_get_property(self.parent.connection, 0,
                self.parent.screen.root,
                self._NET_CURRENT_DESKTOP,
                const.CARDINAL,
                0,
                32)
        currrp = xcb.xcb_get_property_reply(self.parent.connection, currc, None)
        self.current = ctypes.cast(xcb.xcb_get_property_value(currrp),
                ctypes.POINTER(ctypes.c_uint32 * xcb.xcb_get_property_value_length(currrp))).contents[0]
        xcb.free(currrp)

        #if event is None:
        #    self.current = self.parent.root.get_full_property(self._NET_CURRENT_DESKTOP, Xatom.CARDINAL).value[0]

        #if hasattr(event, "window"):
        #    try:
        #        self.current = event.window.get_full_property(self._NET_CURRENT_DESKTOP, Xatom.CARDINAL).value[0]
        #    except:
        #        try:
        #            self.current = event.window.get_full_property(self._BLACKBOX, 0).value[2]
        #        except:
        #            self.current = 0

        self.parent.update()


    def draw(self):
        color = self.fg
        curx = self.x
        for i, name in enumerate(self.desktops):
            if i == self.current:
                out = "<" + name + ">"
                color = self.current_fg
                width = self.parent.text_width(out)
        #        if self.current_bg is not None:
        #            #self.gc.change(foreground=self.current_bg)
        #            #print curx, curx+width-1
        #            #cfillrectangle(self.parent.window.id, self.current_bg, curx, self.parent.border, width-1, self.parent.height - self.parent.border*2)
            else:
                out = " " + name + " "
                color = self.fg
                width = self.parent.text_width(out)
        #        if self.bg is not None:
        #            #self.gc.change(foreground=self.bg)
        #            #print curx, curx+width
        #            #self.parent.window.fill_rectangle(self.gc, curx, self.parent.border, width-1, self.parent.height - self.parent.border*2)
        #            #cfillrectangle(self.parent.window.id, self.bg, curx, self.parent.border, width-1, self.parent.height - self.parent.border*2)

            self.parent.draw_text(curx, out, color)
            curx += self.parent.text_width(out)


"""

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
        for task in self.tasks:
            print "drawing task:",task
            t = self.tasks[task]
            t['x'] = curx
            t['y'] = (self.parent.height - t['height'])/2
            t['window'].configure(onerror=self.error_handler, x=t['x'], y=t['y'], width=t['width'], height=t['height'])
            t['window'].map(onerror=self.error_handler)
            curx += t['width']
        """

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

xcb_window_t = ctypes.c_uint32
xcb_colormap_t = ctypes.c_uint32
xcb_visualid_t = ctypes.c_uint32
xcb_pixmap_t = ctypes.c_uint32
xcb_atom_t = ctypes.c_uint32
xcb_timestamp_t = ctypes.c_uint32

class xcb_intern_atom_reply_t(ctypes.Structure):
   _fields_ = [('response_type', ctypes.c_uint8),
    ('pad0', ctypes.c_uint8),
    ('sequence', ctypes.c_uint16),
    ('length', ctypes.c_uint32),
    ('atom', ctypes.c_uint32)]

class xcb_intern_atom_cookie_t( ctypes.Structure ):
    _fields_ = [('sequence', ctypes.c_uint)]

class xcb_screen_t(ctypes.Structure):
    _fields_ = [
        ("root", xcb_window_t),
        ("default_colormap", xcb_colormap_t),

        ("white_pixel", ctypes.c_uint32),
        ("black_pixel", ctypes.c_uint32),
        ("current_input_masks", ctypes.c_uint32),

        ("width_in_pixels", ctypes.c_uint16),
        ("height_in_pixels", ctypes.c_uint16),
        ("width_in_millimeters", ctypes.c_uint16),
        ("height_in_millimeters", ctypes.c_uint16),
        ("min_installed_maps", ctypes.c_uint16),
        ("max_installed_maps", ctypes.c_uint16),

        ("root_visual", xcb_visualid_t),

        ("backing_stores", ctypes.c_uint8),
        ("save_unders", ctypes.c_uint8),
        ("root_depth", ctypes.c_uint8),
        ("allowed_depths_len", ctypes.c_uint8)
        ]

class xcb_screen_iterator_t(ctypes.Structure):
    _fields_ = [
            ('data', ctypes.POINTER(xcb_screen_t)),
            ('rem', ctypes.c_int),
            ('index', ctypes.c_int)
            ]

class xcb_wm_hints_t(ctypes.Structure):
    _fields_ = [
            ('flags', ctypes.c_int32),
            ('input', ctypes.c_uint32),
            ('initial_state', ctypes.c_int32),
            ('icon_pixmap', xcb_pixmap_t),
            ('icon_window', xcb_window_t),
            ('icon_x', ctypes.c_int32),
            ('icon_y', ctypes.c_int32),
            ('icon_mask', xcb_pixmap_t),
            ('window_group', xcb_window_t),
            ]

class xcb_generic_event_t(ctypes.Structure):
    _fields_ = [
            ('response_type', ctypes.c_uint8),
            ('pad0', ctypes.c_uint8),
            ('sequence', ctypes.c_uint16),
            ('pad', ctypes.c_uint32*7),
            ('full_sequence', ctypes.c_uint32),
            ]

class xcb_property_notify_event_t(ctypes.Structure):
    _fields_ = [
            ('response_type', ctypes.c_uint8),
            ('pad0', ctypes.c_uint8),
            ('sequence', ctypes.c_uint16),
            ('window', xcb_window_t),
            ('atom', xcb_atom_t),
            ('time', xcb_timestamp_t),
            ('state', ctypes.c_uint8),
            ('pad1', ctypes.c_uint8*3)
            ]

class xcb_size_hints_t(ctypes.Structure):
    _fields_ = [
            ('flags', ctypes.c_uint32),
            ('x', ctypes.c_int32),
            ('y', ctypes.c_int32),
            ('width', ctypes.c_int32),
            ('height', ctypes.c_int32),
            ('min_width', ctypes.c_int32),
            ('min_height', ctypes.c_int32),
            ('max_width', ctypes.c_int32),
            ('max_height', ctypes.c_int32),
            ('width_inc', ctypes.c_int32),
            ('height_inc', ctypes.c_int32),
            ('min_aspect_num', ctypes.c_int32),
            ('min_aspect_den', ctypes.c_int32),
            ('max_aspect_num', ctypes.c_int32),
            ('max_aspect_den', ctypes.c_int32),
            ('base_width', ctypes.c_int32),
            ('base_height', ctypes.c_int32),
            ('win_gravity', ctypes.c_uint32),
            ]

class xcb_charinfo_t(ctypes.Structure):
    _fields_ = [
            ('left_side_bearing', ctypes.c_int16),
            ('right_side_bearing', ctypes.c_int16),
            ('character_width', ctypes.c_int16),
            ('ascent', ctypes.c_int16),
            ('descent', ctypes.c_int16),
            ('attributes', ctypes.c_uint16),
            ]

class xcb_query_font_reply_t(ctypes.Structure):
    _fields_ = [
            ('response_type', ctypes.c_uint8),
            ('pad0', ctypes.c_uint8),
            ('sequence', ctypes.c_uint16),
            ('length', ctypes.c_uint32),
            ('min_bounds', xcb_charinfo_t),
            ('pad1', ctypes.c_uint8),
            ('max_bounds', xcb_charinfo_t),
            ('pad2', ctypes.c_uint8),
            ('min_char_or_byte2', ctypes.c_uint16),
            ('max_char_or_byte2', ctypes.c_uint16),
            ('default_char', ctypes.c_uint16),
            ('properties_len', ctypes.c_uint16),
            ('draw_direction', ctypes.c_uint8),
            ('min_byte1', ctypes.c_uint8),
            ('max_byte1', ctypes.c_uint8),
            ('all_chars_exist', ctypes.c_uint8),
            ('font_ascent', ctypes.c_uint16),
            ('font_descent', ctypes.c_uint16),
            ('char_infos_len', ctypes.c_uint32),
            ]

class cairo_text_extents_t(ctypes.Structure):
    _fields_ = [
            ('x_bearing', ctypes.c_double),
            ('y_bearing', ctypes.c_double),
            ('width', ctypes.c_double),
            ('height', ctypes.c_double),
            ('x_advance', ctypes.c_double),
            ('y_advance', ctypes.c_double),
            ]

class cairo_font_extents_t(ctypes.Structure):
    _fields_ = [
            ('ascent', ctypes.c_double),
            ('descent', ctypes.c_double),
            ('height', ctypes.c_double),
            ('max_x_advance', ctypes.c_double),
            ('max_y_advance', ctypes.c_double),
            ]

class xcb_get_window_attributes_reply_t(ctypes.Structure):
    _fields_ = [
            ('response_type', ctypes.c_uint8),
            ('backing_store', ctypes.c_uint8),
            ('sequence', ctypes.c_uint16),
            ('length', ctypes.c_uint32), 
            ('visual', xcb_visualid_t), 
            ('_class', ctypes.c_uint16), 
            ('bit_gravity', ctypes.c_uint8),
            ('win_gravity', ctypes.c_uint8),
            ('backing_planes', ctypes.c_uint32), 
            ('backing_pixel', ctypes.c_uint32),
            ('save_under', ctypes.c_uint8), 
            ('map_is_installed', ctypes.c_uint8),
            ('map_state', ctypes.c_uint8),
            ('override_redirect', ctypes.c_uint8),
            ('colormap', xcb_colormap_t),
            ('all_event_masks', ctypes.c_uint32),
            ('your_event_mask', ctypes.c_uint32),
            ('do_not_propagate_mask', ctypes.c_uint16),
            ('pad0', ctypes.c_uint8 * 2)
            ]

xcb = ctypes.cdll.LoadLibrary('libxcb.so')
xcbatom = ctypes.cdll.LoadLibrary('libxcb-atom.so')
xcbicccm = ctypes.cdll.LoadLibrary('libxcb-icccm.so')
xcbaux = ctypes.cdll.LoadLibrary('libxcb-aux.so')

cairo = ctypes.cdll.LoadLibrary('libcairo.so')

class Pynel(object):
    def __init__(self):
        super(Pynel, self).__init__()

        screen_nbr = ctypes.c_int()

        self.connection = xcb.xcb_connect(None, ctypes.byref(screen_nbr));

        # don't free setup
        setup = xcb.xcb_get_setup(self.connection)
        xcb.xcb_setup_roots_iterator.restype = xcb_screen_iterator_t
        iter = xcb.xcb_setup_roots_iterator(setup)

        self.screen = iter.data.contents
        print "Found Screen:", self.screen.width_in_pixels, "x", self.screen.height_in_pixels


        self.events = collections.defaultdict(list)
        self.atoms = collections.defaultdict(list)
        self._timers = []
        self._colors = {}
        self.colors = {}

        self.xlib = ctypes.cdll.LoadLibrary("libX11.so")

        self.width = self.screen.width_in_pixels
        self.border = 2
        self.height = 10 + self.border*2
        self.border_color = 0xffffff
        self.x = 0
        self.location = 0
        if not self.location:
            self.y = self.screen.height_in_pixels - self.height
        else:
            self.y = 0

        self.bg = 0x000000
        self.fg = 0xcccccc
        self.shade = 50

        self.left = []
        self.right = []

        self._update = False
        self._background_needs_update = 0

        self._init_window()
        self._init_cairo()
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

        self._set_props()
        self._update_struts()
        self._init_root_pixmap()

        self.events[const.XCB_EXPOSE].append(self._redraw)
        self.events[const.XCB_PROPERTY_NOTIFY].append(self._property_notify)
        self.atoms[self._XROOTPMAP_ID].append(self._update_background)

        self._update_background()

        xcb.xcb_map_window(self.connection, self.window)
        xcb.xcb_flush(self.connection)

    def _init_window(self):
        self._back_pixmap = xcb.xcb_generate_id(self.connection)
        xcb.xcb_create_pixmap(self.connection,
                self.screen.root_depth,
                self._back_pixmap,
                self.screen.root,
                self.width,
                self.height)

        self.window = xcb.xcb_generate_id(self.connection)
        xcb.xcb_create_window(self.connection,
                self.screen.root_depth,
                self.window,
                self.screen.root,
                self.x, self.y,
                self.width, self.height,
                0,
                const.XCB_WINDOW_CLASS_INPUT_OUTPUT,
                self.screen.root_visual,
                ctypes.c_uint32(const.XCB_CW_BACK_PIXMAP | const.XCB_CW_EVENT_MASK), 
                (ctypes.c_uint32 * 2)(self._back_pixmap, 
                    const.XCB_EVENT_MASK_EXPOSURE | const.XCB_EVENT_MASK_BUTTON_PRESS | 
                    const.XCB_EVENT_MASK_ENTER_WINDOW | const.XCB_EVENT_MASK_BUTTON_RELEASE))

        self._gc = xcb.xcb_generate_id(self.connection)
        self._font = xcb.xcb_generate_id(self.connection)
        xcb.xcb_open_font_checked(self.connection,
                self._font, len("-artwiz-nu-*-*-*-*-*-*-*-*-*-*-*-*"), 
                "-artwiz-nu-*-*-*-*-*-*-*-*-*-*-*-*")
        xcb.xcb_create_gc(self.connection, self._gc, self.window, 
                const.XCB_GC_FOREGROUND| const.XCB_GC_BACKGROUND|const.XCB_GC_FONT,
                (ctypes.c_uint32 * 3)(self.screen.white_pixel, self.screen.black_pixel, self._font))

        self._vistype = xcbaux.xcb_aux_get_visualtype(self.connection, 0,
                self.screen.root_visual)


    def _init_root_pixmap(self):
        prop_cookie = xcb.xcb_get_property(self.connection, 0,
                self.screen.root,
                self._XROOTPMAP_ID,
                const.PIXMAP,
                0,
                10)

        xcb.xcb_change_window_attributes(self.connection,
                self.screen.root,
                const.XCB_CW_EVENT_MASK,
                ctypes.pointer(ctypes.c_uint32(const.XCB_EVENT_MASK_PROPERTY_CHANGE)))


        rp = xcb.xcb_get_property_reply(self.connection, prop_cookie, None)

        self.root_pixmap = ctypes.cast(xcb.xcb_get_property_value(rp), 
                ctypes.POINTER(ctypes.c_uint32 * xcb.xcb_get_property_value_length(rp))).contents[0]

        xcb.free(rp)

    def _init_cairo(self):
        cs = cairo.cairo_xcb_surface_create(self.connection,
                self.window,
                self._vistype,
                self.width,
                self.height)
        self.cairo_window = cairo.cairo_create(cs)
        cairo.cairo_select_font_face (self.cairo_window, "Terminus", const.CAIRO_FONT_SLANT_NORMAL, const.CAIRO_FONT_WEIGHT_BOLD);
        cairo.cairo_set_font_size (self.cairo_window, ctypes.c_double(8));
        fe = cairo_font_extents_t()
        cairo.cairo_font_extents(self.cairo_window, ctypes.pointer(fe));
        self.cairo_text_height = fe.ascent
        cairo.cairo_surface_destroy(cs)

        cs = cairo.cairo_xcb_surface_create(self.connection,
                self._back_pixmap,
                self._vistype,
                self.width,
                self.height)

        self.cairo_back_pixmap = cairo.cairo_create(cs)
        cairo.cairo_surface_destroy(cs)

    def _property_notify(self, e):
        print "************ PROPERTY NOTIFY ************"
        e = ctypes.cast(e, ctypes.POINTER(xcb_property_notify_event_t))
        for func in self.atoms[e.contents.atom]:
            print "Found functions"
            func(e)

    def get_atoms(self, atoms):
        # get all the atoms we need
        cookies = []
        for a in atoms:
            cookies.append(xcb.xcb_intern_atom(self.connection, 0, len(a), a));

        ret = {}

        # get the replies (properly)
        xcb.xcb_intern_atom_reply.restype = ctypes.POINTER(xcb_intern_atom_reply_t)
        for c,a in zip(cookies, atoms):
            reply = xcb.xcb_intern_atom_reply(self.connection, c, None);
            ret[a] = reply.contents.atom
            xcb.free(reply)

        return ret


    def _set_props(self):
        xcbicccm.xcb_set_wm_name( self.connection,
                self.window,
                const.STRING,
                len("Pynel"),
                "Pynel")

        xcb.xcb_change_property(self.connection,
                const.XCB_PROP_MODE_REPLACE,
                self.window,
                const.WM_CLASS,
                const.STRING,
                8,
                len("pynel\0Pynel\0"),
                "pynel\0Pynel\0")


        wm_hints_cookie = xcbicccm.xcb_get_wm_hints(self.connection, self.window)
        wm_normal_cookie = xcbicccm.xcb_get_wm_normal_hints(self.connection, self.window)

        hints = ctypes.pointer(xcb_wm_hints_t())
        size_hints = ctypes.pointer(xcb_size_hints_t())

        xcbicccm.xcb_get_wm_hints_reply(self.connection, wm_hints_cookie, hints, None)
        xcbicccm.xcb_get_wm_normal_hints_reply(self.connection, wm_normal_cookie, size_hints, None)

        xcbicccm.xcb_wm_hints_set_input(hints, 0)
        xcbicccm.xcb_wm_hints_set_normal(hints)
        xcbicccm.xcb_set_wm_hints(self.connection, self.window, hints)

        size_hints.contents.flags = size_hints.contents.flags | const.XCB_SIZE_HINT_P_POSITION
        xcbicccm.xcb_size_hints_set_min_size(size_hints, 10, 10)
        xcbicccm.xcb_size_hints_set_max_size(size_hints, self.width, self.height)
        xcbicccm.xcb_set_wm_normal_hints(self.connection, self.window, size_hints)

        xcb.xcb_change_property(self.connection,
                const.XCB_PROP_MODE_REPLACE,
                self.window,
                self._NET_WM_WINDOW_TYPE,
                const.ATOM,
                32,
                1,
                ctypes.pointer(ctypes.c_uint32(self._NET_WM_WINDOW_TYPE_DOCK)))

        xcb.xcb_change_property(self.connection,
                const.XCB_PROP_MODE_REPLACE,
                self.window,
                self._NET_WM_DESKTOP,
                const.CARDINAL,
                32,
                1,
                ctypes.pointer(ctypes.c_uint32(0xffffffffL)))

        xcb.xcb_change_property(self.connection,
                const.XCB_PROP_MODE_REPLACE,
                self.window,
                self._WIN_STATE,
                const.CARDINAL,
                32,
                1,
                ctypes.pointer(ctypes.c_uint32(1)))

        xcb.xcb_change_property(self.connection,
                const.XCB_PROP_MODE_REPLACE,
                self.window,
                self._WIN_STATE,
                const.STRING,
                8,
                len("Pynelpoo"),
                "Pynelpoo")

        xcb.xcb_change_property(self.connection,
                const.XCB_PROP_MODE_REPLACE,
                self.window,
                self._NET_WM_STATE,
                const.ATOM,
                32,
                4,
                (ctypes.c_uint32 * 4)(self._NET_WM_STATE_SKIP_PAGER,
                    self._NET_WM_STATE_SKIP_TASKBAR,
                    self._NET_WM_STATE_STICKY,
                    self._NET_WM_STATE_ABOVE))

    def _update_struts(self):
        xcb.xcb_change_property(self.connection,
                const.XCB_PROP_MODE_REPLACE,
                self.window,
                self._NET_WM_STRUT,
                const.CARDINAL,
                32,
                4,
                (ctypes.c_uint32 * 4)(
                    0, 0, self.height, 0))

        xcb.xcb_change_property(self.connection,
                const.XCB_PROP_MODE_REPLACE,
                self.window,
                self._NET_WM_STRUT_PARTIAL,
                const.CARDINAL,
                32, 12,
                (ctypes.c_uint32 * 12)(
                    0, 0, 0, self.height, 0, 0, 0, 0, 0, 0, 0, self.width
                    ))

        #self.window.change_property(self._MOTIF_WM_HINTS,
        #        self._MOTIF_WM_HINTS, 32, [0x2, 0x0, 0x0, 0x0, 0x0])


    def send_event(self, win, ctype, data, mask=None):
        data = (data+[0]*(5-len(data)))[:5]
        #ev = Xlib.protocol.event.ClientMessage(window=win, client_type=ctype, data=(32,(data)))

        if not mask:
            mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
            #self.root.send_event(ev, event_mask=mask)


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

        poll = select.poll()
        poll.register(xcb.xcb_get_file_descriptor(self.connection), select.POLLIN)

        xcb.xcb_poll_for_event.restype = ctypes.POINTER(xcb_generic_event_t)

        timeout = 0
        while True:
            if self._update:
                self._redraw()
                self._update = False
                xcb.xcb_flush(self.connection)

            p = poll.poll(timeout*1000)
            if p:
                evt = xcb.xcb_poll_for_event(self.connection)
                while evt:
                    print "Event:", evt.contents.response_type
                    for func in self.events[evt.contents.response_type]:
                        func(evt)
                    xcb.free(evt)
                    evt = xcb.xcb_poll_for_event(self.connection)

            if len(self._timers) > 0:
                now = time.time()
                while self._timers[0][0] <= now:
                    timeout, func = heapq.heappop(self._timers)
                    func()

                timeout = max(self._timers[0][0] - time.time(), 1)
            else:
                timeout = -1



    def _alloc_color(self, color):
        if color in self._colors:
            return self._colors[color]
        else:
            r = (color >> 16) * 257
            g = ((color >> 8) & 0xff) * 257
            b = (color & 0xff) * 257

            c = self.screen.default_colormap.alloc_color(r, g, b)

            if not c:
                sys.stderr.write("Error allocating color: %s\n" % color)
                return self.screen.white_pixel
            else:
                self._colors[color] = c.pixel
                return c.pixel


    def _update_background(self, *_):
        print "updating background"
        xcb.xcb_copy_area(
                self.connection,
                self.root_pixmap,
                self._back_pixmap,
                self._gc,
                self.x, self.y,
                0,0,
                self.width,
                self.height)
        cairo.cairo_set_source_rgba(self.cairo_back_pixmap, 
                ctypes.c_double(0.0),
                ctypes.c_double(0.0),
                ctypes.c_double(0.0),
                ctypes.c_double(0.3))
        cairo.cairo_rectangle(self.cairo_back_pixmap, 
                ctypes.c_double(0.0),
                ctypes.c_double(0.0),
                ctypes.c_double(self.width),
                ctypes.c_double(self.height))
        cairo.cairo_fill(self.cairo_back_pixmap)
        cairo.cairo_set_line_width(self.cairo_back_pixmap, ctypes.c_double(1))
        cairo.cairo_set_source_rgba(self.cairo_back_pixmap, 
                ctypes.c_double(1.0),
                ctypes.c_double(1.0),
                ctypes.c_double(1.0),
                ctypes.c_double(1.0))
        cairo.cairo_rectangle(self.cairo_back_pixmap, 
                ctypes.c_double(0.0),
                ctypes.c_double(0.0),
                ctypes.c_double(self.width),
                ctypes.c_double(self.height))
        cairo.cairo_stroke(self.cairo_back_pixmap)

    def _redraw(self, *_):
        #if self._background_needs_update:
        #    self._update_background()
        #    self._background_needs_update -= 1
        self.clear(0, 0, self.width, self.height)
        space = self.width-self.border*2
        leftx = self.border
        for w in self.left:
            wh = w.min_width
            w.x = leftx
            w.width = wh
            w.draw()
            leftx += w.width
            space -= w.width

        rightx = self.width - self.border
        for w in self.right:
            wh = w.min_width
            w.x = rightx - wh
            w.width = wh
            w.draw()
            rightx -= w.width
            space -= w.width

    def clear(self, x, y, w, h):
        xcb.xcb_clear_area(self.connection, 0, self.window, x, y, w, h)

    def draw_text(self, x, text, color=None):
        if color is None:
            color = self.fg

        r = ctypes.c_double(float(color >> 16)/0xff)
        g = ctypes.c_double(float(color >> 8 & 0xff)/0xff)
        b = ctypes.c_double(float(color & 0xff)/0xff)

        cairo.cairo_set_source_rgb (self.cairo_window, r, g, b);
        y =  (self.height - 2 + self.cairo_text_height)/2
        cairo.cairo_move_to(self.cairo_window, ctypes.c_double(x), ctypes.c_double(y))
        cairo.cairo_show_text (self.cairo_window, text);

    def text_width(self, text):
        te = cairo_text_extents_t()
        cairo.cairo_text_extents(self.cairo_window, text, ctypes.byref(te));
        return te.width

    def update(self):
        self._update = True

if __name__ == "__main__":
    pynel = Pynel()

    pynel.left.append(Desktop())
    pynel.right.append(Clock())
    pynel.right.append(Text(" | ", 0x00dd00))
    pynel.right.append(CPU(2))
    pynel.right.append(Text(" / ", 0x000000))
    pynel.right.append(CPU(1))

    pynel.mainloop()
