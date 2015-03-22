################

"""
    sb_measureDistance
    Simon Bjork
    March 2014
    bjork.simon@gmail.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_measureDistance
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
    sb_tools.addCommand("Python/sb MeasureDistance", 'sb_measureDistance.sb_measureDistance()', '')

"""

################

import nuke
import math

################

def getTransformFromMatrix(node):

	if node.Class() == "Card" or node.Class() == "Card2":
		m = node["matrix"]
	else:
		m = node["world_matrix"]

	# Row/Column.
	x = m.value(0,3)
	y = m.value(1,3)
	z = m.value(2,3)

	return [x,y,z]

def measureDistance(p1,p2):
    dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
    return "{0:.3f}".format(dist)

def sb_measureDistance():

	nodes = []

	for i in nuke.selectedNodes():
		if i.Class() in ["Card", "Card2", "Camera", "Camera2", "Axis", "Axis2", "Light", "Light2"]:
			nodes.append(i)

	if len(nodes) == 0 or len(nodes) > 2:
		nuke.message("Select two (3d) nodes.")
		return

	n1 = getTransformFromMatrix(nodes[0])
	n2 = getTransformFromMatrix(nodes[1])

	distance = measureDistance(n1, n2)

	nuke.message("The distance between {0} and {1} is {2} units.".format(nodes[0]["name"].value(), nodes[1]["name"].value(), distance))
