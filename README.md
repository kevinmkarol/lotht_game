# Legends of the Hidden Temple Game: Source Code

This repository contains the source code that ran the Legends of the Hidden Temple installation game.  There are three main components:

1. pi_code: This folder contains the python code that managed Button GPIO, messaging the ethernet controlled power strip, and communicating with the main server
2. max_folder: This folder contains a max patch and assets that controlled the live video, OSC messaging for the lightying system, score tracking and audio playback.
3. game_lights.qxw: This is a QLC+ file which contains the lighting ques for the game.  Since the full show feature crashed regularly in the realese this installation was built using, the lights were instead controlled using OSC messaging and a control panel.  In this way, each cue played back independently as sequenced and timed by the central server.

The resulting installation can be viewed on youtube as both a <a href="https://youtu.be/w1DpMpn2OCI">trailer</a> and <a href="https://youtu.be/puwgY1SeGvM">360 video experience.</a>  Full project documentation is available on <a href="kevinmkarol.com">my website.</a>


### License
This code is provided under the MIT License.