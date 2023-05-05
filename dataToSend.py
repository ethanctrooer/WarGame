from Unit import Unit
#object for data transfer between server & client
#TODO: rename this to dataPacket at some point

class dataToSend(object):

    def __init__(self):
            self.units = []
            self.gridSquares = []
            self.TEAM = True #default value #identifies what player this was sent by/to

    #set object team to unit's team
    #this jank af can add discrete definition in intiailizater
    #def addUnit(self, name, coord, TEAM):
    def addUnit(self, Unit, TEAM):
            self.TEAM = TEAM
            #try:
            #      x, y = coord[0], coord[1]
            #      self.units.append(Unit(name, TEAM, x, y))
            #except Exception as e:
            #      print(e)
            self.units.append(Unit)

    def getUnits(self):
           return self.units

    def addGridSquare(self, gridSquareObj):
          self.gridSquares.append(gridSquareObj)
    
    def getGridSquares(self):
           return self.gridSquares
      