
class RRect:

    def __init__(self,rectSrc: 'RRect' = None):
        if rectSrc is None:
            self.top = 0
            self.left = 0
            self.right = 0
            self.bottom = 0
            self.mode = 0
            self.seleted_corner = -1
            self.mouse_start_x = 0
            self.mouse_start_y = 0
            self.sav_top = 0
            self.sav_left = 0
            self.sav_right = 0
            self.sav_bottom = 0
        else:
            self.top = rectSrc.top
            self.left = rectSrc.left
            self.right = rectSrc.right
            self.bottom = rectSrc.bottom
            self.mode = 0
            self.seleted_corner = -1
            self.mouse_start_x = 0
            self.mouse_start_y = 0
            self.sav_top = 0
            self.sav_left = 0
            self.sav_right = 0
            self.sav_bottom = 0

    def Width(self):
        return abs(self.right - self.left)

    def Height(self):
        return abs(self.bottom-self.top)

    def Normalize(self):
        if (self.left>self.right):
            dum = self.left
            self.left = self.right
            self.right = dum

        if (self.top>self.bottom):
            dum = self.top
            self.top = self.bottom
            self.bottom = dum

    def Offset(self,dx :int, dy :int):
        self.left += dx
        self.right += dx
        self.top += dy
        self.bottom += dy

    def PtInRect(self, x :int, y :int):
        return (x>=self.left) and (x<=self.right) \
                and (y>=self.top) and (y<=self.bottom)  

    def Inflate(self, t :int, l:int, r :int, b :int):
        self.left   -= l
        self.right  += r
        self.top    -= t
        self.bottom += b

    def Deflate(self, t :int, l:int, r :int, b :int):
        self.left   += l
        self.right  -= r
        self.top    += t
        self.bottom -= b

    def IsNull(self):
        return ( (self.right-self.left)==0 and (self.bottom-self.top)==0 )

    def IsEmpty(self):
        return ( (self.right==self.left) or (self.bottom==self.top) )

    def SetNull(self):
        self.left = 0 
        self.top = 0
        self.right = 0
        self.bottom = 0

    def Copy(self,rectSrc: 'RRect'):
        if rectSrc is not None:
            self.top = rectSrc.top
            self.left = rectSrc.left
            self.right = rectSrc.right
            self.bottom = rectSrc.bottom

    def SetCorner(self, n:int, x:int, y:int):
        if n==0:
            self.left = x
            self.top = y
        elif n==1:
            self.right = x
            self.top = y
        elif n==2:
            self.right = x
            self.bottom = y
        else:
            self.left = x
            self.bottom = y

    def GetCorner(self, n:int):
        if n==0:
            return (self.left, self.top)
        elif n==1:
            return (self.right, self.top)
        elif n==2:
            return (self.right, self.bottom)
        else:
            return (self.left, self.bottom)

    def BackupPosition(self):
        self.sav_top = self.top
        self.sav_left = self.left
        self.sav_right = self.right
        self.sav_bottom = self.bottom

    def RestorePosition(self):
        self.top = self.sav_top
        self.left = self.sav_left
        self.right = self.sav_right
        self.bottom = self.sav_bottom


