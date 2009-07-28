import caw
import xcb
import struct
import xcb.xproto as xproto

class Tasklist(caw.Widget):
    def __init__(self, alldesktops=False):
        super(Tasklist, self).__init__()
        self.alldesktops = alldesktops
        self.clients = {}
        self.current_desktop = None
        self.current_client = None
        self.trim_length = 0
        self.spacing = 5
        self.width_hint = -1

    def init(self, parent):
        super(Tasklist, self).init(parent)
        a = self.parent.get_atoms([
            "_NET_WM_DESKTOP",
            "_NET_CURRENT_DESKTOP",
            "_NET_CURRENT_DESKTOP",
            "_NET_WM_NAME",
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
        if id in self.clients:
            del self.clients[id]
        self.parent.update()

    def _update_focus(self, evt):
        id = evt.event
        self.current_client = id
        self.parent.update()

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
            self.clients[id]['desktop'] = struct.unpack_from('I',r.value.buf())[0]
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

        for id in clients:
            if id not in self.clients:
                classes[id] = conn.core.GetProperty(0, id, xcb.XA_WM_CLASS, xcb.XA_STRING, 0, 2**16)
                desktops[id] = conn.core.GetProperty(0, id, self._NET_WM_DESKTOP, xcb.XA_CARDINAL, 0, 12)
                names[id] = conn.core.GetProperty(0, id, xcb.XA_WM_NAME, xcb.XA_STRING, 0, 2**16)
                #names[id] = conn.core.GetProperty(0, id, self._NET_WM_NAME, xcb.XA_STRING, 0, 2**16)

        for id in classes:
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

            client = dict(id = id, name = clientname, desktop = clientdesk, cls=clientcls)

            self.clients[id] = client
        self.parent.update()

    def _output(self):
        if self.alldesktops:
            return ' '.join(
                    (c['name'] for c in self.clients.itervalues()))

        return ' '.join(
                (c['name'] for c in self.clients.itervalues() if
                    c['desktop'] == self.current_desktop))

    def draw(self):
        clients = [c for c in self.clients.itervalues() if self.alldesktops or c['desktop'] == self.current_desktop]
        availwidth = self.width - (len(clients)-1) * self.spacing

        percli = availwidth / len(clients)
        dots = self.parent.text_width('...')
        curx = self.x
        for c in clients:
            color = None
            cliavail = percli
            if c['id'] ==  self.current_client:
                color = 0xff0000

            if self.parent.text_width(c['name']) <= cliavail:
                self.parent.draw_text(c['name'], color, curx)
                curx += self.parent.text_width(c['name']) + self.spacing
            else:
                cliavail -= dots
                trim = -1
                while self.parent.text_width(c['name'][:trim]) > cliavail:
                    trim -= 1

                self.parent.draw_text(c['name'][:trim] + '...', color, curx)
                curx += self.parent.text_width(c['name'][:trim] + '...') + self.spacing


