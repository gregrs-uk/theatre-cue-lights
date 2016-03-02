Arduino/wxPython theatrical cue light system
============================================

Background
----------

This repository contains a Fritzing breadboard layout and schematic together with Arduino and Python code for a theatrical cue-light system. The Python code requires the wxPython (GUI) and pySerial (serial communication) libraries to be installed. It has been tested on Mac and Linux under Python 2.7 using an OrangePip Kona328 (Arduino UNO copy).

Purpose
-------

The system allows a theatrical stage manager to give visual cues to, for example, lighting and sound operators and stage crew using a computer-based GUI. The Arduino UNO can send/receive signals from up to six remote circuits. Each line of communication between the Arduino and a single remote circuit is known as a 'channel'.

Connection
----------

The Arduino both communicates with the computer and is powered via USB. By default, the remote circuits connect to the Arduino UNO as follows, although this can be changed in the Arduino sketch.

* Channel 1: pins 2, 3, 4
* Channel 2: pins 5, 6, 7
* Channel 3: pins 8, 9, 10
* Channel 4: pins 11, 12, 13
* Channel 5: pins A0, A1, A2
* Channel 6: pins A3, A4, A5

Circuit
-------

The remote circuits rely on the tri-state nature of Arduino pins in order to control two LEDs and receive input from a switch over three-core cable. This should allow the use of XLR cable, although the circuit has only been tested on a breadboard so far. The Fritzing file shows the circuit for a single remote circuit connected to channel 1 (pins 2, 3 and 4). The parts used for each remote circuit are as follows:

* Red LED
* Green LED
* Momentary push switch
* 2x 330 ohm resistors
* 1x 10k ohm resistor
* Diode

Setup
-----

The serial port used to communicate with the Arduino should be set using the 'device' variable near the top of the Python file (gui.py). This can be found at the bottom of the window in the Arduino IDE.

Usage
-----

The intended usage is as follows.

First, the stage manager sends a 'standby' cue to a remote, causing its red LED to flash. The remote operator confirms their readiness by pressing their button, causing the red LED to be lit steadily and a 'ready' cue to be sent back to the computer. The stage manager then sends a 'go' cue and the green LED is lit instead. The channel can be reset (i.e. both LEDs switched off) from the GUI or by pressing the remote button after a 'go' cue.

Whenever the Arduino receives the new status for a channel (standby, ready, go or reset), it confirms this by sending an update back to the GUI. The status of each channel is then shown at the top of the GUI.

Development
-----------

The hardware aspect has not been fully developed. Ideally a shield would connect the Arduino to several XLR sockets to form a base station connected to the computer. Each remote circuit would have an XLR socket, allowing up to 6 remote circuits to be connected to the Arduino by XLR cable.

Licence
-------

The circuit contained in the Fritzing file is licenced under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Licence](http://creativecommons.org/licenses/by-nc-sa/4.0/). The Python and Arduino code is licenced under the GNU GPL V3 contained in the LICENCE_CODE file. Please feel free to use/adapt the circuit and code for non-commercial uses (including use in amateur/school theatres) but please share your work and provide a link back to this repository. If you've used the circuit and/or code or made any improvements, I'd love to hear from you.
