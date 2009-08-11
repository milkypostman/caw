import fileinput, os, sys, glob
from distutils.core import Extension, setup
from distutils import sysconfig
import commands

# Check for Python Xlib
try:
    import xcb
except:
    print "\nCaw! requires the XPYB"
    print "http://sourceforge.net/projects/python-xlib/"
    sys.exit()

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    return kw

# Distutils config
module = Extension("caw/cawc",
                   sources            = ["caw/cawc.c"],
                   extra_compile_args = ['-Wall'],
                   **pkgconfig('xcb','xcb-atom','xcb-icccm','cairo','freetype2', 'x11', 'x11-xcb', 'xft')
                   #libraries          = ['xcb','xcb-atom','xcb-icccm','cairo','freetype2', 'x11', 'x11-xcb', 'xft'],
                   )

py_modules = []

for file in glob.glob("caw/*.py"):
    py_modules.append(file[:-3])

for file in glob.glob("caw/widgets/*.py"):
    py_modules.append(file[:-3])

setup(name             = "CAW!",
      author           = "Donald Ephraim Curtis",
      author_email     = "dcurtis@gmail.com",
      version          = ".8",
      license          = "GPL",
      platforms        = "POSIX",
      description      = "Lightweight panel/taskbar for X11 Window Managers",
      long_description = "See README for more information",
      url              = "http://caw.sourceforge.net",
      scripts          = ["bin/caw"],
      packages         = ['caw', 'caw/widgets'],
      #package_data     = {'caw':['etc/config.py']},
      data_files       = [('../etc/xdg/caw', ['etc/config.py'])],
      ext_modules      = [module]
      )
