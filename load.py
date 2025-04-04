class Load:
    def __init__(self,dimx,dimy,dimz,mass):
        g = 9.81
        self.dimx = dimx
        self.dimy = dimy
        self.dimz = dimz
        self.mass = mass
        self.weight = self.mass*g
        self.XZCrossSection = self.dimx*self.dimz
        self.YZCrossSection = self.dimy*self.dimz

        self.cgx = self.dimx/2
        self.cgy = self.dimy/2
        self.cgz = self.dimz/2
