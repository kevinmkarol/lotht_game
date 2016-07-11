__author__ = 'Kevin M. Karol'
__copyright__ = "Copyright 2016"
__license__ = "MIT"
__email__ = "kevinmkarol@gmail.com"

import pycurl
from StringIO import StringIO

class PowerstripInterface():
    def __init__(self):
        self.username = "admin"
        self.password = "password"
        self.ip = "192.168.0.100"

    def constructPowerStripMessage(self, username, password, ipAddress, outletNumber, powerState):
      string = username + ":" + password + "@" + ipAddress + "/outlet?" + str(outletNumber) + "=" + powerState;
      return string

    def sendPowerStateMessage(self, outletNumber, powerState):
        message = self.constructPowerStripMessage(self.username, self.password, self.ip, outletNumber, powerState)
        self.sendMessage(message)

    def sendMessage(self, message):
      buffer = StringIO()
      c = pycurl.Curl()
      c.setopt(c.URL, message)
      c.setopt(c.WRITEDATA, buffer) #just for debugging
      c.perform()
      c.close()
