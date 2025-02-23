from yik.dimensions import Dimension
from yik.interface import YikObject

class DimensionHolder(YikObject):

    def __init__(self, parent, *args, **kwargs):
        self.position = kwargs.get("position", Dimension(0, 0))
        YikObject.__init__(self, parent)



    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    @x.setter
    def x(self, value):
        self.position.x = value

    @y.setter
    def y(self, value):
        self.position.y = value


