################

"""
	sb_listExternalNodes
	Simon Bjork
	August 2014
	Version 1.0
	bjork.simon@gmail.com

	Synopsis: List all external nodes (not included in Nuke installation).
	OS: Windows/OSX/Linux
	Credits: Code inspired by NathanR's post at the Nuke mailing list (http://forums.thefoundry.co.uk/phpBB2/viewtopic.php?t=9753&sid=3086440af8928e92493aa6ddab3ff30b)

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your menu.py:

	# Example.
	import sb_listExternalNodes
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand("Python/sb ListExternalNodes", 'sb_listExternalNodes.sb_listExternalNodes()', '')

"""
################

from __future__ import with_statement
import nuke
import os

################

def longMessage(title, message):
    ''' Use instead of nuke.message() for long messages that require scrolling.'''
    p = nuke.Panel(title)
    p.addMultilineTextInput("", message)
    p.addButton("OK")
    p.setWidth(700)
    p.show()

def sb_listExternalNodes():

	# Nuke Path.
	nukeDir = os.path.dirname(nuke.env['ExecutablePath'])

	# Get loaded plugs/gizmos.
	p = nuke.plugins(0, '*.ofx', '*.%s' % nuke.PLUGIN_EXT)
	g = nuke.plugins(0, '*.gizmo')

	loadedPlugs = []
	loadedGizmos = []

	for i in p:
		if not i.startswith(nukeDir):
			pName = os.path.splitext(i.replace("\\", "/").split("/")[-1])[0]
			# Special case for Neat Video.
			if pName == "NeatVideo":
				pName = "OFXcom.absoft.neatvideo_v2"
			loadedPlugs.append(pName)

	for i in g:
		if not i.startswith(nukeDir):
			gName = os.path.splitext(i.replace("\\", "/").split("/")[-1])[0]
			loadedGizmos.append(gName)

	# See which of the loaded nodes are currently used.
	externalPlugins = []
	externalGizmos = []

	with nuke.root():

		for i in nuke.allNodes(recurseGroups=True):
			if i.Class() in loadedPlugs:
				if not i.Class() in externalPlugins:
					externalPlugins.append(i.Class())
			elif i.Class() in loadedGizmos:
				if not i.Class() in externalGizmos:
					externalGizmos.append(i.Class())

	# Format strings.
	gizmoStr = "\n".join( sorted(externalGizmos, key=lambda s: s.lower()) )
	plugStr = "\n".join( sorted(externalPlugins, key=lambda s: s.lower()) )
	externalNodes = "<b>sb ListExternalNodes</b>\n\nA list of external nodes used in current script.\n\n<b>Gizmos:</b>\n{0}\n\n<b>Plug-ins:</b>\n{1}\n\nNote that OFX plug-ins might not be listed.".format(gizmoStr, plugStr)

	# Print info.
	if nuke.GUI:
		lines = externalNodes.split("\n")
		if len(lines) > 125:
			longMessage("info", externalNodes)
		else:
			nuke.message(externalNodes)
	else:
		print externalNodes
