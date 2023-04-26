from Unit import Unit
#requires Unit class, super weird

#Object to track what's in each grid square
class gridSquare(object):
    def __init__(self, TEAM, isBattleSquare, isBoarderSquare, currentUnits, x, y):
        self.TEAM = TEAM #BLUFOR is TRUE. OPFOR is FALSE.
        self.isBattleSquare = isBattleSquare #t/f
        self.isBoarderSquare = isBoarderSquare
        self.currentUnits = currentUnits #array of current units present
        self.x = x
        self.y = y
        self.BLU_points = 0
        self.OP_points = 0

    def getBattleStatus(self):
        return self.isBattleSquare
      
    def getCoord(self):
        coord = [self.x,self.y]
        return(coord)
      
    def getUnits(self):
        return self.currentUnits
      
    def addUnits(self, unitName, TEAM):
        self.currentUnits.append(Unit(unitName, TEAM, self.x, self.y))

    def hasUnits(self):
        if len(self.currentUnits) > 0:
            return True
        return False
      
    def addPoints(self, TEAM, points):
        if TEAM:
            self.BLU_points += points
            print("BLUFOR has scored " + str(points) + " point(s)!")
        else:
            self.OP_points += points
            print("OPFOR has scored " + str(points) + " point(s)!")