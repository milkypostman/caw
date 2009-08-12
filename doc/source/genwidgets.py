#!/usr/bin/python

import glob


def main():
    wid = open("reference/widgets.rst", "w")
    wid.write("""caw.widgets
***********

.. automodule:: caw.widgets

.. autosummary::
   :toctree: widgets/

""")

    for f in glob.glob('../../caw/widgets/*.py'):
        f = f[18:-3]
        if f.startswith("_"): continue
        wid.write("   %s\n" % f)
    wid.write("\n")






if __name__ == '__main__':
    main()
