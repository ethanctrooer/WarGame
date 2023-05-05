import socket, threading, random, time, pickle, select
from Unit import Unit
from datetime import datetime
from dataToSend import dataToSend
from gameMap import gameMap
import queue
import copy
#note: Unit.py is required for many of the custom objects, poor coding style

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "127.0.0.1" #or localhost
PORT = 5050
server.bind((HOST, PORT))

x = 50

has_first_player_connected = False

player_1 = None
player_2 = None

players = []

MAP_WIDTH = 600
masterMap = gameMap(20, MAP_WIDTH)

#initialize queue to share data between threads
q = queue.Queue(maxsize = 2)

### Create initial borders & battles, prep package for transport to client on initial connection
battleCitiesAndBorders = masterMap.makeBattlesAndBorders(3)

initial_packet_obj = dataToSend()
for e in battleCitiesAndBorders:
      initial_packet_obj.addGridSquare(copy.deepcopy(e)) #make deepcopy for sending so as to not just pass references

MAX_PAKCET_SIZE = 8192
initial_packet = pickle.dumps(initial_packet_obj)
if len(initial_packet) > MAX_PAKCET_SIZE:
      print(len(initial_packet))
      raise ValueError('Message too large')
### -----------

### END INIT 

#listening & sending thread, unique to each connection
def handle_client(conn, addr, x):
      global has_first_player_connected
      print(f"Client connected on {conn}")
      connected = True
      conn.setblocking(0) #https://stackoverflow.com/questions/9844263/a-non-blocking-socket-operation-could-not-be-completed-immediately-on-send good read
      #conn.send(bytes(("Connected").encode()))
      
      #Client ONLY expects pickled objects (add protection later).
      conn.send(initial_packet)

      if has_first_player_connected == False:
            #This code will run if this is the first player connecting
            #conn.send(bytes("You Are Player 1".encode())) 
            #for some reason this breaks the code, might have some attribution to the if loop
            
            has_first_player_connected = True

            players.append(conn)

            is_player_1 = True

      else:
            #Player 2
            #conn.send(bytes("You Are Player 2".encode()))

            players.append(conn)

            is_player_1 = False
      
      time.sleep(1)
      
      UDP_MAX = 2 ** 16 - 1
      while connected:

            #this is a waiting call, will freeze thread until call recieved
            timeout = 10 #move outside while loop
            readable, writable, exceptional = select.select([conn], [], [], timeout)
            if readable:
                  data = conn.recv(UDP_MAX) #each data packet from onemakeBattleCities user
                  #data packet CONTAINS: dataToSend obj, has ORDERS of where to ADD UNITS
                  time.sleep(0.5) #terrible terrible terrible

                  #print(data)
                  unpickled_data = pickle.loads(data)
                  print(unpickled_data)

                  try:
                        q.put_nowait(unpickled_data)
                        print(str(q.qsize()) + " queue length")
                        if q.full():
                              #ref https://stackoverflow.com/questions/16686292/how-to-get-the-items-in-queue-without-removing-the-items
                              if q.queue[0].TEAM != q.queue[1].TEAM: #from my understanding, this is dangerous but meh 
                                    #call map write
                                    for i in range(q.qsize()):
                                          unpickled_data_sent = q.get()
                                          for e in unpickled_data_sent.units:
                                                masterMap.addUnitObj(e)

                                    #call map calcualtion
                                    #returned as [Blufor points, Opfor points]
                                    print("Calculating...")
                                    points = masterMap.calcBattle() #only total points, not points per battle square
                                    print("Calculations Complete!")
                                    BLUFOR_poiints = points[0]
                                    OPFOR_points = points[1]

                                    #TODO: keep track of points or update map based on points
                              for e in players:
                                    e.send(bytes((("BLUFOR scored " + str(BLUFOR_poiints) + " points, and OPFOR scored " + str(OPFOR_points) + " points")).encode()))

                              #something something queue lock
                              #q.clear()

                  except Exception as e:
                        print("Queue already full! (Probably) Details:")
                        print(e)
                  
                  #conn.send(bytes(("message recieved OK!").encode()))
                  conn.send(bytes(("return_packet").encode()))

            #make new thread to listen for events and join it to another one clog here
            #print("timeout")

      print(f"Client at {addr} has disconnected")
      conn.close()

def listen():
      server.listen()
      while True:
            conn, addr = server.accept()

            thread = threading.Thread(target = handle_client, args = (conn, addr, x))
            thread.start()

print("SERVER STARTING...")
listen()
