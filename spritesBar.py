import sys
import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, GObject, Gtk, Gdk, GdkPixbuf

class Sprite:

    __gtype_name__ = 'Sprite'

    def __init__(self,width=32,height=32):
        #-- Mandatory to make ImageSurface Display with 
        # cairo.Context.set_source_surface(surface) and cairo.Context.paint()
        sprite = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, width, height)
        sprite.fill(0x00000000)
        self.surface = Gdk.cairo_surface_create_from_pixbuf(sprite, 1, None)
        #n = sys.getrefcount(self.surface)
        self.fileName = ''
        self.fModified = False


class SpritesBar(Gtk.Widget):

    __gtype_name__ = 'SpritesBar'

    # __gsignals__ = {
    #     'sprite_change': (GObject.SIGNAL_RUN_FIRST, None,
    #                   (GObject.TYPE_PYOBJECT,)),
    # }
    @GObject.Signal
    def sprite_change(self, crSurface: GObject.TYPE_PYOBJECT):
        pass

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.set_size_request(64, 128)

        self.idSelect = 0
        self.nbCells = 8
        self.cellSize = 54.0
        self.tblSprites = []
        for i in range(0, self.nbCells):
            self.tblSprites.append(None)
        self.tblSprites[self.idSelect] = Sprite()
        self.idSequence = -1
        self.idTimer = 0


    def do_draw(self, cr):

        allocation = self.get_allocation()

        # Compute Cell size
        self.cellSize = allocation.width - 8

        # Draw Cells
        cr.set_antialias(cairo.ANTIALIAS_NONE)
        cr.set_line_width(1)
        cr.set_source_rgba(0.5, 0.5, 0.5, 1)
        x = (allocation.width - self.cellSize)/2
        for i in range(0, self.nbCells):
            y = i * self.cellSize + 2
            cr.rectangle(x, y, self.cellSize, self.cellSize)
        cr.stroke()

        # Draw Select mark
        xLeft = (allocation.width - self.cellSize)/2 + 2
        yTop = self.idSelect * self.cellSize + 2 + 2
        yBottom = yTop + self.cellSize - 4
        xRight = xLeft + self.cellSize - 4
        cr.set_source_rgba(1, 0.5, 0.5, 1)
        # --
        cr.move_to(xLeft, yTop+6)
        cr.line_to(xLeft, yTop)
        cr.line_to(xLeft+6, yTop)
        cr.move_to(xLeft, yBottom-6)
        cr.line_to(xLeft, yBottom)
        cr.line_to(xLeft+6, yBottom)
        # --
        cr.move_to(xRight, yTop+6)
        cr.line_to(xRight, yTop)
        cr.line_to(xRight-6, yTop)
        cr.move_to(xRight, yBottom-6)
        cr.line_to(xRight, yBottom)
        cr.line_to(xRight-6, yBottom)
        cr.stroke()

        # Draw sprites
        for i in range(0, self.nbCells):
            sprite = self.tblSprites[i]
            if sprite != None:
                w = sprite.surface.get_width()
                h = sprite.surface.get_height()
                x = allocation.width/2 - w/2
                y = self.cellSize*i + self.cellSize/2 - h/2
                cr.set_source_surface(sprite.surface, x, y)
                cr.paint()

        if self.idSequence>=0:
            # --
            left = (allocation.width - self.cellSize)/2
            right = left + self.cellSize
            sprite = self.tblSprites[self.idSequence]
            if sprite is not None:
                w = sprite.surface.get_width()
                h = sprite.surface.get_height()
                x = allocation.width/2 - w/2
                y = self.cellSize*self.nbCells + self.cellSize/2 - h/2
                cr.set_source_surface(sprite.surface, x, y)
                cr.paint()

            # Draw sequence mark
            top = self.idSequence * self.cellSize + 3
            bottom = top + self.cellSize - 2
            left += 1
            right -= 1
            cr.set_source_rgba(0.0, 0.0, 0.9, 1.0)
            cr.move_to(left, top)
            cr.line_to(right, top)
            cr.line_to(right, bottom)
            cr.line_to(left, bottom)
            cr.line_to(left, top)
            cr.stroke()
        

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
        minimum_height = 64
        natural_height = 64*8
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
        minimum_width = 64
        natural_width = 64
        return minimum_width, natural_width

    def do_button_press_event(self, event):
        mx = event.x
        my = event.y
        if event.button == 1:
            id = int((my-2)/self.cellSize)
            if (id != self.idSelect) and (id < self.nbCells):
                self.idSelect = id
                if self.tblSprites[id] == None:
                    sprite = Sprite()
                    self.tblSprites[id] = sprite
                else:
                    sprite = self.tblSprites[id]
                self.emit('sprite_change', sprite.surface)
                self.queue_draw()

    def get_current_sprite(self)->Sprite:
        sprite = self.tblSprites[self.idSelect]
        return sprite

    def new_current_sprite(self, iwidth, iheight):
        self.tblSprites[self.idSelect] = Sprite(iwidth,iheight)
        self.emit('sprite_change', self.tblSprites[self.idSelect].surface)
        self.queue_draw()


    def set_current_sprite(self, newSurface):
        sprite = self.tblSprites[self.idSelect]
        sprite.surface = newSurface
        self.emit('sprite_change', newSurface)
        self.queue_draw()

    def load_current_sprite(self, fileName):
        sprite = GdkPixbuf.Pixbuf.new_from_file(fileName)
        crSurface = Gdk.cairo_surface_create_from_pixbuf(sprite, 1, None)
        self.set_current_sprite(crSurface)

    def save_current_sprite(self, fileName):
        sprite = self.tblSprites[self.idSelect]
        sprite.surface.write_to_png(fileName)
        sprite.fileName = fileName

    def on_sprite_modified(self, sender):
        # Signal from EditArea fire after drawing action
        self.queue_draw()

    def next_sprite(self):
        while True:
            self.idSequence += 1
            if self.idSequence>=self.nbCells:
                self.idSequence = 0
            if self.tblSprites[self.idSequence] is not None:
                # print("Sprite {}".format(self.idSequence))
                self.queue_draw()
                break
        return True

    def play_sequence(self):
        self.idSequence = 0
        self.idTimer = GLib.timeout_add(900, self.next_sprite)
        self.queue_draw()

    def stop_sequence(self):
        if self.idTimer != 0:
            self.idSequence = -1
            GLib.source_remove(self.idTimer)
            self.queue_draw()

    def refresh_display(self):
        self.queue_draw()