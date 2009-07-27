#include <Python.h>

#include <xcb/xcb.h>
#include <xcb/xproto.h>
#include <xcb/xcb_atom.h>
#include <xcb/xcb_icccm.h>
#include <cairo/cairo.h>
#include <cairo/cairo-xcb.h>

typedef enum
{
    _NET_WM_WINDOW_TYPE,
    _NET_WM_WINDOW_TYPE_DOCK,
    _NET_WM_DESKTOP,
    _NET_WM_STATE,
    _NET_WM_STATE_SKIP_PAGER,
    _NET_WM_STATE_SKIP_TASKBAR,
    _NET_WM_STATE_STICKY,
    _NET_WM_STATE_ABOVE,
    _NET_WM_STRUT,
    _NET_WM_STRUT_PARTIAL,
    _WIN_STATE,
    _XROOTPMAP_ID,
    _ATOM_COUNT,
} atoms_t;

char *atom_str[] = {
    "_NET_WM_WINDOW_TYPE",
    "_NET_WM_WINDOW_TYPE_DOCK",
    "_NET_WM_DESKTOP",
    "_NET_WM_STATE",
    "_NET_WM_STATE_SKIP_PAGER",
    "_NET_WM_STATE_SKIP_TASKBAR",
    "_NET_WM_STATE_STICKY",
    "_NET_WM_STATE_ABOVE",
    "_NET_WM_STRUT",
    "_NET_WM_STRUT_PARTIAL",
    "_WIN_STATE",
    "_XROOTPMAP_ID",
};

xcb_atom_t atoms[_ATOM_COUNT];

void
_init_atoms(xcb_connection_t *connection)
{
    xcb_intern_atom_cookie_t cookies[_ATOM_COUNT];
    int i;

    for(i=0; i< _ATOM_COUNT; i++)
    {
        cookies[i] = xcb_intern_atom(connection,
                0, strlen(atom_str[i]), atom_str[i]);
    }

    for (i = 0; i < _ATOM_COUNT; ++i) {
        xcb_intern_atom_reply_t *reply = xcb_intern_atom_reply (connection, cookies[i], NULL );

        if (reply) {
            atoms[i] = reply->atom;
            free (reply);
        }
    }

}

static PyObject * _xcb_connect(PyObject *self, PyObject *args)
{
    xcb_connection_t *connection;
    /*
    if (!PyArg_ParseTuple(args, "ls", &panel, &font))
        return NULL;
        */
    connection = xcb_connect(0, 0);
    _init_atoms(connection);
    return Py_BuildValue("l", connection);
}

static PyObject *
_xcb_visualtype(PyObject *self, PyObject *args)
{
    xcb_depth_iterator_t depth_iter;
    xcb_visualtype_iterator_t visual_iter;
    xcb_screen_t *s;

    if (!PyArg_ParseTuple(args, "l", &s))
        return NULL;

    for(depth_iter = xcb_screen_allowed_depths_iterator(s); depth_iter.rem; xcb_depth_next (&depth_iter))
        for(visual_iter = xcb_depth_visuals_iterator (depth_iter.data); visual_iter.rem; xcb_visualtype_next (&visual_iter))
            if (s->root_visual == visual_iter.data->visual_id)
                return Py_BuildValue("l", visual_iter.data);

    Py_RETURN_NONE;
}

static PyObject *
_xcb_screen(PyObject *self, PyObject *args)
{
    xcb_connection_t *connection;

    if (!PyArg_ParseTuple(args, "l", &connection))
        return NULL;

    const xcb_setup_t *setup = xcb_get_setup (connection);
    xcb_screen_iterator_t iter = xcb_setup_roots_iterator (setup);  
    int i;

    // we want the screen at index screenNum of the iterator
    for (i = 0; i < 0; ++i) {
        xcb_screen_next(&iter);
    }

    return Py_BuildValue("l", iter.data);
}

static PyObject *
_xcb_configure_window(PyObject *self, PyObject *args)
{
    xcb_connection_t *connection;
    xcb_window_t win;
    uint32_t config[7];

    if (!PyArg_ParseTuple(args, "llllll", &connection, &win, &config[0], &config[1], &config[2], &config[3]))
        return NULL;

    xcb_configure_window(connection, win,
            XCB_CONFIG_WINDOW_X | XCB_CONFIG_WINDOW_Y |
            XCB_CONFIG_WINDOW_WIDTH | XCB_CONFIG_WINDOW_HEIGHT,
            config);



    Py_RETURN_NONE;
}

static PyObject *
_cairo_set_source_rgb(PyObject *self, PyObject *args)
{
    cairo_t * cairo;
    double r,g,b;
    
    if (!PyArg_ParseTuple(args, "lddd", &cairo, &r, &g, &b))
        return NULL;

    cairo_set_source_rgb(cairo, r, g, b);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_set_source_rgba(PyObject *self, PyObject *args)
{
    cairo_t * cairo;
    double r,g,b,a;
    
    if (!PyArg_ParseTuple(args, "ldddd", &cairo, &r, &g, &b, &a))
        return NULL;

    cairo_set_source_rgba(cairo, r, g, b, a);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_rectangle(PyObject *self, PyObject *args)
{
    cairo_t * cairo;
    double x,y,w,h;

    if (!PyArg_ParseTuple(args, "ldddd", &cairo, &x, &y, &w, &h))
        return NULL;

    cairo_rectangle(cairo, x, y, w, h);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_fill(PyObject *self, PyObject *args)
{
    cairo_t * cairo;

    if (!PyArg_ParseTuple(args, "l", &cairo))
        return NULL;

    cairo_fill(cairo);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_stroke(PyObject *self, PyObject *args)
{
    cairo_t * cairo;

    if (!PyArg_ParseTuple(args, "l", &cairo))
        return NULL;

    cairo_stroke(cairo);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_select_font_face(PyObject *self, PyObject *args)
{
    cairo_t * cairo;
    char *face;
    int bold = 0;
    
    if (!PyArg_ParseTuple(args, "ls|i", &cairo, &face, &bold))
        return NULL;


    if(bold)
    {
        bold = CAIRO_FONT_WEIGHT_BOLD;
    }
    else
    {
        bold = CAIRO_FONT_SLANT_NORMAL;
    }
    cairo_select_font_face(cairo, face, CAIRO_FONT_SLANT_NORMAL, bold);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_set_font_size(PyObject *self, PyObject *args)
{
    cairo_t * cairo;
    double width;
    
    if (!PyArg_ParseTuple(args, "ld", &cairo, &width))
        return NULL;

    cairo_set_line_width(cairo, width);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_set_line_width(PyObject *self, PyObject *args)
{
    cairo_t * cairo;
    double width;
    
    if (!PyArg_ParseTuple(args, "ld", &cairo, &width))
        return NULL;

    cairo_set_line_width(cairo, width);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_move_to(PyObject *self, PyObject *args)
{
    cairo_t * cairo;
    double x,y;
    
    if (!PyArg_ParseTuple(args, "ldd", &cairo, &x, &y))
        return NULL;

    cairo_move_to(cairo, x, y);
    Py_RETURN_NONE;
}

static PyObject *
_cairo_show_text(PyObject *self, PyObject *args)
{
    cairo_t * cairo;
    char *text;
    
    if (!PyArg_ParseTuple(args, "ls", &cairo, &text))
        return NULL;

    cairo_show_text(cairo, text);
    Py_RETURN_NONE;
}

static PyObject *
_update_struts(PyObject *self, PyObject *args)
{
    xcb_connection_t *connection;
    xcb_window_t window;
    uint32_t data[12];
    int x, y, w, h;

    memset(data, 0, sizeof(data));

    if (!PyArg_ParseTuple(args, "lliiii", &connection, &window, &x, &y, &w, &h))
        return NULL;

    data[3] = h;
    data[11] = h;
    xcb_change_property(connection, XCB_PROP_MODE_REPLACE,
            window, atoms[_NET_WM_STRUT], CARDINAL,
            32, 4, data);

    xcb_change_property(connection, XCB_PROP_MODE_REPLACE,
            window, atoms[_NET_WM_STRUT_PARTIAL], CARDINAL,
            32, 12, data);

    Py_RETURN_NONE;
}


static PyObject *
_set_properties(PyObject *self, PyObject *args)
{
    xcb_connection_t *connection;
    xcb_window_t window;
    uint32_t data[10];
    int x, y, w, h;

    if (!PyArg_ParseTuple(args, "lliiii", &connection, &window, &x, &y, &w, &h))
        return NULL;

    data[0] = 0xffffffff;
    xcb_change_property(connection, XCB_PROP_MODE_REPLACE,
            window, atoms[_NET_WM_DESKTOP], CARDINAL,
            32, 1, data);

    data[0] = atoms[_NET_WM_WINDOW_TYPE_DOCK];
    xcb_change_property(connection, XCB_PROP_MODE_REPLACE,
            window, atoms[_NET_WM_WINDOW_TYPE], ATOM,
            32, 1, data);

    xcb_wm_hints_t hints;
    xcb_size_hints_t normal_hints;

    // send requests
    xcb_get_property_cookie_t hint_c = xcb_get_wm_hints(connection, window);
    xcb_get_property_cookie_t normal_hints_c = xcb_get_wm_normal_hints(connection, window);


    // set wm hints
    xcb_get_wm_hints_reply(connection, hint_c, &hints, 0);
    xcb_wm_hints_set_input(&hints, 0);
    xcb_wm_hints_set_normal(&hints);

    xcb_set_wm_hints(connection, window, &hints);


    // set the normal hints
    xcb_get_wm_normal_hints_reply(connection, normal_hints_c, &normal_hints, 0);

    normal_hints.flags |= XCB_SIZE_HINT_P_POSITION;
    //xcb_size_hints_set_position(&normal_hints, 0, x, y);
    //xcb_size_hints_set_min_size(&normal_hints, 10, 10);
    //xcb_size_hints_set_max_size(&normal_hints, w, h);

    xcb_set_wm_normal_hints(connection, window, &normal_hints);

    data[0] = atoms[_NET_WM_STATE_SKIP_TASKBAR];
    data[1] = atoms[_NET_WM_STATE_SKIP_PAGER];
    data[2] = atoms[_NET_WM_STATE_STICKY];
    data[3] = atoms[_NET_WM_STATE_ABOVE];

    xcb_change_property(connection, XCB_PROP_MODE_REPLACE,
            window, atoms[_NET_WM_STATE], ATOM,
            32, 4, data);

    Py_RETURN_NONE;
}

static PyObject * 
_cairo_text_width(PyObject *self, PyObject *args)
{
    cairo_t *cairo;
    cairo_text_extents_t te;
    char *text;

    if (!PyArg_ParseTuple(args, "ls", &cairo, &text))
        return NULL;

    cairo_text_extents(cairo, text, &te);
    return Py_BuildValue("d", te.width);
}

static PyObject * 
_cairo_font_height(PyObject *self, PyObject *args)
{
    cairo_t *cairo;
    cairo_font_extents_t fe;

    if (!PyArg_ParseTuple(args, "l", &cairo))
        return NULL;

    cairo_font_extents(cairo, &fe);
    return Py_BuildValue("d", fe.ascent - fe.descent);
}

static PyObject * 
_cairo_create(PyObject *self, PyObject *args)
{
    xcb_connection_t *connection;
    xcb_visualtype_t *visual;
    xcb_window_t window;
    cairo_surface_t * surface;
    cairo_t * cairo;
    int width, height;

    if (!PyArg_ParseTuple(args, "lllii", &connection, &window, &visual, &width, &height))
        return NULL;

    surface = cairo_xcb_surface_create(connection,
            window,
            visual,
            width,
            height);

    cairo = cairo_create(surface);
    //cairo_surface_destroy(surface);

    return Py_BuildValue("l", cairo);
}

static PyMethodDef CAWCMethods[] = {
/*-------------------------------*/
    {"xcb_connect",     _xcb_connect,     METH_VARARGS, "Connect"},
    {"xcb_screen",     _xcb_screen,     METH_VARARGS, "Connect"},
    {"xcb_configure_window",     _xcb_configure_window,     METH_VARARGS, "Connect"},
    {"xcb_visualtype",     _xcb_visualtype,     METH_VARARGS, "Connect"},
    {"cairo_create", _cairo_create, METH_VARARGS},
    {"cairo_set_source_rgb", _cairo_set_source_rgb, METH_VARARGS},
    {"cairo_set_source_rgba", _cairo_set_source_rgba, METH_VARARGS},
    {"cairo_rectangle", _cairo_rectangle, METH_VARARGS},
    {"cairo_fill", _cairo_fill, METH_VARARGS},
    {"cairo_stroke", _cairo_stroke, METH_VARARGS},
    {"cairo_set_line_width", _cairo_set_line_width, METH_VARARGS},
    {"cairo_text_width", _cairo_text_width, METH_VARARGS},
    {"cairo_font_height", _cairo_font_height, METH_VARARGS},
    {"cairo_set_font_size", _cairo_set_font_size, METH_VARARGS},
    {"cairo_select_font_face", _cairo_select_font_face, METH_VARARGS},
    {"cairo_move_to", _cairo_move_to, METH_VARARGS},
    {"cairo_show_text", _cairo_show_text, METH_VARARGS},
    {"set_properties", _set_properties, METH_VARARGS},
    {"update_struts", _update_struts, METH_VARARGS},
    {NULL, NULL, 0, NULL}
};


void initcawc(void) {
/*----------------------*/    
    Py_InitModule("cawc", CAWCMethods);
}
