import tkinter as tk

import random
class World:
    def __init__(self, size):
        self.size = size
        self.objects = [[None for i in range(size)] for j in range(size)]
        self.objectsMap = {}

    def updateObject(self, position:tuple, obj):
        x = position[0]
        y = position[1]
        self.objects[x][y] = obj
        if obj in self.objectsMap.keys():
            self.objectsMap[obj].append((x, y))
        else:
            self.objectsMap[obj] = [(x, y)]

    def getObject(self, position : tuple):
        return self.objects[position[0]][position[1]]

    def getPointsForObject(self, obj):
        return self.objectsMap[obj]


class Individual:
    def __init__(self, world: World,position:tuple):
        self.world = world
        self.position = position

    def action(self):
        pass


class MovableLifespannedIndividual(Individual):
    def __init__(self, speed,initial_lifespan ,world,position):
        super().__init__(world,position)
        self.speed = speed
        self.lifespan = initial_lifespan

    def action(self):
        DIRECTION = random.randint(1,4)
        if DIRECTION == 1: self.position[0] += 1
        elif DIRECTION == 2: self.position[0] -= 1
        elif DIRECTION == 3: self.position[1] += 1
        elif DIRECTION == 4: self.position[1] -= 1
        if self.world.getObject(self.position) == 1:
            self.lifespan += 5
        self.lifespan -= 1




root = tk.Tk()
root.geometry("800x800")
root.title("Simulation")
root.mainloop()
