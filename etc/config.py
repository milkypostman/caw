import socket

from caw.widgets.spacer import Spacer
from caw.widgets.text import Text
from caw.widgets.battery import Battery
from caw.widgets.volume import Volume
from caw.widgets.clock import Clock
from caw.widgets.cpu import CPU
from caw.widgets.systray import Systray
from caw.widgets.allornothing import AllOrNothing
from caw.widgets.desktop import Desktop

font_face='gelly'
font_size=10
fg_color=0x636363
bg_color=0x181818
shading=256/4 * 3
border_color=0x303030
height=10
border_width=1
edge=0

hostname = socket.gethostname()

widgets = []
#widgets.append(Spacer(3))
widgets.append(Desktop(showall=False, current_fg=0x0090b4))

widgets.append(Spacer(3))
widgets.append(AllOrNothing(
    Text(" :: ", 0xcf49eb),
    Systray())
    )

widgets.append(Spacer(-1))
#widgets.append(Tasklist())
widgets.append(CPU(1, fg_color=0xdddddd))
widgets.append(Text(" : ", 0x777777))
widgets.append(CPU(2, fg_color=0xdddddd))

widgets.append(Text(" :: ", 0xcf49eb))

if hostname == 'murdock':
    widgets.append(Battery(fg_color=0x9f78ff))
    widgets.append(Text(" :: ", 0xcf49eb))

#widgets.append(Volume(device='PCM'))
if hostname == 'baracus':
    widgets.append(Text(" ", 0x777777))
#    widgets.append(Volume(percent_color=0xaaaaaa))

widgets.append(Text(" :: ", 0xcf49eb))

widgets.append(Clock(format='%Y.%m.%d', color=0xdddddd))
widgets.append(Text(" "))
widgets.append(Clock(format='%H:%M:%S', color=0xffffff))
widgets.append(Spacer(3))
