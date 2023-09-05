import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf
import cairo

from colorsBar import RColor
from rrect import RRect
from editmode import EditMode

class EllipseMode(EditMode):
    def __init__(self):
        EditMode.__init__(self)
        self.selectrect = RRect()
        self.init_tool()

    def init_tool(self):
        self.selectrect.SetNull()
        self.select_move_flag = False

    def ellipse1(self, cx: int, cy: int, a: int, b: int, color: RColor):
        x = 0
        y = b
        a2 = int(a*a)
        b2 = int(b*b)
        crit1 = -(a2/4 + a % 2 + b2)
        crit2 = -(b2/4 + b % 2 + a2)
        crit3 = -(b2/4 + b % 2)
        t = -a2*y
        dxt = 2*b2*x
        dyt = -2*a2*y
        d2xt = 2*b2
        d2yt = 2*a2

        while (y >= 0 and x <= a):

            EditMode.put_pixel(cx+x, cy+y, color)

            if (x != 0 or y != 0):
                EditMode.put_pixel(cx-x, cy-y, color)

            if (x != 0 and y != 0):
                EditMode.put_pixel(cx+x, cy-y, color)
                EditMode.put_pixel(cx-x, cy+y, color)

            if ((t+b2*x <= crit1) or (t+a2*y <= crit3)):
                x += 1
                dxt += d2xt
                t += dxt
            elif ((t-a2*y) > crit2):
                y -= 1
                dyt += d2yt
                t += dyt
            else:
                x += 1
                dxt += d2xt
                t += dxt
                y -= 1
                dyt += d2yt
                t += dyt

    def DrawHorizontalLine(self, xleft: int, xright: int, y: int, color):
        stride = EditMode.CrSurface.get_stride()
        tblPixs = EditMode.CrSurface.get_data()
        for x in range(xleft, xright+1):
            ip = stride*int(y) + int(x) * 4
            tblPixs[ip] = color.blue  # blue
            tblPixs[ip+1] = color.green  # green
            tblPixs[ip+2] = color.red  # red
            tblPixs[ip+3] = color.alpha  # alpha

    def fillEllipse1(self, left, top, right, bottom, color):

        if (right < left):
            temp = left
            left = right
            right = temp

        if(bottom < top):
            temp = top
            top = bottom
            bottom = temp

        a = (right - left) >> 1
        b = (bottom - top) >> 1

        x = 0
        y = b

        a2 = a * a
        b2 = b * b
        a2b2  = a2 + b2
        a2sqr = a2 + a2
        b2sqr = b2 + b2
        a4sqr = a2sqr + a2sqr
        b4sqr = b2sqr + b2sqr
        a8sqr = a4sqr + a4sqr
        b8sqr = b4sqr + b4sqr
        a4sqr_b4sqr: int = a4sqr + b4sqr

        fn   = a8sqr + a4sqr
        fnn  = a8sqr
        fnnw = a8sqr
        fnw  = a8sqr + a4sqr - b8sqr * a + b8sqr
        fnwn = a8sqr
        fnwnw = a8sqr + b8sqr
        fnww  = b8sqr
        fwnw  = b8sqr
        fww   = b8sqr
        d1    = b2 - b4sqr * a + a4sqr

        while((fnw < a2b2) or (d1 < 0) or ((fnw - fn > b2) and (y > 0))):

            self.DrawHorizontalLine(left + x, right - x, top + y, color)
            self.DrawHorizontalLine(left + x, right - x, bottom - y, color)

            y -= 1
            if((d1 < 0) or (fnw - fn > b2)):

                d1 += fn
                fn += fnn
                fnw += fnwn
            else:
                x += 1
                d1 += fnw
                fn += fnnw
                fnw += fnwnw

        fw = fnw - fn + b4sqr
        d2 = d1 + (fw + fw - fn - fn + a4sqr_b4sqr + a8sqr) / 4
        fnw += b4sqr - a4sqr

        old_y = y + 1

        while(x <= a):

            if(y != old_y):  # prevent overdraw
                self.DrawHorizontalLine(left + x, right - x, top + y, color)
                self.DrawHorizontalLine(left + x, right - x, bottom - y, color)

            old_y = y
            x += 1
            if(d2 < 0):
                y -= 1
                d2 += fnw
                fw += fwnw
                fnw += fnwnw
            else:
                d2 += fw
                fw += fww
                fnw += fnww


    def BorderEllipse(self, left, top, right, bottom, col):

        a: int = int ((right - left) / 2)
        b: int = int ((bottom - top) / 2)

        x = 0
        y = b

        a2 = a * a
        b2 = b * b
        a2b2 = a2 + b2
        a2sqr = a2 + a2
        b2sqr = b2 + b2
        a4sqr = a2sqr + a2sqr
        b4sqr = b2sqr + b2sqr
        a8sqr = a4sqr + a4sqr
        b8sqr = b4sqr + b4sqr
        a4sqr_b4sqr = a4sqr + b4sqr

        _fn = a8sqr + a4sqr
        _fnn = a8sqr
        _fnnw = a8sqr
        _fnw = a8sqr + a4sqr - b8sqr * a + b8sqr
        _fnwn = a8sqr
        _fnwnw = a8sqr + b8sqr
        _fnww = b8sqr
        _fwnw = b8sqr
        _fww = b8sqr
        d1 = b2 - b4sqr * a + a4sqr

        while ((_fnw < a2b2) or (d1 < 0) or (((_fnw - _fn) > b2) and (y > 0))) :

            EditMode.put_pixel(left+x, top+y, col)
            EditMode.put_pixel(right-x, top+y, col)
            EditMode.put_pixel(left+x, bottom-y, col)
            EditMode.put_pixel(right-x, bottom-y, col)

            y -= 1
            if ((d1 < 0) or ((_fnw - _fn) > b2)) :
                d1 += _fn
                _fn += _fnn
                _fnw += _fnwn
            else:
                x += 1
                d1 += _fnw
                _fn += _fnnw
                _fnw += _fnwnw
            

        _fw = _fnw - _fn + b4sqr
        d2 = d1 + (_fw + _fw - _fn - _fn + a4sqr_b4sqr + a8sqr) / 4
        _fnw = _fnw + (b4sqr - a4sqr)

        while (x <= a) :

            EditMode.put_pixel(left+x, top+y, col)
            EditMode.put_pixel(right-x, top+y, col)
            EditMode.put_pixel(left+x, bottom-y, col)
            EditMode.put_pixel(right-x, bottom-y, col)

            x += 1
            if (d2 < 0) :
                y -= 1
                d2 += _fnw
                _fw += _fwnw
                _fnw += _fnwnw
            else:
                d2 += _fw
                _fw += _fww
                _fnw += _fnww


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
                        self.fillEllipse1(x0, y0, x1, y1, color)
                    else:
                        self.BorderEllipse( x0, y0, x1, y1, color)

        return True


    def do_draw(self, cr):
        #---------------------------------------------------------
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
