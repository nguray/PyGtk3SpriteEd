import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf


class RColor:
    __gtype_name__ = 'RColor'

    def __init__(self, r: int, g: int, b: int, a: int):
        self.red = r
        self.green = g
        self.blue = b
        self.alpha = a


class ColorsBar(Gtk.Widget):

    __gtype_name__ = 'ColorsBar'

    # __gsignals__ = {
    #     'forecolor_changed': (GObject.SIGNAL_RUN_FIRST, None,
    #                   (GObject.TYPE_PYOBJECT,)),
    #     'backcolor_changed': (GObject.SIGNAL_RUN_FIRST, None,
    #                   (GObject.TYPE_PYOBJECT,)),
    # }
    @GObject.Signal
    def forecolor_changed(self, RColor: GObject.TYPE_PYOBJECT):
        pass

    @GObject.Signal
    def backcolor_changed(self, RColor: GObject.TYPE_PYOBJECT):
        pass

    @GObject.Signal
    def choose_color_dialog(self, idColor: GObject.TYPE_INT):
        pass

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.set_size_request(80, 44)

        self.nbRows = 2
        self.nbColumns = 16
        self.cellSize = 22.0

        self.loadPalette()

        if len(self.palette) == 0:
            self.palette = [
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 255),
                RColor(127, 127, 127, 255),
                RColor(136, 0, 21, 255),
                RColor(237, 28, 36, 255),
                RColor(255, 127, 39, 255),
                RColor(255, 242, 0, 255),
                RColor(34, 177, 79, 255),
                RColor(0, 162, 232, 255),
                RColor(0, 162, 232, 255),
                RColor(0, 162, 232, 255),
                RColor(0, 162, 232, 255),
                RColor(0, 162, 232, 255),
                RColor(0, 162, 232, 255),
                RColor(0, 162, 232, 255),
                RColor(0, 162, 232, 255),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 0),
                RColor(0, 0, 0, 255)
            ]
            self.foregroundColor = RColor(0, 0, 0, 255)
            self.backgroundColor = RColor(0, 0, 0, 0)

    def drawCell(self, cr, x, y, cs, r, g, b, a):
        # ------------------------------------------------
        if a == 0:
            cr.set_source_rgba(0.5, 0.5, 0.5, 1)
            cr.set_line_width(1)
            cr.set_antialias(cairo.ANTIALIAS_NONE)
            cr.move_to(x+1, y+1)
            cr.line_to(x+cs-1, y+cs-1)
            cr.move_to(x+cs-1, y+1)
            cr.line_to(x+1, y+cs-1)
            # cr.move_to(x+1,y+1)
            # cr.line_to(x+cs-1,y+1)
            # cr.line_to(x+cs-1,y+cs-1)
            # cr.line_to(x+1,y+cs-1)
            # cr.line_to(x+1,y+1)
            cr.rectangle(x+1, y+1, cs-2, cs-2)
            cr.stroke()
        else:
            cr.set_source_rgba(r/255, g/255, b/255, a/255)
            cr.rectangle(x+1, y+1, cs-2, cs-2)
            cr.fill()

    def do_draw(self, cr):
        # ------------------------------------------------
        allocation = self.get_allocation()
        iRow = 0
        iCol = 0
        cs = self.cellSize - 2
        for colRect in self.palette:
            x = iCol*self.cellSize + 2*self.cellSize
            y = iRow*self.cellSize
            # cr.set_source_rgba(colRect.red/255,colRect.green/255,colRect.blue/255,colRect.alpha/255)
            self.drawCell(cr, x, y, self.cellSize, colRect.red,
                          colRect.green, colRect.blue, colRect.alpha)
            #cr.rectangle( x+1, y+1, cs, cs)
            # cr.fill()
            iCol += 1
            if iCol >= self.nbColumns:
                iCol = 0
                iRow += 1
        # Draw BackgroundColor
        cs = self.cellSize*2
        self.drawCell(cr, 0, 0, cs, self.backgroundColor.red, self.backgroundColor.green,
                      self.backgroundColor.blue, self.backgroundColor.alpha)
        # Draw ForegroundColor
        cs = self.cellSize
        self.drawCell(cr, 0, 0, cs, self.foregroundColor.red, self.foregroundColor.green,
                      self.foregroundColor.blue, self.foregroundColor.alpha)

        # cr.set_source_rgba(0,0,1,1)
        # cr.set_line_width(1)
        # cr.set_antialias(cairo.ANTIALIAS_NONE)
        # cr.set_antialias(cairo.ANTIALIAS_NONE)
        # cr.line_to(allocation.width,allocation.height)
        # cr.move_to(allocation.width,0)
        # cr.line_to(0,allocation.height)
        # cr.stroke()

    def do_realize(self):
        allocation = self.get_allocation()
        attr = Gdk.WindowAttr()
        attr.window_type = Gdk.WindowType.CHILD
        attr.x = allocation.x
        attr.y = allocation.y
        attr.width = allocation.width
        attr.height = allocation.height
        attr.visual = self.get_visual()
        attr.event_mask = self.get_events() | Gdk.EventMask.EXPOSURE_MASK | Gdk.EventMask.BUTTON_PRESS_MASK \
            | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK \
            | Gdk.EventMask.BUTTON1_MOTION_MASK | Gdk.EventMask.BUTTON3_MOTION_MASK
        WAT = Gdk.WindowAttributesType
        mask = WAT.X | WAT.Y | WAT.VISUAL
        window = Gdk.Window(self.get_parent_window(), attr, mask)
        self.set_window(window)
        self.register_window(window)
        self.set_realized(True)

    def do_get_preferred_height(self):
        """Calculates the DockFrame's initial minimum and natural height.
        While this call is specific to width-for-height requests (that we
        requested not to get) we cannot be certain that our wishes are granted,
        so we must implement this method as well. Returns the preferred height
        of the child widget with padding added for the border width.
        Returns:
            int: minimum height, natural height.
        """
        minimum_height = 8
        natural_height = 16
        return minimum_height, natural_height

    def do_get_preferred_width(self):
        """Calculates the DockFrame's initial minimum and natural width.
        While this call is specific to width-for-height requests (that we
        requested not to get) we cannot be certain that our wishes are granted,
        so we must implement this method as well. Returns the preferred width
        of the child widget with padding added for the border width.
        Returns:
            int: minimum width, natural width.
        """
        minimum_width = 8
        natural_width = 16
        return minimum_width, natural_width

    def savePalette(self):
        with open("palette.cfg", 'w') as outF:
            outF.write('{0} {1} {2} {3}\n'.format(self.foregroundColor.red,
                                                  self.foregroundColor.green, self.foregroundColor.blue, self.foregroundColor.alpha))
            outF.write('{0} {1} {2} {3}\n'.format(self.backgroundColor.red,
                                                  self.backgroundColor.green, self.backgroundColor.blue, self.backgroundColor.alpha))
            for colRect in self.palette:
                outF.write('{0} {1} {2} {3}\n'.format(
                    colRect.red, colRect.green, colRect.blue, colRect.alpha))

    def loadPalette(self):
        self.palette = []
        with open("palette.cfg", 'r') as inF:
            iLin = 0
            lin = inF.readline()
            while lin:
                if lin != "":
                    r, g, b, a = lin.split()
                    c = RColor(int(r), int(g), int(b), int(a))
                    if iLin == 0:
                        # Read Foreground Color
                        self.foregroundColor = c
                    elif iLin == 1:
                        # Read Backgroung Color
                        self.backgroundColor = c
                    else:
                        self.palette.append(c)
                    iLin += 1
                    # print(iLin,r,g,b,a)
                lin = inF.readline()

    def mouseToIndexCol(self, mx: int, my: int):
        if mx > 2*self.cellSize:
            iRow = int(my/self.cellSize)
            iCol = int((mx-2*self.cellSize)/self.cellSize)
            return iCol+iRow*self.nbColumns
        return -1

    def do_button_press_event(self, event):
        mx = event.x
        my = event.y
        if event.button == 1:
            if (event.state & Gdk.ModifierType.SHIFT_MASK):
                # 
                idCell = self.mouseToIndexCol(mx, my)
                self.palette[idCell].alpha = self.foregroundColor.alpha
                self.palette[idCell].red = self.foregroundColor.red
                self.palette[idCell].green = self.foregroundColor.green
                self.palette[idCell].blue = self.foregroundColor.blue
                self.queue_draw()
            elif event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                # 
                idCell = self.mouseToIndexCol(mx, my)
                self.emit("choose_color_dialog",idCell)
            else:
                if mx < 2*self.cellSize:
                    # Swap Fore et Back color
                    d = self.foregroundColor
                    self.foregroundColor = self.backgroundColor
                    self.backgroundColor = d
                    self.queue_draw()
                    self.emit_colors_update()
                else:
                    # Select Color
                    idCol = self.mouseToIndexCol(mx, my)
                    if idCol >= 0:
                        col = self.palette[idCol]
                        #self.emit("forecolor_changed", col.red,col.green,col.blue,col.alpha)
                        # print(">>",self.foregroundColor.red,self.foregroundColor.green,self.foregroundColor.blue,self.foregroundColor.alpha)
                        # Il faut faire l'affectation après emit sinon self.foregroundColor ne change pas ???
                        self.foregroundColor.alpha = col.alpha
                        self.foregroundColor.red = col.red
                        self.foregroundColor.green = col.green
                        self.foregroundColor.blue = col.blue
                        self.queue_draw()
                        self.emit_colors_update()

    def emit_colors_update(self):
        self.emit("forecolor_changed", self.foregroundColor)
        self.emit("backcolor_changed", self.backgroundColor)

    def set_color_cell(self, idCell, r, g, b, a):
        self.palette[idCell].red = r
        self.palette[idCell].green = g
        self.palette[idCell].blue = b
        self.palette[idCell].alpha = a
        self.queue_draw()

    def set_foreground_color(self, a, r, g, b):
        self.foregroundColor.alpha  = a
        self.foregroundColor.red    = r
        self.foregroundColor.green  = g
        self.foregroundColor.blue   = b
        self.emit_colors_update()
        self.queue_draw()
