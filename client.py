import numpy as np
import pygame, threading, socket
from pygame.locals import *

#Initialize the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5050))

#Initialize pygame
pygame.init()

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
BLUE = (45, 103, 255)
RED = (255, 45, 45)

display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

#Constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Player(object):
      def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.jumping = False
            self.jump_count = 10
            self.bottom = False
            self.top = False
            self.right = False
            self.left = False

      def draw(self):
            pygame.draw.rect(display, RED, (self.x, self.y, self.width, self.height))

            #self.move()

player = Player(560, 550, 50, 50)

class gridSquare(object):
      def __init__(self, TEAM, isBattleSquare, isBoarderSquare, currentUnits):
            self.TEAM = TEAM #BLUFOR is TRUE. OPFOR is FALSE.
            self.isBattleSquare = isBattleSquare #t/f
            self.isBoarderSquare = isBoarderSquare
            self.currentUnits = currentUnits #array of current units present

      def getBattleStatus(self):
            return self.isBattleSquare

class Map(object):

      def __init__(self, blockSize):
            self.numBlocks = int(WINDOW_WIDTH / blockSize)
            print(self.numBlocks)
            self.blockSize = blockSize #change size of map with either blocksize or windowsize
            self.mapArray = np.array([ [[gridSquare(True, False, False, 0)] for j in range(self.numBlocks)] for i in range(self.numBlocks) ])
            #self.mapArray = [ [[gridSquare(False, 0)] for j in range(30)] for i in range(30) ] #30 works

            #set battle cities
            self.mapArray[1][1][0].isBattleSquare = True
            self.mapArray[1][2][0].isBattleSquare = True
            #self.mapArray[15][:,15].isBoarderSquare = True

            print(len(self.mapArray[0]))
            print(self.mapArray[1][1][0].getBattleStatus())

      def drawGrid(self):
            #blockSize = 20 #Set the size of the grid block - former, no self reference
            #create map array later
            #for idx, x in enumerate(range(0, WINDOW_WIDTH, self.blockSize)):
            for idx, x in enumerate(range(0, WINDOW_WIDTH, self.blockSize)):
                  #print(idx)
                  for idy, y in enumerate(range(0, WINDOW_WIDTH, self.blockSize)):
                        #print(idy)
                        rect = pygame.Rect(x, y, self.blockSize, self.blockSize)
                        if self.mapArray[idx][idy][0].isBattleSquare == False: #0 is to get thing from list size of 1 this language sucks
                              #print(str(idx) + " " + str(idy))
                              pygame.draw.rect(display, WHITE, rect, 1)
                        else:
                              pygame.draw.rect(display, GREEN, rect, self.blockSize, self.blockSize) #makes a circle
                        if self.mapArray[idx][idy][0].isBoarderSquare == True:
                              if self.mapArray[idx][idy][0].TEAM:
                                    pygame.draw.rect(display, BLUE, rect)
                              else:
                                    pygame.draw.rect(display, RED, rect)

                        

map = Map(20)

def draw_game_window():
      #All code for drawing objects to the screen
      display.fill((0,0,0))

      #Later can add clause to only call this once other client has connected
      data = client.recv(6000).decode()
      line = data

      try:
          pygame.draw.rect(display, GREEN, (float(line.split(",")[0]), float(line.split(",")[1]), 50, 50))
      except Exception as e:
          print(e)

      map.drawGrid()
      #player.draw()

      
      pygame.display.update()
      clock.tick(60)

while True:
      #Main Loop

      draw_game_window()
      
      for event in pygame.event.get():
            if event == pygame.QUIT:
                  pygame.QUIT
                  quit()


