__author__ = "Kevin M. Karol, Ricardo Tucker"
__copyright__ = "Copyright 2016"
__license__ = "MIT"
__email__ = "kevinmkarol@gmail.com"

from time import time
from time import sleep
from random import randint

from button_interface import ButtonInterface
from server_interface import ServerInterface
from powerstrip_interface import PowerstripInterface

#constants
gameMode_normal = 0
gameMode_kids = 1

gameLengthSeconds = 64
timeDelay = 1
tutorialPoints = 5
buttonSyncTolerence = 0.5


blueChan = 11
greenChan = 12
redChan = 8
purpleChan = 13
silverChan = 10
orangeChan = 7
buttons = [blueChan, greenChan, redChan, purpleChan, silverChan, orangeChan]
kidButtons = [redChan, silverChan, orangeChan]

buttonBulbMap = {blueChan:   7,
                 greenChan:  6,
                 redChan:    1,
                 purpleChan: 2,
                 silverChan: 5,
                 orangeChan: 3,
                 }


class MainLoop():
    def __init__(self):
        global gameLengthSeconds, buttonBulbMap, gameMode_normal, timeDelay, buttons
        self.buttons = buttons

        self.listeningChannel1 = self.buttons[randint(0, len(buttonBulbMap) - 1)]
        self.listeningChannel2 = self.buttons[randint(0, len(buttonBulbMap) - 1)]
        while self.listeningChannel2 == self.listeningChannel1:
            self.listeningChannel2 = self.buttons[randint(0, len(buttonBulbMap) - 1)]
        print self.listeningChannel1
        self.score = -1
        self.gameActive = False
        self.gameMode = gameMode_normal

        #set up game parameters
        self.delayTimes = {}
        for chan in buttonBulbMap:
            self.delayTimes[chan] = time() + 1
        
        self.gameEndTime = time() + (gameLengthSeconds)        
        
        self.clearLights()


    #Start the buttons listening with async callbacks to button pressed,
    #and then keep the script running forever, and restart the game when it ends
    def initializeListeners(self):
        global buttonBulbMap
        bi = ButtonInterface()
        si = ServerInterface()
        bi.startListening(self, buttonBulbMap, self.buttonPressed)
        self.waitingForGameStart()

        while True:
            sleep(1)
            if self.gameActive and time() > self.gameEndTime:
                print("Game Over")
                self.clearLights()
                self.gameActive = False
                sleep(5)
                self.waitingForGameStart()

    #Turn on the two lights for the kids game and normal game as a visual cue to press buttons
    def waitingForGameStart(self):
        global buttonBulbMap, greenChan, silverChan

        #So we don't induce current switching
        self.gaurdAgainstSurge()
        
        pi = PowerstripInterface()
        pi.sendPowerStateMessage(buttonBulbMap[greenChan], "ON")
        pi.sendPowerStateMessage(buttonBulbMap[silverChan], "ON")

    #Playback an introductory light pattern of random flashing during the games' intro sequence
    def introLightPattern(self):
        global buttonBulbMap
        previousButtonChan = 0
        nextButtonChan = 0
        stopTime = time() + 13
        pi = PowerstripInterface()
        
        while time() < stopTime:
            while previousButtonChan == nextButtonChan:
              chanIndex = randint(0, len(buttonBulbMap) - 1)
              nextButtonChan = buttonBulbMap.keys()[chanIndex]
            pi.sendPowerStateMessage(buttonBulbMap[nextButtonChan], "ON")
            sleep(0.5)
            pi.sendPowerStateMessage(buttonBulbMap[nextButtonChan], "OFF")
            previousButtonChan = nextButtonChan
            
        sleep(2)



    #called when a button is pressed to a new game
    def startGame(self):
        global gameLengthSeconds
        self.gameEndTime = time() + (gameLengthSeconds)        
        self.score = 0
        
        self.clearLights()

        #Message the server to start audio/video and then playback the intro light pattern
        si = ServerInterface()
        si.startGame()
        self.introLightPattern()

        self.gameActive = True
        self.startNextRound()


    #Turn off all of the lights controlled by the powerstrip
    def clearLights(self):
        global buttonBulbMap
        
        #So we don't induce current switching
        self.gaurdAgainstSurge()
        
        pi = PowerstripInterface()
        for bulb in buttonBulbMap.values():
            pi.sendPowerStateMessage(bulb, "OFF")

    #Ensure the pi doesn't detect phantom button presses when power is turned on/off
    #by incrementing the ignore delay for all buttons
    def gaurdAgainstSurge(self):
        global buttonBulbMap
        for chan in buttonBulbMap:
            self.incrementDelayTime(chan)

    #Increment the time until the next time a button push will register 
    #to protect against phantom button presses
    def incrementDelayTime(self, channelNum):
        global timeDelay
        self.delayTimes[channelNum] = time() + timeDelay

    #Callback for when a button is pressed - asyncronous
    def buttonPressed(self, channel):
        global greenChan, silverChan, gameMode_normal, gameMode_kids, buttonSyncTolerence
        #print "Button press: " + str(channel)
        #print "Listen to: " + str(self.listeningChannel1) + " " + str(self.listeningChannel2)

        channelDelayTime = self.delayTimes[channel] 

        #Is this a phantom button press?
        if time() > channelDelayTime:
            #A game is already running
            if self.gameActive:

                #Listening for one button press
                if self.score < tutorialPoints or self.gameMode == gameMode_kids:
                    if channel == self.listeningChannel1:
                        self.incrementDelayTime(channel)
                        
                        self.updateScore()
                        self.startNextRound()

                #Listening on two channels for syncronized button presses
                else:
                    #buttonSyncTolerence for comparison
                    self.incrementDelayTime(channel)

                    #generic code for checking for both button presses regardless of current channel
                    delayTime1 = self.delayTimes[self.listeningChannel1]
                    delayTime2 = self.delayTimes[self.listeningChannel2]
                    timeDifference = abs(delayTime1 - delayTime2)

                    if timeDifference < buttonSyncTolerence:
                        self.updateScore()
                        self.startNextRound()

            #A game is not already running, which game is the user trying to start?        
            else:
                if channel == greenChan:
                    print("starting normal")
                    self.incrementDelayTime(channel)
                    
                    self.gameMode = gameMode_normal
                    self.startGame()

                elif channel == silverChan:
                    print ("starting kids")
                    self.incrementDelayTime(channel)
                    
                    self.gameMode = gameMode_kids
                    self.startGame()

    #Increment the score and notify the A/V server
    def updateScore(self):
        self.score += 1

        si = ServerInterface()
        si.sendScore(self.score)
        print("Score: " + str(self.score))

    #select which button is the next target
    def determineNextButton(self):
        global buttonBulbMap, gameMode_normal, gameMode_kids, redChan, silverChan, orangeChan, tutorialPoints, kidsButtons

        if self.gameMode == gameMode_normal:
            #Ensure that we don't re-activate the same buttons
            currentChan1 = self.listeningChannel1
            currentChan2 = self.listeningChannel2

            while self.listeningChannel1 == currentChan1:
                  #or self.listeningChannel1 == currentChan2:
                buttonIndex1 = randint(0, len(self.buttons) - 1)
                #print "Button Index: "+ str(buttonIndex)
                self.listeningChannel1 = self.buttons[buttonIndex1]
            
            #Select a second button if tutorial is complete
            if self.score >= tutorialPoints:
                buttonIndex2 = randint(0, len(self.buttons) - 1)
                self.listeningChannel2 = self.buttons[buttonIndex2]

                #Ensure that the same two buttons as the previous round are not selected
                while self.listeningChannel2 == self.listeningChannel1 \
                      or self.listeningChannel2 == currentChan1 \
                      or self.listeningChannel2 == currentChan2:
                    buttonIndex2 = randint(0, len(self.buttons) - 1)
                    self.listeningChannel2 = self.buttons[buttonIndex2]
        
        #Select from the kids button list (lower to the ground) instead
        elif self.gameMode == gameMode_kids:

            currentChan = self.listeningChannel1
            while currentChan == self.listeningChannel1:
                buttonIndex = randint(0, len(kidButtons) - 1)
                self.listeningChannel1 = kidButtons[buttonIndex]

        print "New Channel: " + str(self.listeningChannel1)

    #Start the next round of the game by powering off the old lights,
    #selecting new buttons, and turning on the new lights
    def startNextRound(self):
        global buttonBulbMap, gameMode_normal
        pi = PowerstripInterface()
        bulb1 = buttonBulbMap[self.listeningChannel1]

        self.gaurdAgainstSurge()
        pi.sendPowerStateMessage(bulb1, "OFF")
        
        if self.score >= tutorialPoints and self.gameMode == gameMode_normal:
            bulb2 = buttonBulbMap[self.listeningChannel2]
            pi.sendPowerStateMessage(bulb2, "OFF")
    
        self.determineNextButton()
        bulb = buttonBulbMap[self.listeningChannel1]
        pi.sendPowerStateMessage(bulb, "ON")

        if self.score >= tutorialPoints and self.gameMode == gameMode_normal:
            bulb2 = buttonBulbMap[self.listeningChannel2]
            pi.sendPowerStateMessage(bulb2, "ON")

game = MainLoop()
game.initializeListeners()
