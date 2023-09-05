import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf
import cairo

from colorsBar import RColor
from rrect import RRect
from editmode import EditMode


class RectangleMode(EditMode):
    def __init__(self):
        EditMode.__init__(self)
        self.selectrect = RRect()
        self.init_tool()

    def init_tool(self):
        self.selectrect.SetNull()
        self.select_move_flag = False

    def DrawRectangle(self, x1, y1, x2, y2, color: RColor):
        if x1 > x2:
            dum = x2
            x2 = x1
            x1 = dum
        if y1 > y2:
            dum = y2
            y2 = y1
            y1 = dum
            
        if (x2 != x1) or (y2 != y1):
            # Tracer le rectangle
            stride = EditMode.CrSurface.get_stride()
            tblPixs = EditMode.CrSurface.get_data()
            for x in range(x1, x2+1):
                ip = stride*y1 + x * 4
                tblPixs[ip] = color.blue  # blue
                tblPixs[ip+1] = color.green  # green
                tblPixs[ip+2] = color.red  # red
                tblPixs[ip+3] = color.alpha  # alpha
                ip = stride*y2 + x * 4
                tblPixs[ip] = color.blue  # blue
                tblPixs[ip+1] = color.green  # green
                tblPixs[ip+2] = color.red  # red
                tblPixs[ip+3] = color.alpha  # alpha
            for y in range(y1, y2+1):
                ip = stride*y + x1 * 4
                tblPixs[ip] = color.blue  # blue
                tblPixs[ip+1] = color.green  # green
                tblPixs[ip+2] = color.red  # red
                tblPixs[ip+3] = color.alpha  # alpha
                ip = stride*y + x2 * 4
                tblPixs[ip] = color.blue  # blue
                tblPixs[ip+1] = color.green  # green
                tblPixs[ip+2] = color.red  # red
                tblPixs[ip+3] = color.alpha  # alpha

    def FillRectangle(self, x1, y1, x2, y2,color: RColor):
        if x1 > x2:
            dum = x2
            x2 = x1
            x1 = dum
        if y1 > y2:
            dum = y2
            y2 = y1
            y1 = dum

        if (x2 != x1) or (y2 != y1):
            stride = EditMode.CrSurface.get_stride()
            tblPixs = EditMode.CrSurface.get_data()
            for y in range(y1, y2+1):
                for x in range(x1, x2+1):
                    ip = stride*y + x * 4
                    tblPixs[ip] = color.blue  # blue
                    tblPixs[ip+1] = color.green  # green
                    tblPixs[ip+2] = color.red  # red
                    tblPixs[ip+3] = color.alpha  # alpha

    def hit_handle(self, mx, my)->int :
        id: int = -1
        #----------------------------------------------------------
        for i in range(0,4):
            px,py = self.selectrect.GetCorner(i)
            x,y = self.PixelToMouse( px, py)
            if (mx>=x) and mx<(x+self.CellSize) and (my>=y) and my<=(y+self.CellSize):
                id = i
                break
        return id

    def do_button_press_event(self, event: Gdk.EventButton)->bool:

        tmx = event.x - EditMode.origin_x
        tmy = event.y - EditMode.origin_y

        px, py = self.MouseToPixel(tmx, tmy)

        if self.InEditArea( px, py):
            # --
            if self.selectrect.mode==0:
                EditMode.BackupSurface()
                self.selectrect.SetCorner(0,px,py)
                self.selectrect.SetCorner(2,px,py)

            elif self.selectrect.mode==1:
                if self.selectrect.PtInRect(px,py):
                    id_handle = self.hit_handle(tmx,tmy)
                    if id_handle!=-1:
                        # Start mode Move Handle
                        self.selectrect.seleted_corner = id_handle
                    else:
                        # Start mode Move Select Rect
                        self.selectrect.mouse_start_x = tmx
                        self.selectrect.mouse_start_y = tmy
                        self.selectrect.BackupPosition()    
                
                else:
                    EditMode.BackupSurface()
                    self.selectrect.mode = 0
                    self.selectrect.SetCorner(0,px,py)
                    self.selectrect.SetCorner(2,px,py)
                    self.selectrect.seleted_corner = -1

        return True

    def do_button_release_event(self, event: Gdk.EventButton)->bool:
        if self.selectrect.mode==0 :
            x1, y1 = self.selectrect.GetCorner(0)
            x2, y2 = self.selectrect.GetCorner(2)
            if x1!=x2 and y1!=y2 :
                self.selectrect.Normalize()
                self.selectrect.mode = 1
        self.selectrect.seleted_corner = -1
        return True

    def do_motion_notify_event(self, event: Gdk.EventButton)->bool:

        tmx = event.x - EditMode.origin_x
        tmy = event.y - EditMode.origin_y

        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            color = EditMode.ForegroundColor
        elif event.state & Gdk.ModifierType.BUTTON3_MASK:
            color = EditMode.BackgroundColor
        else:
            color = None

        if color!=None :
            px, py = self.MouseToPixel(tmx, tmy)
            if self.InEditArea( px, py):
                # --
                if self.selectrect.mode==0:
                    self.selectrect.SetCorner(2, px, py)
                elif self.selectrect.mode==1:

                    if self.selectrect.seleted_corner!=-1:
                        self.selectrect.SetCorner(self.selectrect.seleted_corner, px, py)
                    else:
                        mdx = tmx - self.selectrect.mouse_start_x
                        mdy = tmy - self.selectrect.mouse_start_y
                        dx, dy = self.MouseToPixel( mdx, mdy)
                        if dx!=0 or dy!=0 :
                            left = self.selectrect.sav_left + dx
                            top  = self.selectrect.sav_top + dy
                            right= self.selectrect.sav_right + dx
                            bottom = self.selectrect.sav_bottom + dy
                            #
                            if left<0 or right>=self.PixWidth :
                                left  = self.selectrect.left
                                right = self.selectrect.right
                            if top<0 or bottom>=self.PixHeight :
                                top = self.selectrect.top
                                bottom = self.selectrect.bottom
                            self.selectrect.SetCorner(0, left, top)
                            self.selectrect.SetCorner(2, right, bottom)

                #--
                EditMode.RestoreSurface()
                if self.selectrect.right>self.selectrect.left :
                    x0 = self.selectrect.left
                    x1 = self.selectrect.right
                else:
                    x0 = self.selectrect.right
                    x1 = self.selectrect.left
                if self.selectrect.top<self.selectrect.bottom :
                    y0 = self.selectrect.top
                    y1 = self.selectrect.bottom
                else:
                    y0 = self.selectrect.bottom
                    y1 = self.selectrect.top

                #print("x0={} y0={} x1={} y1={}".format(x0,y0,x1,y1))
                if x0!=x1 and y0!=y1 :
                    if event.state & Gdk.ModifierType.CONTROL_MASK:
                        self.FillRectangle(x0, y0, x1, y1, color)
                    else:
                        self.DrawRectangle( x0, y0, x1, y1, color)
        return True

    def do_draw(self, cr: cairo.Context):
        #-----------------------------------------
        #-- Dessiner le rectangle de sélection
        if self.selectrect.IsEmpty()==False :
            #--
            px1, py1 = self.selectrect.GetCorner(0)
            px2, py2 = self.selectrect.GetCorner(2)

            x1, y1 = self.PixelToMouse(px1, py1)
            x2, y2 = self.PixelToMouse(px2, py2)

            if x1>x2 :
                dum = x1
                x1 = x2
                x2 = dum

            if y1>y2 :
                dum = y1
                y1 = y2
                y2 = dum

            #-- Draw Handles
            cr.set_source_rgba(0.0, 0.0, 1.0, 1.0)

            dx = self.CellSize - 5.0
            x = x1 + 2.0
            y = y1 + 2.0
            cr.rectangle(x, y, dx, dx)
            cr.fill()
            x = x2 + 2.0
            y = y1 + 2.0
            cr.rectangle(x, y, dx, dx)
            cr.fill()
            x = x2 + 2.0
            y = y2 + 2.0
            cr.rectangle(x, y, dx, dx)
            cr.fill()
            x = x1 + 2.0
            y = y2 + 2.0
            cr.rectangle(x, y, dx, dx)
            cr.fill()

            #-- Draw Frame
            left = x1
            top  = y1
            right = x2 + self.CellSize
            bottom = y2+ self.CellSize
            cr.set_source_rgba(0.0, 0.0, 1.0, 0.1)
            cr.rectangle(left,top,right-left,bottom-top)
            cr.fill()

