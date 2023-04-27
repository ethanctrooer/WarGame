from Unit import Unit

class dataToSend(object):

      def __init__(self):
            self.units = []

      def addUnit(self, name, coord, TEAM):
            try:
                  x, y = coord[0], coord[1]
                  self.units.append(Unit(name, TEAM, x, y))
            except Exception as e:
                  print(e)