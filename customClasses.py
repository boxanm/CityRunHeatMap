class Point:
    def __init__(self, latitude, longitude, prev):
        self.longitude = longitude
        self.latitude = latitude
        self.density = 1
        self.next = None
        self.prev = prev
        self.neighbor = None

    def addNext(self, next):
        self.next = next
    def addPrev(self, prev):
        self.prev = prev
    def addNeighbor(self,neighbor):#add density to neighbor as well?
        # self.neighbor = neighbor
        self.density+=neighbor.density
    def getLatLon(self):
        return (self.latitude,self.longitude)

    def __str__(self):
        return "[" + str(self.longitude) + "," + str(self.latitude)+ "]"


class Cell:
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude
        self.density = 0
        self.density_norm = 0
    def addUsage(self):
        self.density+=1
    def getLatLon(self):
        return (self.latitude,self.longitude)
    def __str__(self):
        return "[" + str(self.longitude) + "," + str(self.latitude)+ "]"
