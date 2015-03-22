################

"""
	sb_deleteViewers
	Simon Bjork
	October 2012
	bjork.simon@gmail.com

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your menu.py:

	import sb_deleteViewers
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand('Python/sb DeleteViewers', 'sb_deleteViewers.sb_deleteViewers()', 'shift+d')

"""

################
from __future__ import with_statement
import nuke
################

def sb_deleteViewers():
	counter = 0
	with nuke.root():
		for i in nuke.allNodes(recurseGroups=True):
			if i.Class() == "Viewer":
				nuke.delete(i)
				counter+=1
		print "sb DeleteViewers: {0} viewers deleted.".format(counter)
