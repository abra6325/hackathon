

def energy_use(size, speed, sight):
    e = pow(size, 3) * pow(speed, 2) + sight
    return e

def in_distance(x1, y1, x2, y2, d):
    return pow(d, 2) == pow(x2 - x1) + pow(y2 - y1)

