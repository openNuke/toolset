################

"""
	sb_replacePaths
	Simon Bjork
	March 2014
	Latest update September 2014
	bjork.simon@gmail.com

	Synopsis: Replace the file path (part or full) of e.g. Read nodes.
	
	Usage example:

	Current path: D:/projects/show/shot/plates/plate.exr
	Source path: D:/projects/
	Destination path: /net/
	Result: /net/show/shot/plates/plate.exr.

	CAUTION: Make sure you enter a unique string as source path. For example if you enter D as source path (D:/myDog/myDog.exr), the script will then replace all instances of D. Use D:/ instead (which makes it unique). 

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your menu.py:

	import sb_replacePaths
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand("Python/sb ReplacePaths", 'sb_replacePaths.sb_replacePaths()', '')

"""
################

from __future__ import with_statement
import nuke
import nukescripts

################

def sb_replacePaths_Data():
	data = {}
	data["scriptName"] = "sb_replacePaths"
	data["scriptVersion"] = "1.3"
	return data

def sb_replacePaths_Help():

	si = sb_replacePaths_Data()
	helpStr = ("<b>{0} {1}</b>\n\n"

	"Replace the file path (part or full) of all nodes with a file knob, e.g. Read nodes.\n\n"
	
	"Usage example:\n\n"

	"Current path: D:/projects/show/shot/plates/plate.exr\n"
	"Source path: D:/projects/\n"
	"Destination path: /net/\n"
	"Result: /net/show/shot/plates/plate.exr.\n\n"

	"CAUTION: Make sure you enter a unique string as source path. For example if you enter D as source path (D:/myDog/myDog.exr), the script will then replace all instances of D. Use D:/ instead (which makes it unique).\n\n".format(si["scriptName"], si["scriptVersion"] ))
	
	return helpStr.lstrip()

class sb_replacePaths_Panel(nukescripts.PythonPanel):	
	def __init__(self):
		scriptData = sb_replacePaths_Data()
		nukescripts.PythonPanel.__init__(self, '{0} v{1}'.format(scriptData["scriptName"], scriptData["scriptVersion"]))
		self.nodes = nuke.Enumeration_Knob("nodes", "nodes", ["selected nodes", "all nodes"])
		self.rootNode = nuke.Boolean_Knob("rootNode", "include root node")
		self.rootNode.setFlag(nuke.STARTLINE)
		self.div1 = nuke.Text_Knob("divider1", "")
		self.source = nuke.File_Knob("source", "source path")
		self.destination = nuke.File_Knob("destination", "destination path")
		self.div2 = nuke.Text_Knob("divider2", "")
		self.help = nuke.PyScript_Knob("help", " ? ")
		self.div3 = nuke.Text_Knob("divider3", "")
		self.replace = nuke.PyScript_Knob("replace", "replace paths")

		for i in [self.nodes, self.rootNode, self.div1, self.source, self.destination, self.div2, self.help, self.div3, self.replace]:
			self.addKnob(i)

	# Set knobChanged commands.
	def knobChanged(self, knob):
		if knob is self.replace:
			self.replacePath()
		elif knob is self.help:
			nuke.message(sb_replacePaths_Help())

	# Main function.
	def replacePath(self):
		nodes = self.nodes.value()
		rootNode = self.rootNode.value()
		src = self.source.value()
		dest = self.destination.value()
		updatedNodes = []

		# Always start at the root level, and then dive into groups if needed.
		with nuke.root():

			nodeList = nuke.allNodes(recurseGroups=True)
			if rootNode:
				nodeList.append(nuke.root())

			for i in nodeList:
				if i.Class() == "Root":
					if not rootNode:
						continue
				elif nodes == "selected nodes" and i["selected"].value() == False:
					continue

				for j in i.knobs():
					# Don't update the name knob of the root node. Can't save script if we do.		
					if i.Class() == "Root" and j == "name":
						continue
					if i[j].Class() == "File_Knob":
						if i[j].value():							
							currPath = i[j].value()
							newPath  = currPath.replace(src, dest)
							# If not updated, keep going.
							if currPath == newPath:
								continue
							# Set new path.
							i[j].setValue(newPath)
							if i.Class() == "Root":
								name = "Root ({0})".format(j)
							else:
								name = "{0} ({1})".format(i["name"].value(), j)
							updatedNodes.append(name)

			if len(updatedNodes) == 0:
				updatedNodes.append("None")

			print "{0} updated: {1}".format( sb_replacePaths_Data()["scriptName"], ", ".join(updatedNodes))

# Run main script.
def sb_replacePaths():
	sb_replacePaths_Panel().show()
