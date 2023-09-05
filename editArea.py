import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf

from editmode import EditMode,ToolsMode
from pencilmode import PencilMode
from rectanglemode import RectangleMode
from ellipsemode import EllipseMode
from fillmode import FillMode
from selectmode import SelectMode

from colorsBar import RColor
from enum import Enum
from rrect import RRect
import cairo


class EditArea(Gtk.Widget):

    __gtype_name__ = 'EditArea'

    # __gsignals__ = {
    #     'sprite_modified': (GObject.SIGNAL_RUN_FIRST, None,
    #                   ()),
    # }
    @GObject.Signal
    def sprite_modified(self):
        pass

    @GObject.Signal
    def sprite_transform(self, crSurface: GObject.TYPE_PYOBJECT):
        pass

    @GObject.Signal
    def pick_color(self, a: GObject.TYPE_INT, r: GObject.TYPE_INT, g: GObject.TYPE_INT, b: GObject.TYPE_INT):
        pass

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.set_size_request(80, 80)

        self.flagFirst = True

        self.pencilMode = PencilMode()
        self.rectangleMode = RectangleMode()
        self.ellipseMode = EllipseMode()
        self.fillMode = FillMode()
        self.selectMode = SelectMode()

    def do_draw(self, cr):
        # ------------------------------------------------
        cr.translate(EditMode.origin_x,EditMode.origin_y)

        allocation = self.get_allocation()

        bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
        cr.set_source_rgba(*list(bg_color))
        cr.paint()
        fg_color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        cr.set_source_rgba(*list(fg_color))

        EditMode.window = self.get_window()

        # Compute Cells size
        if allocation.width > allocation.height:
            d = allocation.height
        else:
            d = allocation.width
        if EditMode.PixWidth > EditMode.PixHeight:
            EditMode.CellSize = int((d - 4) / EditMode.PixWidth * EditMode.scale)
        else:
            EditMode.CellSize = int((d - 4) / EditMode.PixHeight * EditMode.scale)


        # Draw Grid
        for row in range(0, EditMode.PixHeight+1):
            y = row * EditMode.CellSize + 2
            for col in range(0, EditMode.PixWidth+1):
                x = col * EditMode.CellSize + 2
                cr.move_to(x-0.5, y)
                cr.line_to(x+0.5, y)
        cr.stroke()

        # if self.flagFirst:
        #     self.flagFirst = False
        # Create Sprite
        #self.sprite = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 32, 32)
        # self.sprite.fill(0x00000000)
        #self.crSurface = Gdk.cairo_surface_create_from_pixbuf( self.sprite,1,None)
        #stride = self.crSurface.get_stride()
        # cr1 = cairo.Context(self.crSurface)
        # cr1.set_source_rgba(1,0,0,1)
        # cr1.set_line_width(1)
        # cr1.set_antialias(cairo.ANTIALIAS_NONE)
        # cr1.move_to(0,1)
        # cr1.line_to(31,1)
        # cr1.stroke()
        # cr1.set_source_rgba(0,1,0,1)
        # cr1.move_to(0,2)
        # cr1.line_to(31,2)
        # cr1.stroke()
        # cr1.set_source_rgba(0,0,1,1)
        # cr1.move_to(0,3)
        # cr1.line_to(31,3)
        # cr1.stroke()
        # self.crSurface.mark_dirty()
        # self.crSurface.flush()
        # tblPixs = self.crSurface.get_data()
        # for i in range(0,self.pixWidth):
        #     ip = i * 4
        #     tblPixs[ip] = 255 # blue
        #     tblPixs[ip+1] = 0
        #     tblPixs[ip+2] = 0
        #     tblPixs[ip+3] = 255
        # for i in range(0,self.pixWidth):
        #     ip = stride + i * 4
        #     tblPixs[ip] = 0
        #     tblPixs[ip+1] = 255 # green
        #     tblPixs[ip+2] = 0
        #     tblPixs[ip+3] = 255
        # for i in range(0,self.pixWidth):
        #     ip = stride*2 + i * 4
        #     tblPixs[ip] = 0
        #     tblPixs[ip+1] = 0
        #     tblPixs[ip+2] = 255 # red
        #     tblPixs[ip+3] = 255
        # self.crSurface.mark_dirty()
        # self.crSurface.flush()
        #pixColor = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 1, 1)
        # pixColor.fill(0xff0000ff)
        # for i in range(0,32):
        #    pixColor.copy_area(0,0,1,1,self.sprite,i,i)

        # Draw Sprite method 1
        # cs = self.cellSize - 2
        # pixels = self.sprite.get_pixels()
        # for row in range(0,self.pixHeight):
        #     y = row * self.cellSize + 2
        #     for col in range(0,self.pixWidth):
        #         x = col * self.cellSize + 2
        #         i = (row*self.pixWidth + col)*4
        #         a = pixels[i+3]
        #         if a!=0:
        #             r = pixels[i]
        #             g = pixels[i+1]
        #             b = pixels[i+2]
        #             cr.set_source_rgba(r/255,g/255,b/255,a/255)
        #             cr.rectangle(x+1,y+1,cs,cs)
        #             cr.fill()

        # for i in range(0,2):
        #     ip = i*4
        #     print(tblPixs[ip],tblPixs[ip+1],tblPixs[ip+2],tblPixs[ip+3])
        # for i in range(0,2):
        #     ip = self.crSurface.get_stride() + i*4
        #     print(tblPixs[ip],tblPixs[ip+1],tblPixs[ip+2],tblPixs[ip+3])
        # for i in range(0,2):
        #     ip = self.crSurface.get_stride()*2 + i*4
        #     print(tblPixs[ip],tblPixs[ip+1],tblPixs[ip+2],tblPixs[ip+3])

        # cf = self.crSurface.get_format()
        # if cf==cairo.FORMAT_ARGB32:
        #     i = i + 4
        # self.crSurface.write_to_png('Test1.png')

        if EditMode.CrSurface != None:
            # Draw Sprite
            cs = EditMode.CellSize - 2
            tblPixs = EditMode.CrSurface.get_data()
            row_stride = EditMode.CrSurface.get_stride()
            n_channels = int (EditMode.CrSurface.get_stride()/EditMode.CrSurface.get_width())
            for row in range(0, EditMode.PixHeight):
                y = row * EditMode.CellSize + 2
                for col in range(0, EditMode.PixWidth):
                    x = col * EditMode.CellSize + 2
                    i = row * row_stride + col*n_channels
                    a = tblPixs[i+3]
                    if a != 0:
                        b = tblPixs[i]
                        g = tblPixs[i+1]
                        r = tblPixs[i+2]
                        cr.set_source_rgba(r/255, g/255, b/255, a/255)
                        cr.rectangle(x+1, y+1, cs, cs)
                        cr.fill()

            # cr.set_source_surface(self.crSurface,50,200)
            # cr.paint()

        self.editMode.do_draw(cr)

        # if EditMode.CrSurfaceBak!=None:
        #     cr.set_source_surface(EditMode.CrSurfaceBak,50,100)
        #     cr.paint()

        #Gdk.cairo_set_source_pixbuf(cr, self.sprite,50,50)
        # cr.paint()
        # self.sprite1 = Gdk.pixbuf_get_from_surface(self.crSurface,0,0,32,32)
        # Gdk.cairo_set_source_pixbuf(cr, self.sprite1,100,100)
        # cr.paint()

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
            | Gdk.EventMask.BUTTON1_MOTION_MASK | Gdk.EventMask.BUTTON3_MOTION_MASK | Gdk.EventMask.SCROLL_MASK
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
        minimum_height = 200
        natural_height = 200
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
        minimum_width = 200
        natural_width = 300
        return minimum_width, natural_width

    def do_button_press_event(self, event: Gdk.EventButton):
        # ------------------------------------------------
        if (event.button==2):
            EditMode.start_x = event.x
            EditMode.start_y = event.y
            EditMode.start_origin_x = EditMode.origin_x
            EditMode.start_origin_y = EditMode.origin_y
        else:
            if (event.button==1) and (event.state & Gdk.ModifierType.SHIFT_MASK):
                tmx = int(event.x - EditMode.origin_x)
                tmy = int(event.y - EditMode.origin_y)
                px, py = EditMode.MouseToPixel(tmx, tmy)
                a, r, g, b = EditMode.get_pixel( px, py)
                self.emit("pick_color", a, r, g, b)
    
            else:
                if self.editMode.do_button_press_event(event):
                    self.queue_draw()
                    self.emit("sprite_modified")
        

    def do_button_release_event(self, event):
        # ------------------------------------------------
        if self.editMode.do_button_release_event(event):
            self.queue_draw()
            self.emit("sprite_modified")

    def do_motion_notify_event(self, event):
        # ------------------------------------------------
        if (event.state & Gdk.ModifierType.BUTTON2_MASK):
            dx = event.x - EditMode.start_x
            dy = event.y - EditMode.start_y
            EditMode.origin_x = EditMode.start_origin_x + dx
            EditMode.origin_y = EditMode.start_origin_y + dy
            self.queue_draw()
        else:
            if self.editMode.do_motion_notify_event(event):
                self.queue_draw()
                self.emit("sprite_modified")

    def do_scroll_event(self, event):
        # ------------------------------------------------
        if event.direction==Gdk.ScrollDirection.UP:
            if EditMode.scale<5.0:
                EditMode.scale += 0.05
        elif event.direction==Gdk.ScrollDirection.DOWN:
            if EditMode.scale>0.5:
                EditMode.scale -= 0.05
        self.queue_draw()

    def set_foreground_color_cb(self, sender, newColor: RColor):
        # ------------------------------------------------
        EditMode.SetForegroundColor(newColor)

    def set_background_color_cb(self, sender, newColor: RColor):
        # ------------------------------------------------
        EditMode.SetBackgroundColor(newColor)

    def set_sprite(self, newSurface: cairo.ImageSurface):
        # ------------------------------------------------
        EditMode.CrSurface = newSurface
        EditMode.PixWidth = newSurface.get_width()
        EditMode.PixHeight = newSurface.get_height()
        self.queue_draw()

    def set_tool(self, tool: ToolsMode):
        # ------------------------------------------------
        self.selectMode.init_tool()
        self.pencilMode.init_tool()
        self.rectangleMode.init_tool()
        self.ellipseMode.init_tool()
        self.fillMode.init_tool()
        if tool == ToolsMode.SELECT:
            self.editMode = self.selectMode
        elif tool == ToolsMode.PENCIL:
            self.editMode = self.pencilMode
        elif tool == ToolsMode.RECTANGLE:
            self.editMode = self.rectangleMode
        elif tool == ToolsMode.ELLIPSE:
            self.editMode = self.ellipseMode
        elif tool == ToolsMode.FILL:
            self.editMode = self.fillMode
        self.queue_draw()

    def undo(self):
        # ------------------------------------------------
        EditMode.RestoreSurface()
        self.queue_draw()

    def copy_select(self):
        # ------------------------------------------------
        if self.editMode == self.selectMode:
            if EditMode.CrSurfaceCopy is None:
                pixbuf_tmp = Gdk.pixbuf_get_from_surface(
                    EditMode.CrSurface, 0, 0,
                    EditMode.CrSurface.get_width(), EditMode.CrSurface.get_height())
                EditMode.CrSurfaceCopy = Gdk.cairo_surface_create_from_pixbuf(
                    pixbuf_tmp, 1, None)
            EditMode.BlitPixBuf(EditMode.CrSurfaceCopy, 0, 0, EditMode.CrSurface, self.selectMode.rect_select_pix)
            #EditMode.rect_copy_pix.Copy(self.selectMode.rect_select_pix)
            EditMode.rect_copy_pix.left = 0
            EditMode.rect_copy_pix.top = 0
            EditMode.rect_copy_pix.right = self.selectMode.rect_select_pix.Width()
            EditMode.rect_copy_pix.bottom = self.selectMode.rect_select_pix.Height()

            pixbuf_tmp1 = Gdk.pixbuf_get_from_surface(
                    EditMode.CrSurface, self.selectMode.rect_select_pix.left, self.selectMode.rect_select_pix.top,
                    self.selectMode.rect_select_pix.Width(), self.selectMode.rect_select_pix.Height())
            #sel_surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf_tmp1, 1, None)
            #sel_surface.write_to_png("ClipXX1.png")
            #EditMode.CrSurfaceCopy.write_to_png("ClipX.png")
            #pixbuf_tmp1.savev("ClipX.png","png",[None],[])
            EditMode.clipboard.set_image(pixbuf_tmp1)

            self.selectMode.init_select()
            self.queue_draw()

    def paste_copy(self):
        # ------------------------------------------------
        self.set_tool(ToolsMode.SELECT)
        EditMode.BackupSurface()
   
        image = EditMode.clipboard.wait_for_image()
        if image is not None:
            #
            EditMode.CrSurfaceCopy = cairo.ImageSurface(EditMode.CrSurface.get_format(),\
                                        image.get_width(), image.get_height())
            w = image.get_width()
            h = image.get_height()
            #EditMode.CrSurfaceCopy.write_to_png("ClipXX2.png")
            EditMode.rect_copy_pix.left = 0
            EditMode.rect_copy_pix.top = 0
            EditMode.rect_copy_pix.right = w
            EditMode.rect_copy_pix.bottom = h
            self.selectMode.rect_select_pix.Copy(EditMode.rect_copy_pix)
            ClipSurf = Gdk.cairo_surface_create_from_pixbuf( image, 1, None)
            #ClipSurf.write_to_png("ClipXX2.png")
            EditMode.BlitPixBuf(EditMode.CrSurfaceCopy, 0, 0, ClipSurf, self.selectMode.rect_select_pix)
            #sprite = GdkPixbuf.Pixbuf.new_from_file("ClipXX2.png")
            #EditMode.CrSurfaceCopy = Gdk.cairo_surface_create_from_pixbuf( sprite, 1, None)
            EditMode.BlitPixBuf(EditMode.CrSurface,\
                self.selectMode.rect_select_pix.left,\
                self.selectMode.rect_select_pix.top,\
                EditMode.CrSurfaceCopy, self.selectMode.rect_select_pix)

            self.selectMode.select_state = 3
            self.queue_draw()
            self.emit("sprite_modified")

    def cut_select(self):
        # -----------------------------------------------
        if self.editMode == self.selectMode:
            if EditMode.CrSurfaceCopy is None:
                pixbuf_tmp = Gdk.pixbuf_get_from_surface(
                    EditMode.CrSurface, 0, 0,
                    EditMode.CrSurface.get_width(), EditMode.CrSurface.get_height())
                EditMode.CrSurfaceCopy = Gdk.cairo_surface_create_from_pixbuf(
                    pixbuf_tmp, 1, None)
            EditMode.BlitPixBuf(EditMode.CrSurfaceCopy, 0, 0, EditMode.CrSurface, self.selectMode.rect_select_pix)
            EditMode.BackupSurface()
            pixbuf_tmp1 = Gdk.pixbuf_get_from_surface(
                    EditMode.CrSurface, self.selectMode.rect_select_pix.left, self.selectMode.rect_select_pix.top,
                    self.selectMode.rect_select_pix.Width(), self.selectMode.rect_select_pix.Height())
            EditMode.clipboard.set_image(pixbuf_tmp1)

            EditMode.FillPixBuf(EditMode.CrSurface, self.selectMode.rect_select_pix, EditMode.BackgroundColor)
            EditMode.rect_copy_pix.Copy(self.selectMode.rect_select_pix)
            self.selectMode.init_select()
            self.queue_draw()
            self.emit("sprite_modified")
        
    def flip_horizontaly(self):
        # -----------------------------------------------
        EditMode.BackupSurface()
        EditMode.FlipHorizontaly(EditMode.CrSurfaceBak,EditMode.CrSurface)
        self.queue_draw()
        self.emit("sprite_modified")

    def flip_verticaly(self):
        # -----------------------------------------------
        EditMode.BackupSurface()
        EditMode.FlipVerticaly(EditMode.CrSurfaceBak,EditMode.CrSurface)
        self.queue_draw()
        self.emit("sprite_modified")

    def swing_90_left(self):
        # -----------------------------------------------
        self.selectMode.init_tool()
        self.pencilMode.init_tool()
        self.rectangleMode.init_tool()
        self.ellipseMode.init_tool()
        self.fillMode.init_tool()
        EditMode.Swing90Left()
        self.queue_draw()
        self.emit("sprite_transform",EditMode.CrSurface)

    def swing_90_right(self):
        # -----------------------------------------------
        self.selectMode.init_tool()
        self.pencilMode.init_tool()
        self.rectangleMode.init_tool()
        self.ellipseMode.init_tool()
        self.fillMode.init_tool()
        EditMode.Swing90Right()
        self.queue_draw()
        self.emit("sprite_transform",EditMode.CrSurface)
