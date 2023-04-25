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