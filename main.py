import math

import pynamics as pn
import random

TPS = 128
DAY = TPS * 10

CLOCK = None

ctx = pn.GameManager(pn.Dim(10000, 10000), tps=TPS, fps=0, event_tracker=True)
window = pn.ProjectWindow(ctx, size=pn.Dimension(800, 800))

SHELTERS = []

class Blob(pn.GameObject):
    def __init__(self, world: pn.GameManager, size, x, y, nutrition: int):
        super().__init__(world, x, y, size, size,color="black",fill_color="blue")
        self.nutrition = nutrition
        for i in self.parent.objects:
            if isinstance(i, MovableIndividual):
                i.updateNearest()
        self.age = 0

    def update(self):
        self.age += 1

        if self.age >= DAY:
            self.delete()



class MovableIndividual(pn.GameObject):
    def __init__(self, world: pn.PyNamical, size, x, y):
        self.nearest = None
        self.nearestDistance = 0
        self.speed = 1.05

        self.energy = 500000

        self.sight = 10


        super().__init__(world, x, y, size, size)
        self.energy_display = pn.Text(world, self.x, self.y + 10, font=pn.TextFont("Helvetica", 8))

        self.fill_color = "red"
        self.color = "black"

        self.status = "harvesting"
        self.noenergy = False

        self.age = 0
        self.fissioned = False




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
    # def collide(self,other:Blob):
    #     points1 = self.getRealPoints()
    #     points2 = other.getRealPoints()
    #     topLeft1,botRight1 = points1[0],points1[2]
    #     topLeft2,botRight2 = points2[0],points2[2]
    #
    #     if self.rectangles_intersect((topLeft1[0],topLeft1[1],botRight1[0],botRight1[1]),(topLeft2[0],topLeft2[1],botRight2[0],botRight2[1])):
    #         return True
    #     else: return False
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

        # print("UPDATE")
        self.age += 1

        if self.energy <= 0:
            self.delete()
            self.energy_display.delete()


        if self.status == "sheltering" and CLOCK.during == "day":
            self.status = "harvesting"
            self.updateNearest()

        # if self.status == "harvesting" and CLOCK.during == "day":


        if self.status == "harvesting" and CLOCK.during == "night":
            self.status = "sheltering"

            mind = math.inf
            minshelt = SHELTERS[0]

            for shelter in SHELTERS:
                dist = pn.utils.distance(self.position, shelter.position)

                if dist < mind:
                    mind = dist
                    minshelt = shelter

            self.nearest = minshelt

        #MOVING


        self.nearestDistance = self.position.distance(self.nearest.position)

        cleanVal = self.nearest.position.subtract_dim(self.position)

        xchange = cleanVal.x / self.nearestDistance * self.speed * 2

        ychange = cleanVal.y / self.nearestDistance * self.speed * 2



        if isinstance(self.nearest, Blob):
            self.noenergy = False
            if self.fissioned:
                self.fissioned = False
            if self.collide(self.nearest):
                self.nearest.delete()
                self.nearest = None
                self.nearestDistance = 0
                assert isinstance(self.parent, pn.GameManager)

                b1 = Blob(ctx, 10, random.randint(0, 799), random.randint(0, 799), 10)

                self.energy += 100000
        if isinstance(self.nearest, Shelter):
            if self.collide(self.nearest):

                xchange = 0
                ychange = 0

                self.noenergy = True
                if not self.fissioned:
                    self.fissioned = True

                    half = self.energy / 2
                    self.energy = half

                    newbaby = MovableIndividual(self.parent, self.size.x, self.nearest.position.x + random.randint(25, 50), self.nearest.position.y + random.randint(25, 50))
                    newbaby.energy = half
                    newbaby.fissioned = True
                    newbaby.noenergy = True
                    newbaby.speed += (random.random() - 0.5) * 0.1


        self.position.add_self(xchange, ychange)


        if not self.noenergy: self.energy -= pow(self.size.x, 3) * pow(self.speed, 2) + self.sight

        try:
            self.energy_display.x = self.x
            self.energy_display.y = self.y + 50
            self.energy_display.text = "Energy: " + str(round(self.energy / 1000)) + "kJ\n" +\
            f"Size: {self.size.x}\n" +\
                f"Speed: {self.speed}\n" +\
                f"Sight: {self.sight}\n" +\
                f"Status: {self.status}\n" +\
                f"Age: {self.age}"
        except:
            pass

class DayTimer(pn.Text):

    def __init__(self, world):

        self.during = "day"
        self.half = int(DAY / 2)
        self.current = 0

        self.date = 1

        super().__init__(world, 400, 25, font=pn.TextFont("Helvetica", 12))


    def update(self):
        self.current += 1
        self.text = f"Day {self.date} {self.during} ({self.current}/{self.half})"


        if self.current >= self.half:
            self.current = 0

            if self.during == "day":
                self.during = "night"

                for human in HUMANS:
                    pn.Animation(pn.CubicBezier(0, 0, 0.58, 1), duration=32, fields=["r", "g", "b"]).play(human.energy_display.font.color, [255, 255, 255])

                ani = pn.Animation(pn.CubicBezier(0, 0, 0.58, 1), duration=32, fields=["r", "g", "b"])
                ani.play(window.color, [0, 0, 0])

            else:
                self.during = "day"
                self.date += 1

                for human in HUMANS:
                    pn.Animation(pn.CubicBezier(0, 0, 0.58, 1), duration=32, fields=["r", "g", "b"]).play(human.energy_display.font.color, [0, 0, 0])

                ani = pn.Animation(pn.CubicBezier(0, 0, 0.58, 1), duration=32, fields=["r", "g", "b"])
                ani.play(window.color, [255, 255, 255])

class Shelter(pn.GameObject):

    def __init__(self, world, x, y):
        super().__init__(world, x, y, 50, 50, color="black", fill_color="green")

        self.residents = 0
        self.resident = pn.Text(world, self.x + 25, self.y + 25, text="0/∞")

    def update(self):
        self.resident.text = f"{self.residents}/∞"

shelter_a = Shelter(ctx, 0, 0)
shelter_b = Shelter(ctx, 750, 0)
shelter_c = Shelter(ctx, 750, 750)
shelter_d = Shelter(ctx, 0, 750)
SHELTERS.append(shelter_a)
SHELTERS.append(shelter_b)
SHELTERS.append(shelter_c)
SHELTERS.append(shelter_d)


HUMANS = []

FRUITS = []

b2 = MovableIndividual(ctx, 10, 0, 0)
HUMANS.append(b2)
b2 = MovableIndividual(ctx, 10,  random.randint(0,799),random.randint(0,799))
HUMANS.append(b2)
b2 = MovableIndividual(ctx, 10,  random.randint(0,799),random.randint(0,799))
HUMANS.append(b2)



for i in range(10):
    b1 = Blob(ctx, 10, random.randint(0, 799), random.randint(0, 799), 10)


CLOCK = DayTimer(ctx)






ctx.start()
