import numpy as np
import pygame, threading, socket, pickle
from pygame.locals import *
import pygame_textinput
from Unit import Unit
from gridSquare import gridSquare
import select
import queue
from gameMap import gameMap
import sys
from dataToSend import dataToSend

#Initialize the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "127.0.0.1" #or localhost
PORT = 5050
client.connect((HOST, PORT))

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
GRID_BLUE = (13,80,189)
RED = (255, 45, 45)
GREEN = (0, 255, 0)

display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

data_queue = queue.Queue()

#Unit type object - moved to seperate file

#Object to track what's in each grid square - moved to seperate file

#should only be one - object for the game map & contains battle calculations

#Create Map object (1)
#mainMap = gameMap(50) #USE FOR 12 x 12 GRID
#initalize empty game map, client side stored
mainMap = gameMap(20, MAP_WIDTH)

def drawGrid(game_map): #game_map is gameMap obj
      #blockSize = 20 #Set the size of the grid block - former, no self reference
      for idx, x in enumerate(range(0, MAP_WIDTH, game_map.blockSize)):
            #print(idx)
            for idy, y in enumerate(range(0, MAP_WIDTH, game_map.blockSize)):
                  #print(idy)
                  rect = pygame.Rect(x, y, game_map.blockSize, game_map.blockSize)
                  currentGridObj = game_map.mapArray[idx][idy][0]
                  #draw border squares first
                  if currentGridObj.isBorderSquare == True:
                        if currentGridObj.TEAM:
                              pygame.draw.rect(display, GRID_BLUE, rect)
                        else:
                              pygame.draw.rect(display, RED, rect)

                  #draw in battle squares next
                  if currentGridObj.isBattleSquare == True: #0 is to get thing from list size of 1 this language sucks
                        pygame.draw.rect(display, GREEN, rect, game_map.blockSize, game_map.blockSize) #makes a circle 

                  #draw in units
                  if currentGridObj.hasUnits():
                        #unitList = currentGridObj.getUnits().sort(key=lambda a: a.TEAM)

                        #Sort so OPFOR units come first, done to fix bug where red circle drawn on top of blue circle
                        units = currentGridObj.getUnits()
                        OPFORunits, BLUFORunits = [], []
                        for e in units:
                              if e.TEAM:
                                    BLUFORunits.append(e)
                              else:
                                    OPFORunits.append(e)
                        unitList = OPFORunits + BLUFORunits

                        #set offset so circle appears in the middle of the grid square
                        offset = game_map.blockSize/2

                        #this could be so much better
                        hasDrawnOPFOR, hasDrawnBLUFOR = False, False
                        for e in unitList:
                              if hasDrawnOPFOR and hasDrawnBLUFOR: #only draw each once
                                    break
                              if not e.TEAM: #draw larger OPFOR circle first
                                    pygame.draw.circle(display, RED, [x+offset, y+offset], 8)
                                    hasDrawnOPFOR = True
                              else:
                                    pygame.draw.circle(display, BLUE, [x+offset, y+offset], 5)

                  #draw in all other gridObjects (white borders)
                  else:
                        pygame.draw.rect(display, WHITE, rect, 1)

                  #print(self.mapArray[idx][idy][0].getCoord())

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

      drawGrid(mainMap)
      
      pygame.display.update()
      clock.tick(60)

#https://stackoverflow.com/questions/20289981/python-sockets-stop-recv-from-hanging
def data_receiver():
      while True: #very important to loop here
            #add clause to close thread on server disconnect to stop the tons of errors on server shutdown
            #Assuming self.sock exists
            data = client.recv(8192)
            try: #check for pickle
                  unpickled_data = pickle.loads(data)

                  if isinstance(unpickled_data, dataToSend): #check if pickle is a dataToSent object
                        for e in unpickled_data.getGridSquares(): #get grid square objects
                              mainMap.setGridSquare(e) #set client copy of map to objects
                        for e in unpickled_data.getUnits():
                              mainMap.addUnitObj(e)

            #try decoding in text
            except Exception as e:
                  #print(str(e) + " Exception! in data_receiver()")
                  try:
                        decoded_data = data.decode()
                        #print("DATA: ")
                        print(decoded_data)
                        data_queue.put(decoded_data)
                  except Exception as e:
                        print(str(e) + "Exception! in nested exception in data_reciever()")

         #edit the data in any way necessary here

#this thread listenes for data from the server to not clog main thread with .recv
#daemon causes the thread to die when the main thread does
#without daemon thread (& program) continues running after window close
data_receiver = threading.Thread(target=data_receiver, daemon = True) 
data_receiver.start()

#main update loop
MAX_UDP_SIZE = 65507  # https://en.wikipedia.org/wiki/User_Datagram_Protocol
while True:
      draw_game_window() #all drawing happens here

      try:
            data = data_queue.get_nowait()
            #do something with data
            #print(data)
      except queue.Empty:
            pass
      
      events = pygame.event.get()

      textinput.update(events)
      #print(textinput.value)

      #bogus code to run server in continuous loop
      #client.send(bytes(("client OK!").encode()))
      
      for event in events:
            
            if event.type == pygame.QUIT:
                  print("QUIT NOW")
                  pygame.display.quit()
                  pygame.QUIT
                  quit()
 
            #evaluate keyboard input and update units
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                  dataSent = dataToSend() #initialize data to send object
                  capturedInput = textinput.value
                  #Expected input 'Name, number, x, y, TEAM'
                  try:
                        capturedInput = capturedInput.split(',') #split into array
                        unitName = capturedInput[0] #expect one within Unit Dict
                        numUnits = int(capturedInput[1]) #expect integer
                        xCoord = int(capturedInput[2]) #expect integer
                        yCoord = int(capturedInput[3]) #expect integer
                        inputTEAM = capturedInput[4] #expect either T or F
                  except Exception as e:
                        print(e)
                  for i in range(numUnits):
                        if inputTEAM == "T":
                              mainMap.addUnit(unitName, [xCoord, yCoord], True) #jank af
                              print(unitName + " added!")
                              try:
                                    addUnit = Unit(unitName, True, xCoord, yCoord)
                                    dataSent.addUnit(addUnit, True) #add unit to data to send object
                              except Exception as e:
                                    print(e)

                        elif inputTEAM == "F":
                              mainMap.addUnit(unitName, [xCoord, yCoord], False)
                              print(unitName + " added!")

                              try:
                                    addUnit = Unit(unitName, False, yCoord, yCoord)
                                    dataSent.addUnit(addUnit, False) #add unit to data to send object
                              except Exception as e:
                                    print(e)
                        else:
                              print("fuck")

                  #prepare data package to send
                  data = pickle.dumps(dataSent)
                  #print(str(len(data)) + " data length")
                  if len(data) > MAX_UDP_SIZE:
                        raise ValueError('Message too large')
                  client.send(data)
                  
                  #recalculate battle odds
                  #mainMap.calcBattle() --> MOVE TO Server side


