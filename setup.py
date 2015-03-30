import fileinput, os, sys, glob
from distutils.core import Extension, setup
from distutils import sysconfig
import commands

# Check for Python Xlib
try:
    try:
        import xcffib
    except:
        import xcb
except:
    print "\nCaw! requires xcffib or XPYB"
    print "https://pypi.python.org/pypi/xcffib/"
    print "http://sourceforge.net/projects/python-xlib/"
    sys.exit()

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    packages = ' '.join(packages)
    for flag, extra in [("--libs", "extra_link_args"),
                        ("--cflags", "extra_compile_args"),
                        ]:
        for token in commands.getoutput("pkg-config %s %s" % (flag, packages)).split():
            if token[:2] in flag_map:
                kw.setdefault(flag_map[token[:2]], []).append(token[2:])
            else:
                kw.setdefault(extra, []).append(token)
    return kw

# Distutils config
extargs = pkgconfig('xcb','xcb-atom','xcb-icccm', 'cairo','pango','pangocairo',
                    extra_compile_args=['-Wall'])
module = Extension("caw/cawc",
                   sources            = ["caw/cawc.c"],
                   **extargs
                   )

py_modules = []

for file in glob.glob("caw/*.py"):
    py_modules.append(file[:-3])

for file in glob.glob("caw/widgets/*.py"):
    py_modules.append(file[:-3])

setup(name             = "CAW!",
      author           = "Donald Ephraim Curtis",
      author_email     = "dcurtis@gmail.com",
      version          = ".9",
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
