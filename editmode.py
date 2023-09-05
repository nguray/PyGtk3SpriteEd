from typing import Tuple
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf
import cairo

from enum import Enum
from colorsBar import RColor 
from rrect import RRect

class ToolsMode(Enum):
    SELECT = 0
    PENCIL = 1
    RECTANGLE = 2
    ELLIPSE = 3
    FILL = 4


class EditMode:

    ForegroundColor = RColor(0, 0, 0, 255)
    BackgroundColor = RColor(0, 0, 0, 0)
    PixWidth = 32
    PixHeight = 32
    CellSize = 10.0
    CrSurface = None
    CrSurfaceBak = None
    window = None
    arrow = Gdk.Cursor(Gdk.CursorType.ARROW)
    hand = Gdk.Cursor(Gdk.CursorType.HAND1)
    bottom_left_corner = Gdk.Cursor(Gdk.CursorType.BOTTOM_LEFT_CORNER)
    bottom_right_corner = Gdk.Cursor(Gdk.CursorType.BOTTOM_RIGHT_CORNER)
    top_left_corner = Gdk.Cursor(Gdk.CursorType.TOP_LEFT_CORNER)
    top_right_corner = Gdk.Cursor(Gdk.CursorType.TOP_RIGHT_CORNER)
    #--
    CrSurfaceCopy = None
    rect_copy_pix = RRect()
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    #--
    scale = 1.0
    origin_x = 0
    origin_y = 0
    start_origin_x = 0
    start_origin_y = 0
    undo_mode = 0

    def __init__(self):
        pass

    @classmethod
    def MouseToPixel(cls, mx: int, my: int):
        return int((mx-2)/EditMode.CellSize), int((my-2)/EditMode.CellSize)

    @classmethod
    def PixelToMouse(cls, pixX: int, pixY: int)->Tuple[int,int] :
        return int(pixX*EditMode.CellSize+2), int(pixY*EditMode.CellSize+2)

    @classmethod
    def InEditArea(cls, px: int, py:int) -> bool:
        return (px>=0 and px<EditMode.PixWidth and py>=0 and py<EditMode.PixHeight)

    @classmethod
    def SetForegroundColor(cls, newColor: RColor):
        cls.ForegroundColor.red = newColor.red
        cls.ForegroundColor.green = newColor.green
        cls.ForegroundColor.blue = newColor.blue
        cls.ForegroundColor.alpha = newColor.alpha

    @classmethod
    def SetBackgroundColor(cls, newColor: RColor):
        cls.BackgroundColor.red = newColor.red
        cls.BackgroundColor.green = newColor.green
        cls.BackgroundColor.blue = newColor.blue
        cls.BackgroundColor.alpha = newColor.alpha

    @classmethod
    def BackupSurface(cls):
        cls.CrSurface.flush()
        sprite_bak = Gdk.pixbuf_get_from_surface(
            cls.CrSurface, 0, 0,
            cls.CrSurface.get_width(), cls.CrSurface.get_height())
        cls.CrSurfaceBak = Gdk.cairo_surface_create_from_pixbuf(
            sprite_bak, 1, None)

    @classmethod
    def RestoreSurface(cls):
        tblPixsDes = cls.CrSurface.get_data()
        tblPixsSrc = cls.CrSurfaceBak.get_data()
        for ip in range(0, cls.CrSurface.get_height()*cls.CrSurface.get_stride()):
            tblPixsDes[ip] = tblPixsSrc[ip]

    @classmethod
    def put_pixel(cls, x: int, y: int, color: RColor):
        tblPixs = cls.CrSurface.get_data()
        row_stride = int(cls.CrSurface.get_stride())
        n_channels = int(row_stride / cls.CrSurface.get_width())
        ip = int(row_stride *y + x * n_channels)
        tblPixs[ip] = color.blue  # blue
        tblPixs[ip+1] = color.green  # green
        tblPixs[ip+2] = color.red  # red
        tblPixs[ip+3] = color.alpha  # alpha

    @classmethod
    def get_pixel(cls, x: int, y: int):
        cls.CrSurface.flush()
        tblPixs = cls.CrSurface.get_data()
        row_stride = int(cls.CrSurface.get_stride())
        n_channels = int(row_stride / cls.CrSurface.get_width())
        ip = int(row_stride*y + x * n_channels)
        # ARGB
        return tblPixs[ip+3], tblPixs[ip+2], tblPixs[ip+1], tblPixs[ip]

    @classmethod
    def line(cls, x0: int, y0: int, x1: int, y1: int, color: RColor):
        cls.CrSurface.flush()
        width = cls.CrSurface.get_width()
        height = cls.CrSurface.get_height()
        if (((x0 >= 0 and x0 < width) and (y0 >= 0 and y0 < height)) and
                ((x1 >= 0 and x1 < width) and (y1 >= 0 and y1 < height))):
            steep = (abs(y1-y0) > abs(x1-x0))
            if (steep):
                dum = x0
                x0 = y0
                y0 = dum
                dum = x1
                x1 = y1
                y1 = dum

            if (x0 > x1):
                dum = x0
                x0 = x1
                x1 = dum
                dum = y0
                y0 = y1
                y1 = dum

            deltax = x1 - x0
            deltay = abs(y1-y0)
            error = deltax / 2

            y = y0
            if (y0 < y1):
                ystep = 1
            else:
                ystep = -1

            for x in range(x0, x1+1):
                if (steep):
                    cls.put_pixel(y, x, color)
                else:
                    cls.put_pixel(x, y, color)

                error = error - deltay
                if (error < 0):
                    y = y + ystep
                    error = error + deltax

    @classmethod
    def floodFill(cls, x0, y0, iTargetColor: RColor, iNewColor: RColor):

        cls.CrSurface.flush()
        a, r, g, b = cls.get_pixel(x0, y0)
        if iNewColor.alpha == a and iNewColor.red == r and \
                iNewColor.green == g and iNewColor.blue == b:
            return
        if iTargetColor.alpha != a or iTargetColor.red != r or \
                iTargetColor.green != g or iTargetColor.blue != b:
            return
        cls.put_pixel(x0, y0, iNewColor)
        if (y0 > 0):
            cls.floodFill(x0, y0 - 1, iTargetColor, iNewColor)
        if (y0 < cls.PixHeight - 1):
            cls.floodFill(x0, y0 + 1, iTargetColor, iNewColor)
        if x0 < cls.PixWidth - 1:
            cls.floodFill(x0 + 1, y0, iTargetColor, iNewColor)
        if x0 > 0:
            cls.floodFill(x0 - 1, y0, iTargetColor, iNewColor)
 
    @classmethod
    def BlitPixBuf(cls, destSurf: cairo.ImageSurface, destX: int, destY: int,
                   srcSurf: cairo.ImageSurface, srcRect: RRect):
        # ----------------------------------------------------------------------
        if ((destSurf is not None) and (srcSurf is not None)):

            srcSurf.flush()
            destSurf.flush()

            des_rowstride = destSurf.get_stride()
            src_rowstride = srcSurf.get_stride()

            des_n_channels = int (destSurf.get_stride()/destSurf.get_width())
            src_n_channels = int (srcSurf.get_stride()/srcSurf.get_width())

            src_format = srcSurf.get_format()
            des_format = destSurf.get_format()


            pixelsDest = destSurf.get_data()
            pixelsSrc = srcSurf.get_data()

            h = destSurf.get_height()
            w = destSurf.get_width()

            if src_format==des_format:
                yd = destY
                for y in range(srcRect.top, srcRect.bottom):
                    if (yd >= 0):
                        if (yd < h):
                            xd = destX
                            for x in range(srcRect.left, srcRect.right):
                                if (xd >= 0):
                                    if (xd < w):
                                        ipSrc = src_rowstride * y  +  x * src_n_channels
                                        ipDes = des_rowstride * yd + xd * des_n_channels
                                        pixelsDest[ipDes] = pixelsSrc[ipSrc]
                                        pixelsDest[ipDes+1] = pixelsSrc[ipSrc+1]
                                        pixelsDest[ipDes+2] = pixelsSrc[ipSrc+2]
                                        pixelsDest[ipDes+3] = pixelsSrc[ipSrc+3]
                                    else:
                                        break
                                # --
                                xd += 1
                        else:
                            break
                    # --
                    yd += 1

            else:
                yd = destY
                for y in range(srcRect.top, srcRect.bottom):
                    if (yd >= 0):
                        if (yd < h):
                            xd = destX
                            for x in range(srcRect.left, srcRect.right):
                                if (xd >= 0):
                                    if (xd < w):
                                        ipSrc = src_rowstride * y  +  x * src_n_channels
                                        ipDes = des_rowstride * yd + xd * des_n_channels
                                        _v0 = pixelsSrc[ipSrc]
                                        _v1 = pixelsSrc[ipSrc+1]
                                        _v2 = pixelsSrc[ipSrc+2]
                                        _v3 = pixelsSrc[ipSrc+3]
                                        if (src_format==cairo.Format.RGB24) :
                                            pixelsDest[ipDes] = _v0
                                            pixelsDest[ipDes+1] = _v1
                                            pixelsDest[ipDes+2] = _v2
                                            pixelsDest[ipDes+3] = 255
                                        elif (src_format==cairo.Format.ARGB32):
                                            pixelsDest[ipDes] = _v0      # B
                                            pixelsDest[ipDes+1] = _v1    # G
                                            pixelsDest[ipDes+2] = _v2    # R
                                            pixelsDest[ipDes+3] = _v3    # A

                                    else:
                                        break
                                # --
                                xd += 1
                        else:
                            break
                    # --
                    yd += 1

    @classmethod
    def FillPixBuf(cls, destSurf: cairo.ImageSurface, rectDes: RRect, color: RColor):
        # ----------------------------------------------------------------------
        if destSurf is not None:

            destSurf.flush()

            rowstride = destSurf.get_stride()
            pixelsDest = destSurf.get_data()

            h = destSurf.get_height()
            w = destSurf.get_width()

            for yd in range(rectDes.top, rectDes.bottom):
                if (yd >= 0):
                    if (yd < h):
                        for xd in range(rectDes.left, rectDes.right):
                            if (xd >= 0):
                                if (xd < w):
                                    ipDes = rowstride*yd + xd * 4
                                    pixelsDest[ipDes] = color.blue
                                    pixelsDest[ipDes+1] = color.green
                                    pixelsDest[ipDes+2] = color.red
                                    pixelsDest[ipDes+3] = color.alpha
                                else:
                                    break
                    else:
                        break

    @classmethod
    def FlipHorizontaly(cls, srcSurf: cairo.ImageSurface, desSurf:  cairo.ImageSurface):
        if (srcSurf is not None) and (desSurf is not None):
            srcSurf.flush()
            desSurf.flush()
            rowstride = desSurf.get_stride()

            pixelsDes = desSurf.get_data()
            pixelsSrc = srcSurf.get_data()

            height = desSurf.get_height()
            width = desSurf.get_width()
            n_channels = int (desSurf.get_stride()/desSurf.get_width())

            w = width-1
            for y in range(0,height):
                yOffset = y * rowstride
                for x in range(0,width):
                    iSrc = int(yOffset + x *n_channels)
                    iDes = int(yOffset + (w - x) * n_channels)
                    pixelsDes[iDes] = pixelsSrc[iSrc]
                    pixelsDes[iDes+1] = pixelsSrc[iSrc+1]
                    pixelsDes[iDes+2] = pixelsSrc[iSrc+2]
                    pixelsDes[iDes+3] = pixelsSrc[iSrc+3]

    @classmethod
    def FlipVerticaly(cls, srcSurf: cairo.ImageSurface, desSurf:  cairo.ImageSurface):
        if (srcSurf is not None) and (desSurf is not None):
            srcSurf.flush()
            desSurf.flush()
            rowstride = desSurf.get_stride()

            pixelsDes = desSurf.get_data()
            pixelsSrc = srcSurf.get_data()

            height = desSurf.get_height()
            width = desSurf.get_width()
            n_channels = int (desSurf.get_stride()/desSurf.get_width())

            h = height-1
            for y in range(0,height):
                yOffsetSrc = int(y * rowstride)
                yOffsetDes = int((h-y) * rowstride)
                for x in range(0,width):
                    iSrc = int(yOffsetSrc + x *n_channels)
                    iDes = int(yOffsetDes + x * n_channels)
                    pixelsDes[iDes] = pixelsSrc[iSrc]
                    pixelsDes[iDes+1] = pixelsSrc[iSrc+1]
                    pixelsDes[iDes+2] = pixelsSrc[iSrc+2]
                    pixelsDes[iDes+3] = pixelsSrc[iSrc+3]

    @classmethod
    def Swing90Left(cls):
        #cairo.ImageSurface(format, width, height)
        w = EditMode.CrSurface.get_width()
        h = EditMode.CrSurface.get_height()
        if w!=h :
            if h>w:
                d_max = h
            else:
                d_max = w
            EditMode.CrSurfaceBak = cairo.ImageSurface(EditMode.CrSurface.get_format(), d_max, d_max)
        srcRect = RRect()
        srcRect.left = 0
        srcRect.top  = 0
        srcRect.right= w
        srcRect.bottom = h
        EditMode.BlitPixBuf( EditMode.CrSurfaceBak, 0, 0, EditMode.CrSurface, srcRect)
        sprite = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, w, h)
        CrSurfaceDes = Gdk.cairo_surface_create_from_pixbuf(sprite, 1, None)

        row_stride_des = CrSurfaceDes.get_stride()
        pixels_des = CrSurfaceDes.get_data()
        n_channels_des = int (CrSurfaceDes.get_stride()/CrSurfaceDes.get_width())

        row_stride_src = EditMode.CrSurface.get_stride()
        pixels_src = EditMode.CrSurface.get_data()
        n_channels_src = int (EditMode.CrSurface.get_stride()/EditMode.CrSurface.get_width())

        offSetH = w - 1
        for x in range(0,w):
            for y in range(0,h):
                iSrc = x * n_channels_src + y * row_stride_src
                iDes = y * n_channels_des  + (offSetH-x) * row_stride_des
                pixels_des[iDes] = pixels_src[iSrc]
                pixels_des[iDes+1] = pixels_src[iSrc+1]
                pixels_des[iDes+2] = pixels_src[iSrc+2]
                pixels_des[iDes+3] = pixels_src[iSrc+3]
            
        EditMode.CrSurface = CrSurfaceDes
        EditMode.PixWidth  = h
        EditMode.PixHeight = w


    @classmethod
    def Swing90Right(cls):
        w = EditMode.CrSurface.get_width()
        h = EditMode.CrSurface.get_height()
        if w!=h :
            if h>w:
                d_max = h
            else:
                d_max = w
            EditMode.CrSurfaceBak = cairo.ImageSurface(EditMode.CrSurface.get_format(), d_max, d_max)
        srcRect = RRect()
        srcRect.left = 0
        srcRect.top  = 0
        srcRect.right= w
        srcRect.bottom = h
        EditMode.BlitPixBuf( EditMode.CrSurfaceBak, 0, 0, EditMode.CrSurface, srcRect)
        sprite = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, w, h)
        CrSurfaceDes = Gdk.cairo_surface_create_from_pixbuf(sprite, 1, None)

        row_stride_des = CrSurfaceDes.get_stride()
        pixels_des = CrSurfaceDes.get_data()
        n_channels_des = int (CrSurfaceDes.get_stride()/CrSurfaceDes.get_width())

        row_stride_src = EditMode.CrSurface.get_stride()
        pixels_src = EditMode.CrSurface.get_data()
        n_channels_src = int (EditMode.CrSurface.get_stride()/EditMode.CrSurface.get_width())

        offSetW = h - 1
        for x in range(0,w):
            for y in range(0,h):
                iSrc = x * n_channels_src + y * row_stride_src
                iDes = (offSetW-y) * n_channels_des  + x * row_stride_des
                pixels_des[iDes] = pixels_src[iSrc]
                pixels_des[iDes+1] = pixels_src[iSrc+1]
                pixels_des[iDes+2] = pixels_src[iSrc+2]
                pixels_des[iDes+3] = pixels_src[iSrc+3]
            
        EditMode.CrSurface = CrSurfaceDes
        EditMode.PixWidth  = h
        EditMode.PixHeight = w
