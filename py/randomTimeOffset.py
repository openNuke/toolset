################

"""
	sb_randomTimeOffset
	Simon Bjork
	August 2014
	bjork.simon@gmail.com

	Synopsis: Set a random number to selected Read, TimeClip and TimeOffset nodes. Could also be used to set a start frame for selected Read nodes if minVal=maxVal.
	OS: Windows/OSX/Linux

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your menu.py:

	import sb_randomTimeOffset
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand("Python/sb RandomTimeOffset", 'sb_randomTimeOffset.sb_randomTimeOffset()', '')

"""

################

import nuke
import random

################

def sb_randomTimeOffset():

	p = nuke.Panel("sb RandomTimeOffset")
	p.addEnumerationPulldown("method", "offset startAt")
	p.addSingleLineInput('min', '-100')
	p.addSingleLineInput("max", "100")
	result = p.show()

	if not result:
		return

	try:
		minVal = int(p.value("min"))
		maxVal = int(p.value("max"))
	except ValueError:
		nuke.message("Enter numbers as min/max value.")
		return

	method = p.value("method")

	tn = []
	for i in nuke.selectedNodes():
		if i.Class() in ["Read", "DeepRead", "TimeClip"]:
			tn.append(i)
		elif i.Class() == "TimeOffset" and method == "offset":
			tn.append(i)

	if not tn:
		nuke.message("Select a Read, TimeOffset or TimeClip node.")
		return

	for i in tn:

		if minVal == maxVal:
			num = minVal
		else:
			num = random.randrange(minVal,maxVal+1)

		if method == "offset":
			if i.Class() == "TimeOffset":
				i["time_offset"].setValue(num)
			else:
				i["frame_mode"].setValue("offset")
				i["frame"].setValue(str(num))
		else:
			i["frame_mode"].setValue("start at")
			i["frame"].setValue(str(num))
