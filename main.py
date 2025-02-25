import math
import parameters
import pynamics as pn
import random
import formulas
import matplotlib.pyplot as plt
import queue
TPS = parameters.TPS
DAY = parameters.DAY

CLOCK = None
BLOBS_PER_DAY = parameters.Num_food

ctx = pn.GameManager(pn.Dim(800, 800), tps=TPS, fps=0, event_tracker=True)
window = pn.ProjectWindow(ctx, size=pn.Dimension(800, 800))

SHELTERS = []
DELETE_QUEUE = []
DELETE_QUEUE_SIZE = parameters.Num_indi+parameters.Num_food
axis_x = []
axis_size = []
axis_sight = []
axis_speed = []
axis_population = []



class Blob(pn.GameObject):
    def __init__(self, world: pn.GameManager, size, x, y, nutrition: int):
        super().__init__(world, x, y, size, size,color="black",fill_color="blue")
        self.nutrition = nutrition
        for i in self.parent.objects:
            if isinstance(i, MovableIndividual):
                i.updateNearest()
    def delete(self):
        for i in self.parent.objects:
            if isinstance(i, MovableIndividual):
                i.updateNearest()

        DELETE_QUEUE.append(self)
        super().delete()



class MovableIndividual(pn.GameObject):
    def __init__(self, world: pn.PyNamical, size, x, y):
        self.nearest = None
        self.nearestDistance = 0
        self.speed = parameters.speed
        self.sight = parameters.sights
        self.energy = parameters.energy
        self.tmpDestination = pn.Dimension(0,0)


        super().__init__(world, x, y, size, size)
        self.energy_display = pn.Text(world, self.x, self.y + 10, font=pn.TextFont("Helvetica", 8))

        self.fill_color = "red"
        self.color = "black"

        self.status = "harvesting"
        self.noenergy = False
        self.ai = True
        self.target = None

        self.age = 0
        self.fissioned = False
    def delete(self):


        DELETE_QUEUE.append(self)
        super().delete()



    def pathfindNearestBlob(self):
        assert isinstance(self.parent, pn.GameManager)
        large = [math.inf, None]
        for i in self.parent.objects:
            if isinstance(i, Blob):
                dist = pn.utils.distance(i.position, self.position)
                if dist < large[0]:
                    large[0] = dist
                    large[1] = i
            if i is not self and isinstance(i, MovableIndividual) and (self.size.x - i.size.x) / i.size.x >= 0.2 :
                dist = pn.utils.distance(i.position, self.position)
                if dist < large[0]:
                    large[0] = dist
                    large[1] = i

        if large[1] and large[0] < self.sight:
            return large
        else:
            return None

    def updateNearest(self):

        near = self.pathfindNearestBlob()
        if near:
            self.nearest = near[1]
            self.nearestDistance = near[0]
        elif self.status == "sheltering":
            mind = math.inf
            minshelt = SHELTERS[0]

            for shelter in SHELTERS:
                dist = pn.utils.distance(self.position, shelter.position)

                if dist < mind:
                    mind = dist
                    minshelt = shelter

            self.nearest = minshelt
        else:
            self.nearest = None

            self.tmpDestination = pn.Dimension(random.randint(0,self.parent.width),random.randint(0,self.parent.height))
            self.nearestDistance = math.inf
    def updateNearestOnlyBlobs(self):
        near = self.pathfindNearestBlob()
        if near:
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
        if self.ai:
            if self.energy <= 0:
                self.delete()
                self.energy_display.delete()

                HUMANS.remove(self)


            if self.status == "sheltering" and CLOCK.during == "day":
                self.status = "harvesting"
                self.updateNearest()

            # if self.status == "harvesting" and CLOCK.during == "day":


            if self.status == "harvesting" and CLOCK.during == "night":
                self.status = "sheltering"
                self.updateNearest()
                # mind = math.inf
                # minshelt = SHELTERS[0]
                #
                # for shelter in SHELTERS:
                #     dist = pn.utils.distance(self.position, shelter.position)
                #
                #     if dist < mind:
                #         mind = dist
                #         minshelt = shelter
                #
                # self.nearest = minshelt

            #MOVING

            if self.nearest != None:

                self.nearestDistance = self.position.distance(self.nearest.position)

                cleanVal = self.nearest.position.subtract_dim(self.position)

                xchange = cleanVal.x / self.nearestDistance * self.speed * parameters.MOVE_SPEED_MULTIPLIER

                ychange = cleanVal.y / self.nearestDistance * self.speed * parameters.MOVE_SPEED_MULTIPLIER

            if self.nearest is None:
                self.nearestDistance = self.position.distance(self.tmpDestination)

                cleanVal = self.tmpDestination.subtract_dim(self.position)

                xchange = cleanVal.x / self.nearestDistance * self.speed

                ychange = cleanVal.y / self.nearestDistance * self.speed

                self.position.add_self(xchange, ychange)
                self.updateNearestOnlyBlobs()
                if self.nearestDistance < 2:
                    self.updateNearest()


            else:

                if isinstance(self.nearest, Shelter):
                    if self.collide(self.nearest):

                        xchange = 0
                        ychange = 0

                        self.noenergy = True
                        if not self.fissioned:
                            self.fissioned = True

                            half = self.energy / 2
                            self.energy = half

                            size = self.size.x
                            size += random.randint(-parameters.SIZE_MUTATE_INDEX, parameters.SIZE_MUTATE_INDEX)
                            size = max(size, 5)

                            newbaby = MovableIndividual(self.parent, size,
                                                        self.nearest.position.x + random.randint(25, 50),
                                                        self.nearest.position.y + random.randint(25, 50))
                            newbaby.energy = half
                            newbaby.fissioned = True
                            newbaby.noenergy = True
                            newbaby.sight = self.sight + random.randint(-parameters.SIGHT_MUTATE_INDEX,parameters.SIGHT_MUTATE_INDEX)
                            newbaby.speed += (random.random() - parameters.SPEED_MUTATE_INDEX) * 0.5
                            newbaby.status = "sheltering"
                            newbaby.nearest = self.nearest
                            newbaby.ai = False
                            self.ai = False
                            HUMANS.append(newbaby)

                elif isinstance(self.nearest, Blob):
                    self.noenergy = False
                    if self.fissioned:
                        self.fissioned = False
                    if self.collide(self.nearest):
                        self.nearest.delete()
                        self.energy += self.nearest.nutrition


                        self.nearest = None
                        self.nearestDistance = 0
                        assert isinstance(self.parent, pn.GameManager)

                        # b = Blob(ctx, 10, random.randint(0, 799), random.randint(0, 799), 10)
                        # FRUITS.append(b)
                        self.updateNearest()

                elif isinstance(self.nearest, MovableIndividual):
                    if (self.size.x - self.nearest.size.x) / self.nearest.size.x >= 0.2:
                        if self.collide(self.nearest):
                            self.nearest.energy_display.delete()
                            self.nearest.delete()

                            self.energy += self.nearest.energy


                            HUMANS.remove(self.nearest)
                            self.nearest = None

                            for human in HUMANS:
                                human.updateNearest()


                            self.updateNearest()




            self.position.add_self(xchange, ychange)


            if not self.noenergy: self.energy -= formulas.energy_use(self.size.x, self.speed, self.sight)

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

        self.recorded_date = None

        self.speed_avg = None
        self.size_avg = None
        self.sight_avg = None

        super().__init__(world, 400, 350, font=pn.TextFont("Helvetica", 12))


    def update(self):
        self.current += 1

        statistics = f"""Day {self.recorded_date} Statistics:
Average Speed: {self.speed_avg}
Average Size: {self.size_avg}
Average Sight: {self.sight_avg}"""

        self.text = f"Day {self.date} {self.during} ({self.current}/{self.half})\nPopulation: {len(HUMANS)}\n" + statistics


        if self.current >= self.half:
            self.current = 0

            if self.during == "day":
                self.during = "night"

                for human in HUMANS:
                    pn.Animation(pn.CubicBezier(0, 0, 0.58, 1), duration=32, fields=["r", "g", "b"]).play(human.energy_display.font.color, [255, 255, 255])

                ani = pn.Animation(pn.CubicBezier(0, 0, 0.58, 1), duration=32, fields=["r", "g", "b"])
                ani.play(window.color, [0, 0, 0])

                while len(FRUITS) > 0:
                    k = FRUITS.pop()
                    k.delete()
                for i in DELETE_QUEUE:
                    ctx.window.remove(i)
                    if isinstance(i, MovableIndividual):
                        ctx.window.remove(i.energy_display)
                    DELETE_QUEUE.remove(i)



            else:
                self.during = "day"

                self.recorded_date = self.date

                speed = 0
                size = 0
                sight = 0

                for human in HUMANS:
                    speed += human.speed
                    size += human.size.x
                    sight += human.sight

                self.speed_avg = speed / len(HUMANS)
                self.size_avg = size / len(HUMANS)
                self.sight_avg = sight / len(HUMANS)

                axis_x.append(self.date)
                axis_speed.append(self.speed_avg)
                axis_size.append(self.size_avg)
                axis_sight.append(self.sight_avg)
                axis_population.append(len(HUMANS))



                self.date += 1

                for human in HUMANS:
                    pn.Animation(pn.CubicBezier(0, 0, 0.58, 1), duration=32, fields=["r", "g", "b"]).play(human.energy_display.font.color, [0, 0, 0])
                    human.ai = True
                ani = pn.Animation(pn.CubicBezier(0, 0, 0.58, 1), duration=32, fields=["r", "g", "b"])
                ani.play(window.color, [255, 255, 255])

                for i in range(BLOBS_PER_DAY):
                    b = Blob(ctx, 10, random.randint(0, 799), random.randint(0, 799), parameters.NUTRITION)
                    FRUITS.append(b)

class Shelter(pn.GameObject):

    def __init__(self, world, x, y):
        super().__init__(world, x, y, 50, 50, color="black", fill_color="green")

        self.residents = 0
        self.resident = pn.Text(world, self.x + 25, self.y + 25, text="0/∞")

    def update(self):
        self.resident.text = f"{self.residents}/∞"
        # print(self.__pn_completed_initialization__)

shelter_a = Shelter(ctx, 0, 0)
shelter_b = Shelter(ctx, 750, 0)
shelter_c = Shelter(ctx, 750, 750)
shelter_d = Shelter(ctx, 0, 750)
SHELTERS.append(shelter_a)
SHELTERS.append(shelter_b)
SHELTERS.append(shelter_c)
SHELTERS.append(shelter_d)
shelter_a = Shelter(ctx, 0, 375)
shelter_b = Shelter(ctx, 375, 0)
shelter_c = Shelter(ctx, 750, 375)
shelter_d = Shelter(ctx, 375, 750)
SHELTERS.append(shelter_a)
SHELTERS.append(shelter_b)
SHELTERS.append(shelter_c)
SHELTERS.append(shelter_d)


HUMANS = []

FRUITS = []

for i in range(parameters.Num_indi):
    b2 = MovableIndividual(ctx, 10, random.randint(0, 799), random.randint(0, 799))
    b2.speed = random.randint(10000, 20000) / 10000
    HUMANS.append(b2)




for i in range(BLOBS_PER_DAY):
    b = Blob(ctx, 10, random.randint(0, 799), random.randint(0, 799), parameters.NUTRITION)
    FRUITS.append(b)

CLOCK = DayTimer(ctx)







ctx.start()

import matplotlib.pyplot as plt
import numpy as np
import time

# Initialize figure
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()

# Data for the plot


# Create two lines (plots)
line1, = ax.plot(axis_x, axis_sight, marker='o', linestyle='-', color='r', label="Avg Sight")
line2, = ax.plot(axis_x, axis_size, marker='o', linestyle='-', color='g', label="Avg Size")
line3, = ax.plot(axis_x, axis_speed, marker='o', linestyle='-', color='b', label="Avg Speed")
line4, = ax.plot(axis_x, axis_population, marker='o', linestyle='-', color='y', label="Population")

# Add a legend
ax.legend()

# Add points live
# for i in range(10):
#     x.append(i)
#     y1.append(i ** 2)  # Line 1: Example data
#     y2.append(i ** 1.5)  # Line 2: Example data
#
#     # Update both lines with new data
#     line1.set_xdata(x)
#     line1.set_ydata(y1)
#
#     line2.set_xdata(x)
#     line2.set_ydata(y2)
#
#     # Redraw the plot
#     fig.canvas.draw()
#     fig.canvas.flush_events()
#
#     # Pause to simulate live updating
#     plt.pause(0.5)

# Keep the plot open after the loop
plt.ioff()  # Turn off interactive mode
plt.show()
