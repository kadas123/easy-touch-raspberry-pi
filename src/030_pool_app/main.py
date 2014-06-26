#!/usr/bin/python

import serialThread
import httpThread
import time
import sys
import circuit
import controller
import logging

# set up circuits
# I just guessed at circuit number; it is really a label tied to byte/bit
# byte 1 is equipment byte 1 in status message,
# byte 2 is equipment byte 2 in status message
circuits = {	
		1 : { 'name' : 'spa', 'byte' : 1, 'bit' : 0 },
		2 : { 'name' : 'pool pump', 'byte' : 1, 'bit' : 5 },
		3 : { 'name' : 'jets 1', 'byte' : 1, 'bit' : 1 },
		4 : { 'name' : 'jets 2', 'byte' : 1, 'bit' : 2 },
		5 : { 'name' : 'spillway', 'byte' : 1, 'bit' : 3 },
		6 : { 'name' : 'waterfall', 'byte' : 1, 'bit' : 4 },
		7 : { 'name' : 'slide', 'byte' : 1, 'bit' : 6 },
		8 : { 'name' : 'pool light', 'byte' : 1, 'bit' : 7 },
		9 : { 'name' : 'spa light', 'byte' : 2, 'bit' : 0 },
	}

circuitlist=[]
for k in circuits.keys():
	circuitlist.append( circuit.circuit( 	k,
						circuits[k]['name'],
						circuits[k]['byte'],
						circuits[k]['bit'],
						0
						))


# switch to DEBUG for packet level byte data (but then that writes to the SD
# card so do not keep it there in normal operation

logging.basicConfig( filename='main.log', level=logging.INFO)

# pass the circuits to the serial thread for decoding and stuffing
# in the redis database
controller = controller.controller( circuitlist )
#controller.save()
serialT = serialThread.serialThread( '/dev/ttyAMA0', controller, 2)
cmdT = serialThread.cmdThread()
httpT = httpThread.httpThread(1,2)

serialT.start()
httpT.start()
cmdT.start()

bExit = False
print "Type CTRL-z to background, then kill the job to exit. This is usually 'kill %1'"

while not bExit:
	try: 
		line = sys.stdin.readline().strip()

		if line[0:4] == "exit":
			bExit = True

	except:
		bExit=True
	
	if line:	
		print line

	time.sleep(1)

# clean up and stop threads
serialT.stop()
cmdT.stop()
httpT.stop()
serialT.join()
cmdT.join()
httpT.join()

print "Exiting main"
