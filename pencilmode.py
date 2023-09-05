import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf
import cairo

from editmode import EditMode

class PencilMode(EditMode):
    def __init__(self):
        EditMode.__init__(self)
        self.init_tool()

    def init_tool(self):
        self.curPixelX = 0
        self.curPixelY = 0
        self.lastPixelX = 0
        self.lastPixelY = 0

    def do_button_press_event(self, event: Gdk.EventButton)->bool:

        tmx = event.x - EditMode.origin_x
        tmy = event.y - EditMode.origin_y

        self.curPixelX, self.curPixelY = self.MouseToPixel(tmx, tmy)

        if event.button == 1:
            color = PencilMode.ForegroundColor
        elif event.button == 3:
            color = PencilMode.BackgroundColor
        else:
            color = None

        if (color is not None) and self.curPixelX < PencilMode.PixWidth \
                and self.curPixelY < PencilMode.PixHeight:

            if event.state & Gdk.ModifierType.CONTROL_MASK:
                EditMode.BackupSurface()
                EditMode.line(self.lastPixelX, self.lastPixelY,
                              self.curPixelX, self.curPixelY, color)
            # elif event.state & Gdk.ModifierType.SHIFT_MASK:
            #     EditMode.RestoreSurface()
            else:
                tblPixs = PencilMode.CrSurface.get_data()
                ip = PencilMode.CrSurface.get_stride()*self.curPixelY + \
                    self.curPixelX * 4
                tblPixs[ip] = color.blue  # blue
                tblPixs[ip+1] = color.green  # green
                tblPixs[ip+2] = color.red  # red
                tblPixs[ip+3] = color.alpha  # alpha
            return True

        return False

    def do_button_release_event(self, event: Gdk.EventButton)->bool:
        self.lastPixelX = self.curPixelX
        self.lastPixelY = self.curPixelY
        return True

    def do_motion_notify_event(self, event: Gdk.EventButton)->bool:
        tmx = event.x - EditMode.origin_x
        tmy = event.y - EditMode.origin_y
        px, py = self.MouseToPixel(tmx, tmy)
        if px >= 0 and px < PencilMode.PixWidth and \
                py >= 0 and py < PencilMode.PixHeight:
            if event.state & Gdk.ModifierType.BUTTON1_MASK:
                color = PencilMode.ForegroundColor
            elif event.state & Gdk.ModifierType.BUTTON3_MASK:
                color = PencilMode.BackgroundColor
            else:
                color = None
            if color is not None:
                if ((px != self.curPixelX) or (py != self.curPixelY)):
                    self.curPixelX = px
                    self.curPixelY = py
                    if event.state & Gdk.ModifierType.CONTROL_MASK:
                        EditMode.RestoreSurface()
                        EditMode.line(self.lastPixelX, self.lastPixelY,
                                    self.curPixelX, self.curPixelY, color)
                        print(self.curPixelX, self.curPixelY)
                    else:
                        tblPixs = PencilMode.CrSurface.get_data()
                        ip = PencilMode.CrSurface.get_stride()*py + px * 4
                        tblPixs[ip] = color.blue  # blue
                        tblPixs[ip+1] = color.green  # green
                        tblPixs[ip+2] = color.red  # red
                        tblPixs[ip+3] = color.alpha  # alpha
                    return True
        return False

    def do_draw(self, cr: cairo.Context):
        pass
