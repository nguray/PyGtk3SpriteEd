import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf
import cairo

from rrect import RRect
from editmode import EditMode

class SelectMode(EditMode):
    def __init__(self):
        EditMode.__init__(self)
        self.init_tool()

    def init_select(self):
        self.start_pix_x = 0
        self.start_pix_y = 0
        self.end_pix_x = 0
        self.end_pix_y = 0
        #--
        self.pt1_x = 0
        self.pt1_y = 0        
        self.pt2_x = 0
        self.pt2_y = 0
        #--
        self.select_state = 0
        self.rect_select_pix = RRect()
        self.select_move_flag = False

    def init_tool(self):
        #--
        self.left_top_rect = RRect()
        self.left_bottom_rect = RRect()
        self.right_top_rect = RRect()
        self.right_bottom_rect = RRect()
        #--
        self.left_top_handle = False
        self.left_bottom_handle = False
        self.right_top_handle = False
        self.right_bottom_handle = False
        #--
        self.init_select()
    
    def DrawHandle(self, cr : cairo.Context, r :RRect):
        #--
        r.Deflate(2, 2, 2, 2)
        cr.rectangle(r.left, r.top, r.Width(), r.Height())
        cr.fill()

    def PtInEditArea(self, x :int, y :int)->bool:
        #--
        return (x>=0) and (x<self.PixWidth*self.CellSize) and \
                (y>=0) and (y<self.PixHeight*self.CellSize)
       
    def do_button_press_event(self, event: Gdk.EventButton)->bool:
        #--
        tmx = event.x - EditMode.origin_x
        tmy = event.y - EditMode.origin_y

        px, py = self.MouseToPixel(tmx, tmy)

        if (self.select_state == 0):
            if (self.PtInEditArea(tmx, tmy)):
                self.select_state = 1
                self.pt1_x = tmx
                self.pt2_x = tmx
                self.pt1_y = tmy
                self.pt2_y = tmy
        elif (self.select_state == 2):
            if self.rect_select_pix.PtInRect(px, py):

                if self.right_bottom_rect.PtInRect(tmx, tmy):
                    self.right_bottom_handle = True
                    EditMode.window.set_cursor(EditMode.bottom_right_corner)
                elif self.right_top_rect.PtInRect(tmx, tmy):
                    self.right_top_handle = True
                    EditMode.window.set_cursor(EditMode.top_right_corner)
                elif self.left_top_rect.PtInRect(tmx, tmy):
                    self.left_top_handle = True
                    EditMode.window.set_cursor(EditMode.top_left_corner)
                elif self.left_bottom_rect.PtInRect(tmx, tmy):
                    self.left_bottom_handle = True
                    EditMode.window.set_cursor(EditMode.bottom_left_corner)
                else:
                    EditMode.window.set_cursor(EditMode.hand)
                    self.select_move_flag = True
                    EditMode.rect_copy_pix.Copy(self.rect_select_pix)
                    self.start_pix_x = px
                    self.start_pix_y = py
            else:
                self.init_tool()
                self.pt1_x = tmx
                self.pt2_x = tmx
                self.pt1_y = tmy
                self.pt2_y = tmy

        elif (self.select_state == 3):
            if self.rect_select_pix.PtInRect(px, py):
                EditMode.rect_copy_pix.Copy(self.rect_select_pix)
                self.start_pix_x = px
                self.start_pix_y = py
                self.select_move_flag = True
            else:
                self.init_tool()
                self.pt1_x = tmx
                self.pt2_x = tmx
                self.pt1_y = tmy
                self.pt2_y = tmy

        return True

    def do_button_release_event(self, event: Gdk.EventButton)->bool:
        # --
        self.left_top_handle = False
        self.left_bottom_handle = False
        self.right_top_handle = False
        self.right_bottom_handle = False
        self.select_move_flag = False
        EditMode.window.set_cursor(EditMode.arrow)
        if (self.select_state == 1):
            self.select_state = 2
            return True
        return False

    def do_motion_notify_event(self, event: Gdk.EventButton)->bool:
        # --
        tmx = event.x - EditMode.origin_x
        tmy = event.y - EditMode.origin_y
        
        if (self.select_state == 1):
            rightEdge = EditMode.PixWidth*self.CellSize
            bottomEdge = EditMode.PixHeight*self.CellSize
            if (tmx>rightEdge):
                self.pt2_x = rightEdge
            elif (tmx>=0):
                self.pt2_x = tmx
            else:
                self.pt2_x = 0

            if (tmy>bottomEdge):
                self.pt2_y = bottomEdge
            elif (tmy>=0):
                self.pt2_y = tmy
            else:
                self.pt2_y = 0
            #--
            if (self.pt1_x<self.pt2_x):
                left = self.pt1_x
                right = self.pt2_x
            else:
                left = self.pt2_x
                right = self.pt1_x
            
            if (self.pt1_y<self.pt2_y):
                top = self.pt1_y
                bottom = self.pt2_y
            else:
                top = self.pt2_y
                bottom = self.pt1_y
            
            if ((left!=right) and (top!=bottom)):
                self.rect_select_pix.top = int((top-2) / self.CellSize)
                self.rect_select_pix.left = int((left-2) / self.CellSize)
                x = right-2
                y = bottom-2
                self.rect_select_pix.right = int(x / self.CellSize)
                if (x % self.CellSize):
                    self.rect_select_pix.right += 1
                
                self.rect_select_pix.bottom = int(y / self.CellSize)
                if (y % self.CellSize):
                    self.rect_select_pix.bottom += 1
                return True
        elif (self.select_state==2):
            fModif = True
            if (event.state & Gdk.ModifierType.BUTTON1_MASK):
                if (self.right_bottom_handle or self.right_top_handle or 
                        self.left_top_handle or self.left_bottom_handle):
                    x = tmx - 2
                    y = tmy - 2
                    if (self.left_top_handle):
                        left = int(x / self.CellSize)
                        top = int(y / self.CellSize)
                        if ((left>=0) and (left < self.rect_select_pix.right)):
                            if (self.rect_select_pix.left != left):
                                fModif = True
                                self.rect_select_pix.left = left
                        if ((top>=0) and (top < self.rect_select_pix.bottom)):
                            if (self.rect_select_pix.top != top):
                                fModif = True
                                self.rect_select_pix.top = top
                    elif (self.left_bottom_handle):
                        left = int(x / self.CellSize)
                        bottom = int(y / self.CellSize)
                        if (y % self.CellSize):
                            bottom += 1
                        if ((left>=0) and (left < self.rect_select_pix.right)):
                            if (self.rect_select_pix.left != left):
                                fModif = True
                                self.rect_select_pix.left = left
                        if ((bottom<=EditMode.PixHeight) and (bottom > self.rect_select_pix.top)):
                            if (self.rect_select_pix.bottom != bottom):
                                fModif = True
                                self.rect_select_pix.bottom = bottom
                    elif (self.right_top_handle):
                        right = int(x / self.CellSize)
                        if (x % self.CellSize):
                            right += 1
                        top = int(y / self.CellSize)
                        if ((right <= EditMode.PixWidth) and
                                (right > self.rect_select_pix.left)):
                            if (self.rect_select_pix.right != right):
                                fModif = True
                                self.rect_select_pix.right = right
                        if ((top >= 0) and (top < self.rect_select_pix.bottom)):
                            if (self.rect_select_pix.top != top):
                                fModif = True
                                self.rect_select_pix.top = top

                    elif (self.right_bottom_handle):
                        fModif = False
                        right = int(x / self.CellSize)
                        if (x % self.CellSize):
                            right += 1
                        bottom = int(y / self.CellSize)
                        if (y % self.CellSize):
                            bottom += 1
                        if ((right <= EditMode.PixWidth) and
                                (right > self.rect_select_pix.left)):
                            if (self.rect_select_pix.right != right):
                                fModif = True
                                self.rect_select_pix.right = right
                        if ((bottom <= EditMode.PixHeight) and (bottom > self.rect_select_pix.top)):
                            if (self.rect_select_pix.bottom != bottom):
                                fModif = True
                                self.rect_select_pix.bottom = bottom
                elif (self.select_move_flag):
                    self.end_pix_x, self.end_pix_y = self.MouseToPixel(tmx, tmy)
                    vx = self.end_pix_x - self.start_pix_x
                    vy = self.end_pix_y - self.start_pix_y
                    self.rect_select_pix.Copy(EditMode.rect_copy_pix)
                    self.rect_select_pix.Offset(vx, vy)
                    fModif = True
            else:
                if self.right_bottom_rect.PtInRect(tmx, tmy):
                    EditMode.window.set_cursor(EditMode.bottom_right_corner)
                elif self.right_top_rect.PtInRect(tmx, tmy):
                    EditMode.window.set_cursor(EditMode.top_right_corner)
                elif self.left_top_rect.PtInRect(tmx, tmy):
                    EditMode.window.set_cursor(EditMode.top_left_corner)
                elif self.left_bottom_rect.PtInRect(tmx, tmy):
                    EditMode.window.set_cursor(EditMode.bottom_left_corner)
                else:
                    EditMode.window.set_cursor(EditMode.arrow)
                    x, y = self.MouseToPixel(tmx, tmy)
                    if self.rect_select_pix.PtInRect(x, y):
                        EditMode.window.set_cursor(EditMode.hand)
                    else:
                        EditMode.window.set_cursor(EditMode.arrow)
            return fModif

        elif (self.select_state==3):
            if (self.PtInEditArea(tmx, tmy)):
                if (self.select_move_flag):
                    self.end_pix_x, self.end_pix_y = self.MouseToPixel(tmx, tmy)
                    vx = self.end_pix_x - self.start_pix_x
                    vy = self.end_pix_y - self.start_pix_y
                    self.rect_select_pix.Copy(EditMode.rect_copy_pix)
                    self.rect_select_pix.Offset(vx, vy)
                    # -- restore backup
                    EditMode.RestoreSurface()
                    # --
                    rectSrc = RRect()
                    rectSrc.left = 0
                    rectSrc.top = 0
                    rectSrc.right = self.rect_select_pix.Width()
                    rectSrc.bottom = self.rect_select_pix.Height()
                    EditMode.BlitPixBuf(EditMode.CrSurface,self.rect_select_pix.left, self.rect_select_pix.top,
                                        EditMode.CrSurfaceCopy, rectSrc)
                    EditMode.window.set_cursor(EditMode.hand)
                else:
                    x, y = self.MouseToPixel(tmx, tmy)
                    if self.rect_select_pix.PtInRect( x, y):
                        EditMode.window.set_cursor(EditMode.hand)
                    else:
                        EditMode.window.set_cursor(EditMode.arrow)
                return True

        return False

    def do_draw(self, cr :cairo.Context):
        #--
        if self.select_state and (not self.rect_select_pix.IsNull()):
            cr.set_source_rgba(0.0, 0.0, 1.0, 1.0)
            cr.set_line_width(0.8)
            left, top = self.PixelToMouse(self.rect_select_pix.left,self.rect_select_pix.top)
            right, bottom = self.PixelToMouse(self.rect_select_pix.right,self.rect_select_pix.bottom)

            # cr.move_to(left, top)
            # cr.line_to(right, top)
            # cr.line_to(right, bottom)
            # cr.line_to(left, bottom)
            # cr.line_to(left, top)
            # cr.stroke()
            cr.set_source_rgba(0.0, 0.0, 1.0, 0.1)
            cr.rectangle(left,top,right-left,bottom-top)
            cr.fill()

            d = EditMode.CellSize
            cr.set_source_rgba(0.0, 0.0, 1.0, 1.0)
            #-- Draw resize Handles
            self.left_top_rect.left = left
            self.left_top_rect.top = top
            self.left_top_rect.right = left + d
            self.left_top_rect.bottom = top + d
            self.DrawHandle(cr, self.left_top_rect)

            self.left_bottom_rect.left = left 
            self.left_bottom_rect.top = bottom - d
            self.left_bottom_rect.right = left + d
            self.left_bottom_rect.bottom = bottom
            self.DrawHandle(cr, self.left_bottom_rect)

            self.right_top_rect.left = right - d
            self.right_top_rect.top = top
            self.right_top_rect.right = right
            self.right_top_rect.bottom = top + d
            self.DrawHandle(cr, self.right_top_rect)

            self.right_bottom_rect.left = right - d
            self.right_bottom_rect.top = bottom - d
            self.right_bottom_rect.right = right
            self.right_bottom_rect.bottom = bottom
            self.DrawHandle(cr, self.right_bottom_rect)


