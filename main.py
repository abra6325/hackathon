import math

import pynamics as pn
import random
ctx = pn.GameManager(pn.Dim(10000, 10000), tps=128, fps=0, event_tracker=True)
window = pn.ProjectWindow(ctx)


class Blob(pn.GameObject):
    def __init__(self, world: pn.GameManager, size, x, y, nutrition: int):
        super().__init__(world, x, y, size, size)
        self.nutrition = nutrition
        for i in self.parent.objects:
            if isinstance(i, MovableIndividual):
                i.updateNearest()

class MovableIndividual(pn.GameObject):
    def __init__(self, world: pn.PyNamical, size, x, y):
        self.nearest = None
        self.nearestDistance = 0
        self.speed = 1
        super().__init__(world, x, y, size, size)

    def pathfindNearestBlob(self):
        assert isinstance(self.parent, pn.GameManager)
        large = [math.inf, None]
        for i in self.parent.objects:
            if isinstance(i, Blob):
                dist = pn.utils.distance(i.position, self.position)
                if dist < large[0]:
                    large[0] = dist
                    large[1] = i
        if large[1]:
            return large
        else:
            return None

    def updateNearest(self):
        near = self.pathfindNearestBlob()
        self.nearest = near[1]
        self.nearestDistance = near[0]
    def collide(self,other:Blob):
        points1 = self.getRealPoints()
        points2 = other.getRealPoints()
        topLeft1,botRight1 = points1[0],points1[2]
        topLeft2,botRight2 = points2[0],points2[2]

        if self.rectangles_intersect((topLeft1[0],topLeft1[1],botRight1[0],botRight1[1]),(topLeft2[0],topLeft2[1],botRight2[0],botRight2[1])):
            return True
        else: return False
    def findCorners(self,points1):
        topLeft1 = points1[0]
        botRight1 = points1[1]
        for i in points1:
            if i[0] <= topLeft1[0] and i[1] >= topLeft1[1]:
                topLeft1 = i
            if i[0] >= botRight1[0] and i[1] <= botRight1[1]:
                botRight1 = i
        return list(topLeft1),list(botRight1)

    def rectangles_intersect(self,rect1, rect2):
        x1_top, y1_top, x1_bottom, y1_bottom = rect1
        x2_top, y2_top, x2_bottom, y2_bottom = rect2

        if (x1_bottom < x2_top or x2_bottom < x1_top or
                y1_bottom > y2_top or y2_bottom > y1_top):
            return False

        return True
    def rec_intersect(self, ax1: int, ay1: int, ax2: int, ay2: int, bx1: int, by1: int, bx2: int, by2: int) -> int:

        if ax1 >= bx2 or bx1 >= ax2 or ay1 >= by2 or by1 >= ay2:
            return True

        return False

    def update(self):
        if isinstance(self.nearest, Blob):
            self.nearestDistance = self.position.distance(self.nearest.position)

            cleanVal = self.nearest.position.subtract_dim(self.position)

            xchange = cleanVal.x / self.nearestDistance

            ychange = cleanVal.y / self.nearestDistance

            self.position.add_self(xchange, ychange)
            if self.collide(self.nearest):
                self.nearest.delete()
                self.nearest = None
                self.nearestDistance = 0
                assert isinstance(self.parent,pn.GameManager)
                b1 = Blob(ctx, 10, random.randint(0, 799), random.randint(0, 799), 10)


b2 = MovableIndividual(ctx, 10, 0, 0)
b2 = MovableIndividual(ctx, 10,  random.randint(0,799),random.randint(0,799))
b2 = MovableIndividual(ctx, 10,  random.randint(0,799),random.randint(0,799))
b1 = Blob(ctx, 10, random.randint(0,799),random.randint(0,799), 10)
b1 = Blob(ctx, 10, random.randint(0,799),random.randint(0,799), 10)
b1 = Blob(ctx, 10, random.randint(0,799),random.randint(0,799), 10)


ctx.start()
