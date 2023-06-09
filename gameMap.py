import numpy as np
from gridSquare import gridSquare

class gameMap(object):

      def __init__(self, blockSize, MAP_WIDTH):
            self.numBlocks = int(MAP_WIDTH / blockSize)
            #print(self.numBlocks)
            self.blockSize = blockSize #change size of map with either blocksize or windowsize
            self.mapArray = np.array([ [[gridSquare(True, False, False, [], i, j),] for j in range(self.numBlocks)] for i in range(self.numBlocks) ])

            #test units
            #self.mapArray[1][1][0].addUnits("Interceptor", True)
            #self.mapArray[1][2][0].addUnits("Interceptor", False)
            #self.mapArray[1][2][0].addUnits("Interceptor", True)

            #self.mapArray[3][15][0].addUnits("Interceptor", False)
            #self.mapArray[3][17][0].addUnits("Gunship", True)

            #self.mapArray[15][2][0].addUnits("Interceptor", False)
            #self.mapArray[20][2][0].addUnits("Fighter", False)
            #self.mapArray[17][2][0].addUnits("Gunship", True)

            self.battleCitiesAndBorders = []

            #self.makeBattleCities(3)

            self.calcBattle()

      def makeBattlesAndBorders(self, numBattles):
            #remove all previous battle cities
            for e in self.battleCitiesAndBorders:
                  e.isBattleSquare = False
                  e.isBorderSquare = False

            retval = []
            battleSquares = numBattles #set number of battle squares
            xCoordBorder = int(self.numBlocks/2) #set x coordinate of border, just in the middle right now
            randBattleCities = np.random.randint(0, len(self.mapArray[xCoordBorder][:]), battleSquares).tolist() #sometimes only generates 2 for some reason, good bug

            #add spacing of 1 between battle cities - doesn't work lmao
            while 1 in np.diff(randBattleCities):
                  randBattleCities = np.random.randint(0, len(self.mapArray[xCoordBorder][:]), battleSquares).tolist()

            #set gridObj values: border cities & set 3 random cities to battle squares
            for id, e in enumerate(self.mapArray[xCoordBorder][:]): #select column at border x coordinate
                  #select grid square
                  #gridObj = e[0] 
                  #e[0] is the grid object as above
                  if id in randBattleCities:
                        e[0].isBattleSquare = True #set battle squares
                  e[0].isBorderSquare = True
                  retval.append(e[0])
                  self.battleCitiesAndBorders.append(e[0]) #intention - append reference to object, which is an object from the map.

            return retval
      
      #stolen from https://www.geeksforgeeks.org/find-if-a-point-lies-inside-or-on-circle/
      def isInside(self, circle_x, circle_y, rad, x, y):
            # Compare radius of circle with distance of 
            # its center from given point
            if ((x - circle_x) * (x - circle_x) +
                  (y - circle_y) * (y - circle_y) <= rad * rad):
                  return True
            else:
                  return False

      #TODO: move to server side
      #TODO: change order to match C/Maj. Baschy's code
      #RETURN: [Blufor points, Opfor points]
      def calcBattle(self):
            airUnits = self.getUnits() #returns Unit objects
            BLUFOR_points = 0 #only total points, not points per battle square
            OPFOR_points = 0

            #NOTE: implement interceptor/fighter checks before bombers?
            #Add up all defense checks for in range units
            for e in airUnits[0]: #Unit objects with all interceptors and fighters
                  e_coord = e.getCoords()

                  for j in airUnits[1]: #Unit objects with all bombers #THERE IS OVERLAP CURRENTLY
                        j_coord = j.getCoords()

                        if (e != j) and (e.getStats()[2] != j.getStats()[2]): #if e is not the same unit as j and they are not on the same team
                              radius = e.getStats()[1][2] #get coordinates of interceptor/fighter
                              x1, y1 = e_coord[0], e_coord[1]
                              x2, y2 = j_coord[0], j_coord[1]

                              #check if j (air unit) is inside fighter/interceptor radius
                              if self.isInside(x1, y1, radius, x2, y2):
                                    #add defense check
                                    j.addDefCheck()

            #Carry out defense checks
            for j in airUnits[1]: #this list contains all the air units in combat
                  if j.getDefChecks() > 0:
                        stats = j.getStats()[1]
                        def_stat = stats[0]
                        for i in range(j.getDefChecks()):
                              rand = np.random.randint(0, 100)
                              if def_stat < rand:
                                    #print(str(def_stat) + " " + str(rand))
                                    j.die()

            #Carry out bombing runs
            for e in airUnits[2]: #e is a UNIT object
                  if e.isAlive(): #only check if unit is still alive
                        TEAM = e.getStats()[2]
                        stats = e.getStats()[1]
                        attk_stat = stats[1]
                        if attk_stat > np.random.randint(0,100):
                              unit_coord = e.getCoords()
                              if self.mapArray[unit_coord[0]][unit_coord[1]][0].isBattleSquare == True:
                                    pointsScored = stats[3]

                                    self.mapArray[unit_coord[0]][unit_coord[1]][0].addPoints(TEAM, pointsScored) #add points to grid Object (the battle square)
                                    
                                    if TEAM: #only total points, not points per battle square
                                          BLUFOR_points += pointsScored
                                    else:
                                          OPFOR_points += pointsScored
                              else:
                                    print(str(e.name) + " scored, but not on a battle square!")

            #TODO: do something with the dead units

            return [BLUFOR_points, OPFOR_points]
      
      def getUnits(self):
            coordIntFight = []
            coordBombers = []
            coordAll = [] #need to add more for other forces
            for x in self.mapArray:
                  for y in x:
                        gridObj = y[0]
                        if gridObj.hasUnits():
                              units = gridObj.getUnits()
                              for e in units:
                                    #format "NAME" [STATS] bool TEAM
                                    stats = e.getStats()
                                    if (stats[0] == "Interceptor") | (stats[0] == "Fighter"):
                                          coordIntFight.append(e) #add int, fighter
                                    else:
                                          coordBombers.append(e) #add bombers
                                    coordAll.append(e) #add all int, fight, and bomb

            return [coordIntFight, coordAll, coordBombers]

      def addUnit(self, name, coord, TEAM):
            #self.mapArray[1][1][0].addUnits("Interceptor", True)
            try:
                  self.mapArray[coord[0]][coord[1]][0].addUnits(name, TEAM)
            except Exception as e:
                  print(e)

      #standardize to one of these at some point
      def addUnitObj(self, UnitObj):
            coord = [UnitObj.x, UnitObj.y]
            try:
                  self.mapArray[coord[0]][coord[1]][0].addUnitObj(UnitObj)
            except Exception as e:
                  print(e)

      def setGridSquare(self, gridSquareObj):
            x = gridSquareObj.x
            y = gridSquareObj.y
            #setBattleStatus = gridSquareObj.getBattleStatus()
            #setBorderStatus = gridSquareObj.getBorderStatus()
            #self.mapArray[x][y][0].setBattleStatus(gridSquareObj)
            self.mapArray[x][y][0] = gridSquareObj