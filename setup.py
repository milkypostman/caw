import fileinput, os, sys
from distutils.core import Extension, setup
from distutils import sysconfig

# Full paths to imlib2-config and freetype-config, adjust as needed -
configs = []

# Add any additional library directories here -
ldirs   = []

# Add any additional compile options here -
cargs   = ["-Wall"]

#------------------------------------------------------------------------------
# The rest of this script should not need to be modified! 
#------------------------------------------------------------------------------
libs  = [] # libraries (listed without -l)
largs = [] # extra link arguments
defs  = [] # define macros
files = [] #"COPYING", "README", "ppicon.png", "pypanelrc"]
install_dir = sysconfig.get_python_lib() + "/caw"

# Check for Python Xlib
try:
    import xcb
except:
    print "\nCaw! requires the XPYB"
    print "http://sourceforge.net/projects/python-xlib/"
    sys.exit()

# Fix the shebang and add the Imlib2 workaround if necessary
#if len(sys.argv) > 1 and sys.argv[1] != "sdist":
#    for line in fileinput.input(["bin/caw"], inplace=1):
#        if fileinput.isfirstline():
#            print "#!%s -OO" % sys.executable
#        else:
#            print line,


# Distutils config
module = Extension("caw/cawc",
                   sources            = ["caw/cawc.c"],
                   include_dirs       = [],
                   library_dirs       = ldirs,
                   libraries          = ['xcb','xcb-atom','xcb-icccm','cairo'],
                   extra_compile_args = cargs,
                   extra_link_args    = largs,
                   define_macros      = defs,
                   )

setup(name             = "CAW!",
      author           = "Donald Ephraim Curtis",
      author_email     = "dcurtis@gmail.com",
      version          = ".8",
      license          = "GPL",
      platforms        = "POSIX",
      description      = "Lightweight panel/taskbar for X11 Window Managers",
      long_description = "See README for more information",
      url              = "http://caw.sourceforge.net",
      data_files       = [(install_dir, files)],
      scripts          = ["bin/caw"],
      ext_modules      = [module]
      )
