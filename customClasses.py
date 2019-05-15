class Cell:
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude
        self.density = 0
        self.density_norm = 0
        self.color = 0
    def addUsage(self):
        self.density+=1
    def getLatLon(self):
        return (self.latitude,self.longitude)
    def __str__(self):
        return "[" + str(self.longitude) + "," + str(self.latitude)+ "]"
