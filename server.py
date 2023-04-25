import socket, threading, random, time, pickle
from Unit import Unit

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "127.0.0.1" #or localhost
PORT = 5050
server.bind((HOST, PORT))

x = 50

has_first_player_connected = False

player_1 = None
player_2 = None

players = []

class dataToSend(object):

      def __init__(self):
            self.units = []

      def addUnit(self, name, coord, TEAM):
            try:
                  x, y = coord[0], coord[1]
                  self.units.append(Unit(name, TEAM, x, y))
            except Exception as e:
                  print(e)

def handle_client(conn, addr, x):
      global has_first_player_connected
      print(f"Client connected on {conn}")
      connected = True

      if has_first_player_connected == False:
            #This code will run if this is the first player connecting
            #To the server
            conn.send(bytes("You Are Player 1".encode()))
            
            has_first_player_connected = True

            players.append(conn)

            is_player_1 = True
      else:
            #Player 2
            conn.send(bytes("You Are Player 2".encode()))

            players.append(conn)

            is_player_1 = False
            
      time.sleep(1)
      
      UDP_MAX = 2 ** 16 - 1
      while connected:

            data = conn.recv(UDP_MAX)

            #print(data)
            unpickled_data = pickle.loads(data)
            print(unpickled_data)

            """
            for i in range(len(players)):
                  try:
                        for j in range(len(players)):
                              if i != j:
                                    players[j].send(bytes(data))
                  except Exception as e:
                        print("hiasdf")
                        print(e)
                        pass
            """

            if is_player_1:
                  try:
                        players[1].send(bytes(data))
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
