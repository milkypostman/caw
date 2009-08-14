import caw.widget
import xcb
import xcb.xproto as xproto
import struct
import caw.cawc as cawc

class Systray(caw.widget.Widget):
    def __init__(self, spacing=2, icon_size=None, **kwargs):
        super(Systray, self).__init__(**kwargs)
        self.spacing=spacing
        self.icon_size = icon_size

    def init(self, parent):
        super(Systray, self).init(parent)

        if self.icon_size is None:
            if self.parent.height >= 24:
                self.icon_size = 24
            elif self.parent.height >= 16:
                self.icon_size = 16
            else:
                self.icon_size = self.parent.height - 2*self.parent.border_width

        self.tasks = {}

        conn = self.parent.connection
        scr = self.parent.screen
        self.parent.events[xproto.ClientMessageEvent].append(self._clientmessage)
        self.parent.events[xproto.ConfigureNotifyEvent].append(self._configurenotify)
        self.parent.events[xproto.DestroyNotifyEvent].append(self._destroynotify)

        a = self.parent.get_atoms([
            "_NET_SYSTEM_TRAY_OPCODE",
            "_NET_SYSTEM_TRAY_S%d" % 0,
            "MANAGER",
            "WM_STATE"
            ])

        for key,val in a.iteritems():
            setattr(self, key, val)

        self.window = conn.generate_id()
        conn.core.CreateWindow(scr.root_depth,
                self.window, self.parent.window,
                -1, -1, 1, 1, 0,
                xproto.WindowClass.CopyFromParent,
                scr.root_visual,
                0,
                [])

        #print "Systray window:", self.window

        e = conn.core.SetSelectionOwnerChecked(self.window, self._NET_SYSTEM_TRAY_S0, xcb.CurrentTime)
        self.parent.send_event(scr.root, self.MANAGER, xcb.CurrentTime, self._NET_SYSTEM_TRAY_S0, self.window)

        # have to manually build the event!
        #response_type = 33 # XCB_CLIENT_MESSAGE
        #format = 32
        #sequence = 0
        #window = scr.root
        #type = self.MANAGER
        #data = [xcb.CurrentTime, self._NET_SYSTEM_TRAY_S0, self.window, 0, 0]
        #event = struct.pack('BBHII5I', response_type, format, sequence, window, type, xcb.CurrentTime, self._NET_SYSTEM_TRAY_S0, self.window, 0, 0)

        #e = conn.core.SendEvent(0, scr.root, 0xffffff, event)
        # FIXME: CONFIRM THIS WORKS
        #e = conn.core.ChangeProperty(xproto.PropMode.Replace, scr.root, self._NET_SYSTEM_TRAY_S0, self.MANAGER, 32, 1, struct.pack("I",self.window))

    def _set_width_hint(self):
        width_hint=self.icon_size*len(self.tasks)+ self.spacing * (len(self.tasks)-1)
        self.width_hint = max(width_hint, 0)

    def _destroynotify(self, event):
        #print "********* DESTROY NOTIFY **************"
        if event.window in self.tasks:
            conn = self.parent.connection
            del self.tasks[event.window]
            self._set_width_hint()


    def _clientmessage(self, event):
        if event.window == self.window:
            #print "!!!!!!!!!!!!! CLIENT MESSAGE !!!!!!!!!!!!!!!"
            opcode = xproto.ClientMessageData(event, 0, 20).data32[2]
            data = xproto.ClientMessageData(event, 12, 20)
            task = data.data32[2]
            if opcode == self._NET_SYSTEM_TRAY_OPCODE:
                conn = self.parent.connection

                #conn.core.ChangeProperty(xproto.PropMode.Replace, task, self.WM_STATE, self.WM_STATE, 32, 2, struct.pack('II', 0, 0))

                #print task
                conn.core.ReparentWindow(task, self.parent.window, 0, 0)
                conn.core.ChangeWindowAttributes(task, xproto.CW.EventMask, [xproto.EventMask.Exposure|xproto.EventMask.StructureNotify])
                conn.flush()
                self.tasks[task] = dict(x=0, y=0, width=self.icon_size, height=self.icon_size)
                self._set_width_hint()
                self.parent.update()

    def _configure_window(self, window, x, y, w, h):
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)

        cawc.xcb_configure_window(self.parent.connection_c,
                window, x, y, w, h)
        return

        #self.parent.connection.core.ConfigureWindow(
        #        window, 
        #        (xproto.ConfigWindow.X |
        #        xproto.ConfigWindow.Y |
        #        xproto.ConfigWindow.Width |
        #        xproto.ConfigWindow.Height),
        #        struct.pack('IIIIIII', x,y,w,h,0,0,0))

    def _configurenotify(self, event):
        #print "********* CONFIGURE NOTIFY **************"
        if event.window in self.tasks:
            #print 'HERES OUR WINDOW!'
            task = self.tasks[event.window]
            conn = self.parent.connection
            self._configure_window(event.window,
                    task['x'], task['y'],
                    task['width'], task['height'])
            self._set_width_hint()
            #conn.core.ChangeWindowAttributes(event.window, xproto.CW.EventMask, [xproto.EventMask.StructureNotify])

    def draw(self):
        curx = self.x

        conn = self.parent.connection
        #self._configure_window(self.window, curx, 0, width, self.parent.height)
        #conn.core.ClearArea(0, self.window, 0, 0, width, self.parent.height)
        #conn.core.MapWindow(self.window)

        for taskwin in self.tasks:
            task = self.tasks[taskwin]
            task['x'] = curx
            task['y'] = (self.parent.height - task['height'])/2
            self._configure_window(taskwin,
                    task['x'], task['y'],
                    task['width'], task['height'])
            conn.core.MapWindow(taskwin)
            conn.flush()
            curx += task['width'] + self.spacing

