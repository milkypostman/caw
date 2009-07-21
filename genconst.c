#include <xcb/xcb.h>
#include <xcb/xcb_atom.h>
#include <xcb/xcb_icccm.h>
#include <cairo/cairo.h>
#include <string.h>
#include <stdio.h>

int main()
{
    FILE *f = fopen("const.py", "w");

    fprintf(f, "WM_NAME = %d\n", WM_NAME);
    fprintf(f, "WM_CLASS = %d\n", WM_CLASS);
    fprintf(f, "ATOM = %d\n", ATOM);
    fprintf(f, "WM_ICON_NAME = %d\n", WM_ICON_NAME);
    fprintf(f, "STRING = %d\n", STRING);
    fprintf(f, "CARDINAL = %d\n", CARDINAL);
    fprintf(f, "PIXMAP = %d\n", PIXMAP);
    fprintf(f, "XCB_EXPOSE = %d\n", XCB_EXPOSE);
    fprintf(f, "XCB_GC_FOREGROUND = %d\n", XCB_GC_FOREGROUND);
    fprintf(f, "XCB_GC_BACKGROUND = %d\n", XCB_GC_BACKGROUND);
    fprintf(f, "XCB_GC_FONT = %d\n", XCB_GC_BACKGROUND);
    fprintf(f, "XCB_PROPERTY_NOTIFY = %d\n", XCB_PROPERTY_NOTIFY);
    fprintf(f, "XCB_WINDOW_CLASS_INPUT_OUTPUT = %d\n", XCB_WINDOW_CLASS_INPUT_OUTPUT);
    fprintf(f, "XCB_PROP_MODE_REPLACE = %d\n", XCB_PROP_MODE_REPLACE);
    fprintf(f, "XCB_SIZE_HINT_P_POSITION = %d\n", XCB_SIZE_HINT_P_POSITION);
    fprintf(f, "XCB_CW_BACK_PIXEL = %d\n", XCB_CW_BACK_PIXEL);
    fprintf(f, "CAIRO_FONT_SLANT_ITALIC = %d\n", CAIRO_FONT_SLANT_ITALIC);
    fprintf(f, "CAIRO_FONT_SLANT_OBLIQUE = %d\n", CAIRO_FONT_SLANT_OBLIQUE);
    fprintf(f, "CAIRO_FONT_SLANT_NORMAL = %d\n", CAIRO_FONT_SLANT_NORMAL);
    fprintf(f, "CAIRO_FONT_WEIGHT_NORMAL = %d\n", CAIRO_FONT_WEIGHT_BOLD);
    fprintf(f, "CAIRO_FONT_WEIGHT_BOLD = %d\n", CAIRO_FONT_WEIGHT_BOLD);
    fclose(f);
}
