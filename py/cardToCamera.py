################

"""
    sb_cardToCamera
    Simon Bjork
    March 2014
    bjork.simon@gmail.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_cardToCamera
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
    sb_tools.addCommand("Python/sb CardToCamera", 'sb_cardToCamera.sb_cardToCamera()', '')

"""

################

import nuke

################

def sb_cardToCamera():

	cameras = []

	for i in nuke.selectedNodes():
		if i.Class() == "Camera" or i.Class() == "Camera2":
			cameras.append(i)

	if(len(cameras) == 0):
		nuke.message("Select a camera node.")
		return

	for i in cameras:
		card = nuke.createNode("Card2", inpanel = False)
		card["selected"].setValue(False)
		card["xpos"].setValue(i["xpos"].value())
		card["ypos"].setValue(i["ypos"].value() + 100)

		# Set values.
		card["translate"].fromScript(i["translate"].toScript()) 
		card["rotate"].fromScript(i["rotate"].toScript()) 
		card["lens_in_focal"].fromScript(i["focal"].toScript()) 
		card["lens_in_haperture"].fromScript(i["haperture"].toScript()) 
		card["z"].setValue(1000)
