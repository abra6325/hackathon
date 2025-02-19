import pynamics as pn

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
        large = [0, None]
        for i in self.parent.objects:
            if isinstance(i, Blob):
                dist = pn.utils.distance(i.position, self.position)
                if dist > large[0]:
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
        p1 = self.points[0]
        p2 = None
        for i in self.points[1:]:
            if i[0] != p1[0] and i[1] != p1[1]:
                p2 = i
        q2 = None
        q1 = other.points[0]
        for i in other.points[1:]:
            if i[0] != q1[0] and i[1] != q1[1]:
                q2 = i
        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
        x3 = q1[0]
        y3 = q1[1]
        x4 = q2[0]
        y4 = q2[1]
        x5 = max(x1, x3)
        y5 = max(y1, y3)

        # gives top-right point
        # of intersection rectangle
        x6 = min(x2, x4)
        y6 = min(y2, y4)
        intersect = True
        # no intersection
        if x5 > x6 or y5 > y6:
            intersect = False
        return intersect

    def update(self):
        print(self.nearest)
        if isinstance(self.nearest, Blob):

            cleanVal = self.nearest.position.subtract_dim(self.position)

            xchange = cleanVal.x / self.nearestDistance

            ychange = cleanVal.y / self.nearestDistance

            self.position.add_self(xchange, ychange)
            if self.collide(self.nearest):
                self.nearest.delete()

b2 = MovableIndividual(ctx, 10, 0, 0)
b1 = Blob(ctx, 10, 500, 500, 10)


ctx.start()
