import numpy as np
import pygame, threading, socket
from pygame.locals import *
import pygame_textinput

#Initialize the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5050))

#Initialize pygame
pygame.init()
pygame.font.init()
#print(pygame.font.get_fonts())
arial = pygame.font.SysFont('arial', 15)

#for entire window
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
#for game map
MAP_WIDTH = 600
MAP_HEIGHT = 600

#initialize colors
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
BLUE = (45, 103, 255)
RED = (255, 45, 45)
GREEN = (0, 255, 0)

display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

#Unit type object
class Unit(object):

      def __init__(self, name, TEAM, x, y):
            self.name = name
            self.TEAM = TEAM #TRUE is BLUFOR. FALSE is OPFOR.
            self.x = x
            self.y = y

            self.alive = True
            self.defChecks = 0

            #format [Defense Stat, Offense Stat (999 for N/A), Range]
            classDict = {
                  "Interceptor" : [30, 999, 6],
                  "Fighter" : [60, 999, 3],
                  "Multirole-B" : [60, 70, 0, 1],
                  "Multirole-F" : [60, 70, 3],
                  "CAS" : [40, 70, 0],
                  "Stealth-B" : [80, 70, 0, 2],
                  "Gunship" : [20, 100, 0, 2],
                  "SEAD" : [80, 80, 6],
                  "SR" : [0, 100, 3],
                  "SAM" : [0, 999, 2]
            }

            try:
                  self.myStats = classDict[self.name]
                  print(self.myStats)
            except Exception as e:
                  print(e)

      def getStats(self):
            return [self.name, self.myStats, self.TEAM]
      
      def getCoords(self):
            return [self.x, self.y]
      
      def getDefChecks(self):
            return self.defChecks
      
      def isAlive(self):
            return self.alive
      
      def addDefCheck(self):
            self.defChecks += 1
            print(self.name + " currently has " + str(self.defChecks) + " defense checks.")

      def die(self):
            self.alive = False
            print(self.name + " died!")

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

#should only be one - object for the game map & contains battle calculations
class gameMap(object):

      def __init__(self, blockSize):
            self.numBlocks = int(MAP_WIDTH / blockSize)
            #print(self.numBlocks)
            self.blockSize = blockSize #change size of map with either blocksize or windowsize
            self.mapArray = np.array([ [[gridSquare(True, False, False, [], i, j),] for j in range(self.numBlocks)] for i in range(self.numBlocks) ])

            #test units
            self.mapArray[1][1][0].addUnits("Interceptor", True)
            self.mapArray[1][2][0].addUnits("Interceptor", False)
            self.mapArray[1][2][0].addUnits("Interceptor", True)

            self.mapArray[3][15][0].addUnits("Interceptor", False)
            self.mapArray[3][17][0].addUnits("Gunship", True)

            self.mapArray[15][2][0].addUnits("Interceptor", False)
            self.mapArray[20][2][0].addUnits("Fighter", False)
            self.mapArray[17][2][0].addUnits("Gunship", True)

            battleSquares = 3 #set number of battle squares
            xCoordBoarder = int(self.numBlocks/2) #set x coordinate of boarder, just in the middle right now
            randBattleCities = np.random.randint(0, len(self.mapArray[xCoordBoarder][:]), battleSquares).tolist() #sometimes only generates 2 for some reason, good bug

            #add spacing of 1 between battle cities - doesn't work lmao
            while 1 in np.diff(randBattleCities):
                  randBattleCities = np.random.randint(0, len(self.mapArray[xCoordBoarder][:]), battleSquares).tolist()

            #set gridObj values: boarder cities & set 3 random cities to battle squares
            for id, e in enumerate(self.mapArray[xCoordBoarder][:]): #select column at boarder x coordinate
                  gridObj = e[0] #select grid square
                  if id in randBattleCities:
                        gridObj.isBattleSquare = True #set battle squares
                  gridObj.isBoarderSquare = True

            self.calcBattle()

      def drawGrid(self):
            #blockSize = 20 #Set the size of the grid block - former, no self reference
            for idx, x in enumerate(range(0, MAP_WIDTH, self.blockSize)):
                  #print(idx)
                  for idy, y in enumerate(range(0, MAP_WIDTH, self.blockSize)):
                        #print(idy)
                        rect = pygame.Rect(x, y, self.blockSize, self.blockSize)
                        currentGridObj = self.mapArray[idx][idy][0]
                        #draw boarder squares first
                        if currentGridObj.isBoarderSquare == True:
                              if currentGridObj.TEAM:
                                    pygame.draw.rect(display, BLUE, rect)
                              else:
                                    pygame.draw.rect(display, RED, rect)

                        #draw in battle squares next
                        if currentGridObj.isBattleSquare == True: #0 is to get thing from list size of 1 this language sucks
                              pygame.draw.rect(display, GREEN, rect, self.blockSize, self.blockSize) #makes a circle 

                        #draw in units
                        if currentGridObj.hasUnits():
                              unitList = currentGridObj.getUnits()
                              hasDrawnOPFOR = False
                              offset = self.blockSize/2
                              for e in unitList:
                                    if not e.TEAM and not hasDrawnOPFOR: #draw larger OPFOR circle first, and only draw once
                                          pygame.draw.circle(display, RED, [x+offset, y+offset], 8)
                                          hasDrawnOPFOR = True
                                    else:
                                          pygame.draw.circle(display, BLUE, [x+offset, y+offset], 5)

                        #draw in everything else
                        else:
                              pygame.draw.rect(display, WHITE, rect, 1)

                        #print(self.mapArray[idx][idy][0].getCoord())
      
      #stolen from https://www.geeksforgeeks.org/find-if-a-point-lies-inside-or-on-circle/
      def isInside(self, circle_x, circle_y, rad, x, y):
            # Compare radius of circle
            # with distance of its center
            # from given point
            if ((x - circle_x) * (x - circle_x) +
                  (y - circle_y) * (y - circle_y) <= rad * rad):
                  return True
            else:
                  return False

      #TODO: move to server side
      def calcBattle(self):
            airUnits = self.getUnits() #returns Unit objects

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
            for e in airUnits[2]:
                  if e.isAlive(): #only check if unit is still alive
                        TEAM = e.getStats()[2]
                        stats = e.getStats()[1]
                        attk_stat = stats[1]
                        if attk_stat > np.random.randint(0,100):
                              unit_coord = e.getCoords()
                              if self.mapArray[unit_coord[0]][unit_coord[1]][0].isBattleSquare == True:
                                    self.mapArray[unit_coord[0]][unit_coord[1]][0].addPoints(TEAM, stats[3]) #add points to grid Object
                              else:
                                    print(str(e.name) + " scored, but not on a battle square!")

            #TODO: do something with the dead units
      
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

      def search(self, coord):
            #create array to search
            searchRadius = 6
            xSearchCoords = range(coord[0]-6,coord[0]+6)
            ySearchCoords = range(coord[1]-6,coord[1]+6)
            searchCoords = [range()]

      def addUnit(self, name, coord, TEAM):
            #self.mapArray[1][1][0].addUnits("Interceptor", True)
            try:
                  self.mapArray[coord[0]][coord[1]][0].addUnits(name, TEAM)
            except Exception as e:
                  print(e)

#Create Map object (1)
#mainMap = gameMap(50) #USE FOR 12 x 12 GRID
mainMap = gameMap(20)

#initialize text input object - reference https://github.com/Nearoo/pygame-text-input
textinput = pygame_textinput.TextInputVisualizer(font_object=arial, font_color=[255, 255, 255])

#all graphics in this function
def draw_game_window():
      display.fill((0,0,0))

      #set text input fields
      bomber_text = arial.render('Name,number,x,y,TEAM(T/F)', False, (200, 120, 200))

      display.blit(bomber_text, (625,50))
      display.blit(textinput.surface, (625, 75))

      #Later can add clause to only call this once other client has connected
      #data = client.recv(6000).decode()
      #line = data

      try:
          #pygame.draw.rect(display, GREEN, (float(line.split(",")[0]), float(line.split(",")[1]), 50, 50))
          kajshgdf=1
      except Exception as e:
          print(e)

      mainMap.drawGrid()
      
      pygame.display.update()
      clock.tick(60)

#main update loop
while True:
      draw_game_window() #all drawing happens here

      #client.send((bytes(str("hello!").encode())))
      
      events = pygame.event.get()

      textinput.update(events)
      #print(textinput.value)
      
      for event in events:
            
            if event.type == pygame.QUIT:
                  pygame.display.quit()
                  pygame.QUIT
                  quit()

            #evaluate keyboard input and update units
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                  capturedInput = textinput.value
                  #Expected input 'Name, number, x, y, TEAM'
                  try:
                        capturedInput = capturedInput.split(',') #split into array
                  except Exception as e:
                        print(e)
                  for i in range(int(capturedInput[1])):
                        print(capturedInput[4])
                        if capturedInput[4] == "T":
                              mainMap.addUnit(capturedInput[0], [int(capturedInput[2]), int(capturedInput[3])], True)
                              print(capturedInput[0] + " added!")
                        elif capturedInput[4] == "F":
                              mainMap.addUnit(capturedInput[0], [int(capturedInput[2]), int(capturedInput[3])], False)
                              print(capturedInput[0] + " added!")
                        else:
                              print("fuck")
                  
                  #recalculate battle odds
                  mainMap.calcBattle()


