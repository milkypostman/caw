import fileinput, os, sys, glob
from distutils.core import Extension, setup
from distutils import sysconfig

# Check for Python Xlib
try:
    import xcb
except:
    print "\nCaw! requires the XPYB"
    print "http://sourceforge.net/projects/python-xlib/"
    sys.exit()


# Distutils config
module = Extension("caw/cawc",
                   sources            = ["caw/cawc.c"],
                   libraries          = ['xcb','xcb-atom','xcb-icccm','cairo'],
                   extra_compile_args = ['-Wall'],
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
