#

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf
import cairo

from colorsBar import RColor
from editmode import EditMode

class FillMode(EditMode):
    def __init__(self):
        EditMode.__init__(self)
        self.init_tool()

    def init_tool(self):
        pass

    def do_button_press_event(self, event: Gdk.EventButton)->bool:

        tmx = event.x - EditMode.origin_x
        tmy = event.y - EditMode.origin_y

        px, py = self.MouseToPixel(tmx, tmy)
        if px < EditMode.PixWidth and py < EditMode.PixHeight:
            if event.button == 1:
                color = EditMode.ForegroundColor
            elif event.button == 3:
                color = EditMode.BackgroundColor
            else:
                color = None
            if color != None:
                EditMode.BackupSurface()
                # Get Target Color
                a, r, g, b = EditMode.get_pixel(px, py)
                iTargetColor = RColor(r, g, b, a)
                # Replace Target Color
                EditMode.floodFill(px, py, iTargetColor, color)
            return True
        return False


    def do_button_release_event(self, event: Gdk.EventButton)->bool:
        return False

    def do_motion_notify_event(self, event: Gdk.EventButton)->bool:
        return False

    def do_draw(self, cr):
        pass

