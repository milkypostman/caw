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
from caw.widgets.weather import Weather
from caw.widgets.tasklist import Tasklist
from caw.widgets.net import Net
from caw.widgets.wifi import Wifi
from caw.widgets.fifo import FIFO
from caw.widgets.memory import Memory

hostname = socket.gethostname()

font_face='mintsstrong'
#font_face='nu'
#font_y_offset=-1
#font_face='gelly'
#font_face='Terminus'
#font_face='DejaVu Sans Mono'
font_size = 8
fg=0xc05e00
netdev = 'eth1'
bg=(0x4c3a11, 0x33260b)
shading=256/4 * 3
border_color=0x33260b


caw = Caw(
        font_face=font_face,
        font_size=font_size,
        #width = .8,
        #xoffset = .1,
        yoffset = 0,
        above = True,
        bg=bg,
        shading=shading,
        border_color=border_color,
        height=12,
        border_width=1,
        edge=0
        )

widgets = []
widgets.append(Spacer(3))
widgets.append(Desktop(current_fg=0x00ff00, showall=False))

widgets.append(Spacer(3))
widgets.append(AllOrNothing(
    Text(" :: "),
    Systray())
    )

widgets.append(Spacer(10))

#widgets.append(Tasklist(alldesktops=True, normal_fg=0xcccccc, current_fg=0x0000ff, normal_border=0x555555, current_border=0x00ff00, minimized_border=0xcccccc, border_width=0))
widgets.append(Spacer(-1))

widgets.append(Text("CPU-", 0xff6565))
widgets.append(CPU(1, normal_fg=0xdddddd))
widgets.append(Text("%", 0xaaaaaa))
widgets.append(Text(" : ", 0x777777))
widgets.append(CPU(2, normal_fg=0xdddddd))
widgets.append(Text("%", 0xaaaaaa))

widgets.append(Text(" :: "))
widgets.append(Text("Mem-", 0xff6565))
widgets.append(Memory(fg=0xdddddd))
widgets.append(Text(" :: "))

widgets.append(Net(netdev, normal_fg=0xdddddd))
widgets.append(Text("k", 0x46a4ff))
widgets.append(Text(" : ", 0x777777))
widgets.append(Net(netdev, 'up', normal_fg=0xdddddd))
widgets.append(Text("k", 0xff6565))
widgets.append(Text(" :: "))

widgets.append(Wifi(adapter='ath0', normal_fg=0xdddddd))
widgets.append(Text("%", 0xaaaaaa))
widgets.append(Text(" :: "))


widgets.append(Weather())

widgets.append(Text(" :: "))

widgets.append(Battery(normal_fg=0x9f78ff))
widgets.append(Text(" :: "))

vol = Volume(device='PCM')
widgets.append(vol)
widgets.append(Text("% ", 0xaaaaaa, button5=vol.button5, button4=vol.button4))
vol = Volume()
widgets.append(vol)
widgets.append(Text("% ", 0xaaaaaa, button5=vol.button5, button4=vol.button4))

widgets.append(Text(":: "))

widgets.append(Clock(format='%Y.%m.%d', fg=0xaaaaaa))
widgets.append(Text(" "))
widgets.append(Clock(format='%H:%M:%S', fg=0xffffff))
widgets.append(Spacer(3))

caw.widgets = widgets

caw.mainloop()
