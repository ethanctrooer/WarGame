import socket, threading, random, time, pickle
from Unit import Unit
from datetime import datetime
from dataToSend import dataToSend
from gameMap import gameMap
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

#listening & sending thread, unique to each connection
def handle_client(conn, addr, x):
      global has_first_player_connected
      print(f"Client connected on {conn}")
      connected = True

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
            data = conn.recv(UDP_MAX) #each data packet from one user

            #print(data)
            unpickled_data = pickle.loads(data)
            print(unpickled_data)

            currenttime = str(datetime.now().strftime("%H:%M:%S"))

            conn.send(bytes(("message recieved OK!").encode()))

            if is_player_1:
                  try:
                        players[1].send(bytes(data)) #send player 1's [0] data straight to player 2 [1]
                        #players[0].send(bytes(currenttime))
                  except:
                        pass

            if not is_player_1:
                  try:
                        players[0].send(bytes(data))
                  except:
                        pass
            

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
