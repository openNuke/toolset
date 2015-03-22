################

"""
	sb_createRead
	Simon Bjork
	July 2014
	Latest update August 2014
	Version 1.1
	bjork.simon@gmail.com

	Synopsis: Custom create read function with support for OpenColorIO.
	OS: Windows/OSX/Linux
	Comments: Set the envrionment variable USE_OCIO to "1" (or "True") to use OCIO.
	Installation: Override the default nukescripts.create_read() function.

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your init.py:

	os.environ["USE_OCIO] = 1
	import sb_createRead
	nukescripts.create_read = sb_createRead

"""

################

import os
import nuke
import nukescripts
import PyOpenColorIO as OCIO

################

def sb_createRead_Data():
	data = {}
	data["scriptName"] = "sb CreateRead"
	data["scriptVersion"] = "1.1"
	return data

def createOCIOColorspaceNode(readNode):

	o = nuke.createNode("OCIOColorSpace")
	o["tile_color"].setValue(8847615)
	o.setInput(0, readNode)
	fileName = readNode["file"].value().split("/")[-1]

	# Get colorspace..
	# The current config ($OCIO)
	config = OCIO.GetCurrentConfig()

	# Try to get color-space from file name.
	colorSpaceName = config.parseColorSpaceFromString(fileName)

	# Couldn't find colorspace. Set manually.
	if not colorSpaceName:
		print "OCIO colorspace not found."
		return

	# Get family name.
	colorSpaceFamily = ""
	for i in config.getColorSpaces():
		if i.getName() == colorSpaceName:
			colorSpaceFamily = i.getFamily()
			break

	# Set colorspace.
	try:
		colorSpace = "{0}/{1}".format(colorSpaceFamily, colorSpaceName)
		o["in_colorspace"].setValue(colorSpace)
		print "OCIO colorspace set to: {0}".format(csName)
	except:
		print "Could not set input colorspace ({0}) of OCIO node.".format(colorSpaceName)
		pass

def sb_createRead(nodeType="Read"):

	'''
	Depending on wich type of read (Deep, Audio), the nodeType will update.
	'''

	version = 1.1
	
	files = nuke.getClipname("Image file(s)", multiple=True)

	if not files:
		return

	for i in files:
		r = nuke.createNode(nodeType, "file {"+i+"}", inpanel = True)
		if nodeType in ["Read", "DeepRead"]:
			if os.getenv("USE_OCIO") in ["1", "True"]:
				createOCIOColorspaceNode(r)
				r["raw"].setValue(True)

	scriptData = sb_createRead_Data()
	print "Read node(s) created with {0} version {1}.".format(scriptData["scriptName"], scriptData["scriptVersion"])
