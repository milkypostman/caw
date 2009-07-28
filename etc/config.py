import socket

from caw import Caw
from caw.widgets.spacer import Spacer
from caw.widgets.text import Text
from caw.widgets.battery import Battery
from caw.widgets.volume import Volume
from caw.widgets.clock import Clock
from caw.widgets.cpu import CPU
from caw.widgets.systray import Systray
from caw.widgets.allornothing import AllOrNothing
from caw.widgets.desktop import Desktop

c = Caw(
        font_face='gelly',
        font_size=10,
        fg_color=0x636363,
        bg_color=0x181818,
        shading=256/4 * 3,
        border_color=0x303030,
        height=10,
        border_width=1,
        edge=0
        )

hostname = socket.gethostname()

c.widgets = []

#c.widgets.append(Spacer(3))
c.widgets.append(Desktop(showall=False, current_fg=0x0090b4))

c.widgets.append(Spacer(3))
c.widgets.append(AllOrNothing(
    Text(" :: ", 0xcf49eb),
    Systray())
    )

c.widgets.append(Spacer(-1))
#c.widgets.append(Tasklist())
c.widgets.append(CPU(1, fg_color=0xdddddd))
c.widgets.append(Text(" : ", 0x777777))
c.widgets.append(CPU(2, fg_color=0xdddddd))

c.widgets.append(Text(" :: ", 0xcf49eb))

if hostname == 'murdock':
    c.widgets.append(Battery(fg_color=0x9f78ff))
    c.widgets.append(Text(" :: ", 0xcf49eb))

#c.widgets.append(Volume(device='PCM'))
if hostname == 'baracus':
    c.widgets.append(Text(" ", 0x777777))
#    c.widgets.append(Volume(percent_color=0xaaaaaa))

c.widgets.append(Text(" :: ", 0xcf49eb))

c.widgets.append(Clock(format='%Y.%m.%d', color=0xdddddd))
c.widgets.append(Text(" "))
c.widgets.append(Clock(format='%H:%M:%S', color=0xffffff))
c.widgets.append(Spacer(3))

c.mainloop()
