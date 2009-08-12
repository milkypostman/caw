"""CAW! main module.

Imported in the config.py file for instanciating and configuring the CAW! bar.

**Example**

::

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

    font_face='mintsstrong'
    font_size = 8
    fg_color=0xc05e00
    netdev = 'eth1'
    bg_color=(0x4c3a11, 0x33260b)
    shading=256/4 * 3
    border_color=0x33260b

    caw = Caw(
            font_face=font_face,
            font_size=font_size,
            #width = .8,
            #xoffset = .1,
            yoffset = 0,
            above = False,
            bg_color=bg_color,
            shading=shading,
            border_color=border_color,
            height=12,
            border_width=1,
            edge=0
            )

    widgets = []
    widgets.append(Spacer(3))
    widgets.append(Desktop(showall=False))

    widgets.append(Spacer(3))
    widgets.append(AllOrNothing(
        Text(" :: "),
        Systray()
        ))

    widgets.append(AllOrNothing(
        Text(" :: "),
        FIFO('/home/dcurtis/.config/caw/irssi')
        ))

    widgets.append(Spacer(10))
    widgets.append(Tasklist())
    widgets.append(CPU(1, fg_color=0xdddddd))
    widgets.append(Text("%", 0xaaaaaa))
    widgets.append(Text(" : ", 0x777777))
    widgets.append(CPU(2, fg_color=0xdddddd))
    widgets.append(Text("%", 0xaaaaaa))

    widgets.append(Text(" :: "))

    widgets.append(Net(netdev, fg_color=0xdddddd))
    widgets.append(Text("k", 0x46a4ff))
    widgets.append(Text(" : ", 0x777777))
    widgets.append(Net(netdev, 'up', fg_color=0xdddddd))
    widgets.append(Text("k", 0xff6565))
    widgets.append(Text(" :: "))


    widgets.append(Weather())

    widgets.append(Text(" :: "))

    vol = Volume(device='PCM')
    widgets.append(vol)
    widgets.append(Text("% ", 0xaaaaaa, button5=vol.button5, button4=vol.button4))
    vol = Volume()
    widgets.append(vol)
    widgets.append(Text("% ", 0xaaaaaa, button5=vol.button5, button4=vol.button4))

    widgets.append(Text(":: "))

    widgets.append(Clock(format='%Y.%m.%d', fg_color=0xaaaaaa))
    widgets.append(Text(" "))
    widgets.append(Clock(format='%H:%M:%S', fg_color=0xffffff))
    widgets.append(Spacer(3))

    caw.widgets = widgets

    caw.mainloop()

"""

__author__ = """Donald Ephraim Curtis <dcurtis@cs.uiowa.edu>"""
__docformat__ = """restructuredtext en"""

from caw import *

