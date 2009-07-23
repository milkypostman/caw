#include <Python.h>
#include <xcb/xcb.h>
#include <xcb/xproto.h>

static PyObject * _connect(PyObject *self, PyObject *args) 
{
    xcb_connection_t *connection;
    /*
    if (!PyArg_ParseTuple(args, "ls", &panel, &font))
        return NULL;
        */
    connection = xcb_connect(0, 0);
    return Py_BuildValue("l", connection);
}
static PyMethodDef CAWCMethods[] = {
/*-------------------------------*/
    {"connect",     _connect,     METH_VARARGS, "Connect"},
    {NULL, NULL, 0, NULL}
};


void initcawc(void) {
/*----------------------*/    
    Py_InitModule("cawc", CAWCMethods);
}
