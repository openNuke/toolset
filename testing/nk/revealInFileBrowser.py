################

"""
	sb_revealInFileBrowser
	Simon Bjork
	May 2014
	Version 1.0
	bjork.simon@gmail.com

	Synopsis: Open the path of the selected read/write nodes in the os file browser.
	OS: Windows/OSX/Linux

	To install the script:
	- Add the script to your Nuke pluginPath.
	- Add the following to your init.py/menu.py:

	import sb_revealInFileBrowser
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand('Python/sb RevealInFileBrowser', 'sb_revealInFileBrowser.sb_revealInFileBrowser()', "shift+r")

"""
################

import nuke
import os
import subprocess
import platform

################

def sb_revealInFileBrowser():

	n = nuke.selectedNodes("Read") + nuke.selectedNodes("Write")

	if len(n) == 0:
		nuke.message("Select at least one Read or Write node.")
		return

	if len(n) > 3:
		makeSure = nuke.ask("Are you sure you want to open {0} file browser windows?".format(len(n)))
		if not makeSure:
			return

	for i in n:
		try:
			getPath = i["file"].evaluate().split("/")[:-1]
			folderPath = "/".join(getPath)

			if platform.system() == "Windows":
				subprocess.Popen('explorer "{0}"'.format(folderPath.replace("/", "\\")))
			elif platform.system() == "Darwin":
				subprocess.Popen(["open", folderPath])
			elif platform.system() == "Linux":
				subprocess.Popen(["xdg-open", folderPath])
		except:
			continue
