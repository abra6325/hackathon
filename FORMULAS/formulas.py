import math

def energy_use(size, speed, sight):
    e = pow(size, 3) * pow(speed, 2) + sight
    return e

def in_distance(x1, y1, x2, y2, d):
    return pow(d, 2) == pow(x2 - x1) + pow(y2 - y1)

def energy_used_to_sleep(x1, y1, x2, y2, size, speed, sight):
    #xy1 is coordinate of the individual.
    # xy2 is the size of the platform
    x_d = min(x1, x2-x1)
    y_d = min(y1, y2-y1) #move to closes edge
    e = energy_use(size, speed, sight)
    e_used = math.ceil(min(x_d, y_d) / speed) * e
    return e_used
