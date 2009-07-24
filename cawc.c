#include <Python.h>
#include <xcb/xcb.h>
#include <xcb/xproto.h>
#include <cairo/cairo.h>
#include <cairo/cairo-xcb.h>

static PyObject * _xcb_connect(PyObject *self, PyObject *args)
{
    xcb_connection_t *connection;
    /*
    if (!PyArg_ParseTuple(args, "ls", &panel, &font))
        return NULL;
        */
    connection = xcb_connect(0, 0);
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
    cairo_surface_destroy(surface);

    return Py_BuildValue("l", cairo);
}

static PyMethodDef CAWCMethods[] = {
/*-------------------------------*/
    {"xcb_connect",     _xcb_connect,     METH_VARARGS, "Connect"},
    {"xcb_screen",     _xcb_screen,     METH_VARARGS, "Connect"},
    {"xcb_visualtype",     _xcb_visualtype,     METH_VARARGS, "Connect"},
    {"cairo_create", _cairo_create, METH_VARARGS},
    {NULL, NULL, 0, NULL}
};


void initcawc(void) {
/*----------------------*/    
    Py_InitModule("cawc", CAWCMethods);
}
