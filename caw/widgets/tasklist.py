import caw.widget
import xcb
import struct
import xcb.xproto as xproto
import time

class Tasklist(caw.widget.Widget):
    def __init__(self, alldesktops=False, align='left', padding=5, fg_color=None, fg_current=None, fg_minimized=None, bg_color=None, bg_current=None, bg_minimized=None, border_color=None, border_current=None, border_minimized=None, border_width=1, margin=0, alpha=None, alpha_current=None, alpha_minimized=None, spacing=5, **kwargs):
        super(Tasklist, self).__init__(**kwargs)
        self.alldesktops = alldesktops
        self.clients = {}
        self.current_desktop = None
        self.current_client = None
        self.trim_length = 0

        self.fg_color = fg_color
        self.fg_current = fg_current
        self.fg_minimized = fg_minimized

        self.bg_color = bg_color
        self.bg_current = bg_current
        self.bg_minimized = bg_minimized

        self.alpha = alpha
        self.alpha_current = alpha_current
        self.alpha_minimized = alpha_minimized

        self.border_color = border_color
        self.border_current = border_current
        self.border_minimized = border_minimized
        self.border_width = border_width

        self.padding = padding
        self.margin = margin
        self.spacing = spacing
        self.width_hint = -1
        self.align=dict(left=-1, center=0, right=1).get(align, -1)

    def init(self, parent):
        super(Tasklist, self).init(parent)
        a = self.parent.get_atoms([
            "_NET_WM_DESKTOP",
            "_NET_CURRENT_DESKTOP",
            "_NET_CURRENT_DESKTOP",
            "_NET_WM_NAME",
            "WM_CHANGE_STATE",
            "_NET_WM_STATE",
            "_NET_WM_STATE_HIDDEN",
            "_NET_CLIENT_LIST"])

        for key,val in a.iteritems():
            setattr(self, key, val)

        self._update_clients()
        self._update_current_desktop()

        self.parent.atoms[self._NET_WM_DESKTOP].append(self._update_desktop)
        self.parent.atoms[self._NET_CLIENT_LIST].append(self._update_clients)
        self.parent.atoms[xcb.XA_WM_NAME].append(self._update_name)
        self.parent.events[xproto.FocusInEvent].append(self._update_focus)
        self.parent.events[xproto.DestroyNotifyEvent].append(self._destroynotify)
        self.parent.atoms[self._NET_WM_DESKTOP].append(self._update_current_desktop)
        self.parent.atoms[self._NET_CURRENT_DESKTOP].append(self._update_current_desktop)
        self.parent.atoms[self._NET_WM_STATE].append(self._update_state)

    def _update_current_desktop(self, evt=None):
        conn = self.parent.connection
        scr = self.parent.screen
        currc = conn.core.GetProperty(0, scr.root, self._NET_CURRENT_DESKTOP,
                xcb.XA_CARDINAL, 0, 12)
        currp = currc.reply()
        self.current_desktop = struct.unpack_from("I", currp.value.buf())[0]
        self.parent.update()

    def _destroynotify(self, evt):
        id = evt.window
        #print 'destroy:', id
        if id in self.clients:
            del self.clients[id]
        self.parent.update()

    def _update_focus(self, evt):
        id = evt.event
        self.current_client = id
        self.parent.update()

    def _unhide(self, win):
        conn = self.parent.connection
        conn.core.MapWindow(win)

    def _hide(self, win):
        conn = self.parent.connection
        event = struct.pack('BBHII5I', 33, 32, 0, win, self.WM_CHANGE_STATE, 3,0,0,0,0)
        e = conn.core.SendEventChecked(0, win, 0xffffff, event)
        #print e.check()
        #conn.core.ChangeProperty(xproto.PropMode.Replace, win, self.WM_CHANGE_STATE, xcb.XA_ATOM, 32, 1, struct.pack("I",self._NET_WM_STATE_HIDDEN))

        return

    def _update_state(self, evt):
        #print "*** UPDATE STATE"
        conn = self.parent.connection
        id = evt.window
        if id in self.clients:
            r = conn.core.GetProperty(0, id, self._NET_WM_STATE, xcb.XA_ATOM, 0, 2**16).reply()
            state = struct.unpack_from('%dI' % r.value_len, r.value.buf())
            #print state
            if self._NET_WM_STATE_HIDDEN in state:
                self.clients[id]['hidden'] = True
            else:
                self.clients[id]['hidden'] = False

    def _update_name(self, evt):
        conn = self.parent.connection
        id = evt.window
        if id in self.clients:
            r = conn.core.GetProperty(0, id, xcb.XA_WM_NAME, xcb.XA_STRING, 0, 2**16).reply()
            self.clients[id]['name'] = struct.unpack_from('%ds' % r.value_len, r.value.buf())[0].strip("\x00")
        self.parent.update()

    def _update_desktop(self, evt):
        conn = self.parent.connection
        id = evt.window
        if id in self.clients:
            r = conn.core.GetProperty(0, id, self._NET_WM_DESKTOP, xcb.XA_CARDINAL, 0, 12).reply()
            if r.value_len >= 4:
                self.clients[id]['desktop'] = struct.unpack_from('I',r.value.buf())[0]
            else:
                del self.clients[id]
        self.parent.update()

    def _update_clients(self, *args):
        conn = self.parent.connection
        scr = self.parent.screen
        clientsc = conn.core.GetProperty(0,
                scr.root,
                self._NET_CLIENT_LIST,
                xcb.XA_WINDOW,
                0,
                2**16)

        clientsr = clientsc.reply()
        buf = clientsr.value.buf()
        clients = struct.unpack_from('%dI' %clientsr.value_len, clientsr.value.buf(),0)

        classes = {}
        desktops = {}
        names = {}
        states = {}

        for id in clients:
            if id not in self.clients and id != self.parent.window:
                classes[id] = conn.core.GetProperty(0, id, xcb.XA_WM_CLASS, xcb.XA_STRING, 0, 2**16)
                desktops[id] = conn.core.GetProperty(0, id, self._NET_WM_DESKTOP, xcb.XA_CARDINAL, 0, 12)
                names[id] = conn.core.GetProperty(0, id, xcb.XA_WM_NAME, xcb.XA_STRING, 0, 2**16)
                states[id] = conn.core.GetProperty(0, id, self._NET_WM_STATE, xcb.XA_ATOM, 0, 2**16)
                #names[id] = conn.core.GetProperty(0, id, self._NET_WM_NAME, xcb.XA_STRING, 0, 2**16)

        for id in classes:
            #print "new window:", id
            r = classes[id].reply()
            clientcls = struct.unpack_from('%ds' % r.value_len, r.value.buf())[0].strip("\x00").split("\x00")

            r = desktops[id].reply()
            clientdesk = struct.unpack_from('I',r.value.buf())[0]

            r = names[id].reply()
            clientname = struct.unpack_from('%ds' % r.value_len, r.value.buf())[0].strip("\x00")
            
            conn.core.ChangeWindowAttributes(id, xproto.CW.EventMask, [
                        xproto.EventMask.PropertyChange|
                        xproto.EventMask.FocusChange |
                        xproto.EventMask.StructureNotify])

            r = states[id].reply()
            state = struct.unpack_from('%dI' % r.value_len, r.value.buf())

            hidden = False
            if self._NET_WM_STATE_HIDDEN in state:
                hidden = True

            client = dict(id = id, name = clientname, desktop = clientdesk, cls=clientcls, x=0, width=0, hidden=hidden)

            self.clients[id] = client
        self.parent.update()

    def button1(self, x):
        conn = self.parent.connection
        clients = [c for c in self.clients.itervalues() if self.alldesktops or c['desktop'] == self.current_desktop]
        for c in self.clients.itervalues():
            if self.alldesktops or c['desktop'] == self.current_desktop:
                if c['x'] <= x and x < (c['x'] + c['width']):
                    # found our client
                    #print c['name']
                    win = c['id']
                    conn.core.ConfigureWindow(win, xproto.ConfigWindow.StackMode, [xproto.StackMode.Above])
                    if c['hidden']:
                        self._unhide(win)
                    elif win == self.current_client:
                        self._hide(win)
                    else:
                        conn.core.SetInputFocus(xproto.InputFocus.Parent, win, xcb.CurrentTime)


    def _output(self):
        if self.alldesktops:
            return ' '.join(
                    (c['name'] for c in self.clients.itervalues()))

        return ' '.join(
                (c['name'] for c in self.clients.itervalues() if
                    c['desktop'] == self.current_desktop))

    def draw(self):
        clients = [c for c in self.clients.itervalues() if self.alldesktops or c['desktop'] == self.current_desktop]
        availwidth = self.width - (len(clients)+1) * (self.spacing)

        percli = availwidth
        if len(clients) > 0:
            percli = availwidth / len(clients)

        #print availwidth, percli, self.padding
        dots = self.parent.text_width('...')
        curx = self.x + self.spacing
        for c in clients:
            fg_color = self.fg_color
            c['x'] = curx
            c['width'] = percli
            cliavail = percli
            bg_color = self.bg_color
            border_color = self.border_color
            alpha = self.alpha
            if c['id'] == self.current_client:
                fg_color = self.fg_current
                bg_color = self.bg_current
                border_color = self.border_current
                alpha = self.alpha_current
            elif c['hidden']:
                fg_color = self.fg_minimized
                bg_color = self.bg_minimized
                border_color = self.border_minimized
                alpha = self.alpha_minimized

            if bg_color is not None:
                self.parent.draw_rectangle_filled(curx, self.parent.border_width+self.margin, percli, self.parent.height - 2*self.parent.border_width-2*self.margin-1, bg_color, 255)

            if border_color is not None:
                self.parent.draw_rectangle(curx, self.parent.border_width+self.margin, percli, self.parent.height - 2*self.parent.border_width-2*self.margin-1, border_color, 255, self.border_width)


#            if border_color is not None:
#                self.parent.draw_rectangle(curx-self.padding+self.margin, self.parent.border_width+self.margin, percli+2*self.padding, self.parent.height - 2*self.parent.border_width-2*self.margin-1, 1, border_color, alpha)

            cliavail -= 2*self.padding
            width = self.parent.text_width(c['name'])

            x = curx + self.padding

            #if width <= cliavail:
            #    if self.align==0:
            #        x = curx + (percli - width) / 2
            #    if self.align > 0:
            #        x = curx + percli - width
            self.parent.draw_text(c['name'], fg_color, x, cliavail)
#            else:
#                cliavail -= dots
#                trim = -1
#                while self.parent.text_width(c['name'][:trim]) > cliavail:
#                    trim -= 1
##
#                self.parent.draw_text(c['name'][:trim] + '...', fg_color, x)
            curx += percli + self.spacing


