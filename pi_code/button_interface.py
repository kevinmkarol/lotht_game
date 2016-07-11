__author__ = 'Kevin M. Karol'
__copyright__ = "Copyright 2016"
__license__ = "MIT"
__email__ = "kevinmkarol@gmail.com"


import RPi.GPIO as GPIO

class ButtonInterface():
    def __init__(self):
        global gameLengthSeconds
        GPIO.setmode(GPIO.BOARD)

    #starts the buttons listening for asyncronous callbacks of the button being pressed
    def startListening(self, mainLoop, channels, callback):
        print(channels)
        for channelNum in channels:
            GPIO.setup(channelNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(channelNum, GPIO.RISING, callback)

    ######
    ##Utility functions
    ######

    def logButtonChannel(self, channel):
        print("log: " + str(channel))

    def util_button_log(self, channels):
        for channelNum, __ in channels:
            GPIO.add_event_detect(channels[channelNum], GPIO.RISING, self.logButtonChannel)
