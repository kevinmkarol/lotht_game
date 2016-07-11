__author__ = 'Kevin M. Karol'
__copyright__ = "Copyright 2016"
__license__ = "MIT"
__email__ = "kevinmkarol@gmail.com"

from OSC import OSCClient, OSCMessage

class ServerInterface():
    def __init__(self):
        self.serverIP = "SERVER.IP.GOES.HERE"
        self.serverPort = 2016

    def messageServer(self, messagePath, argument):
        client = OSCClient()
        client.connect((self.serverIP, self.serverPort))
        message = OSCMessage(messagePath)
        message.append(argument)

        client.send(message)

    def sendScore(self, score):
        self.messageServer("/score", score)

    def startGame(self):
        self.messageServer("/game/start", 1)
