################

"""
	sb_setKnobValue
	Simon Bjork
	September 2014
	Version 1.0
	bjork.simon@gmail.com

	Synopsis: Automatically set values on multiple knobs. Support for string/number knobs.
	OS: Windows/OSX/Linux

	To install the script:
	- Add the script to your Nuke pluginPath.
	- Add the following to your init.py/menu.py:

	import sb_setKnobValue
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand('Python/sb SetKnobValue', 'sb_setKnobValue.sb_setKnobValue()', "")

"""
################

from __future__ import with_statement
import nuke
import nukescripts

################

def sb_setKnobValue_Data():

	data = {}
	data["scriptName"] = "sb SetKnobValue"
	data["scriptVersion"] = "1.0"
	return data

def sb_setKnobValue_Help():

	si = sb_setKnobValue_Data()

	helpStr = ("<b>{0} {1}</b>\n\n"

	"Automatically set knob values to multiple nodes.\n\n"

	"Support for string/number knobs.\n\n"

	"Hover the mouse cursor over a knob to see it's name.\n\n"

	"When dealing with knobs that takes more than one value (such as a xyz transform knob), separate values with a comma (e.g. 100, 200, 300).".format(si["scriptName"], si["scriptVersion"] ))
	
	return helpStr.lstrip()

class sb_setKnobValue_Panel(nukescripts.PythonPanel):

	def __init__(self):
		scriptData = sb_setKnobValue_Data()
		nukescripts.PythonPanel.__init__(self, '{0} v{1}'.format(scriptData["scriptName"], scriptData["scriptVersion"]))
		self.nodes = nuke.Enumeration_Knob("nodes", "nodes", ["selected nodes", "all nodes", "all nodes (incl groups)"])
		self.div1 = nuke.Text_Knob("divider1", "")
		self.kName = nuke.String_Knob("kName", "knob name")
		self.kVal = nuke.String_Knob("kVal", "knob value")
		self.div2 = nuke.Text_Knob("divider2", "")
		self.help = nuke.PyScript_Knob("help", " ? ")
		self.help.setFlag(nuke.STARTLINE)
		self.div3 = nuke.Text_Knob("divider3", "")
		self.setVal = nuke.PyScript_Knob("setVal", "set value")

		for i in [self.nodes, self.div1, self.kName, self.kVal, self.div2, self.help, self.div3, self.setVal]:
			self.addKnob(i)

	# Set knobChanged commands.
	def knobChanged(self, knob):
		if knob is self.setVal:
			self.setKnobValue()
		elif knob is self.help:
			nuke.message(sb_setKnobValue_Help())

	# Main function.
	def setKnobValue(self):

		nodes = self.nodes.value()
		kName = self.kName.value()
		kVal = self.kVal.value()

		if nodes == "selected nodes":
			nodeList = nuke.selectedNodes()
		elif nodes == "all nodes":
			nodeList = nuke.allNodes()
		else:
			nodeList = nuke.allNodes(recurseGroups=True)

		if not kName or not kVal:
			nuke.message("Set both knob name and knob value.")
			return

		updatedNodes = 0
		convertedVal = None

		# Begin undo command.
		undo = nuke.Undo() 
		undo.begin(sb_setKnobValue_Data()["scriptName"])

		with nuke.root():

			for i in nodeList:
				try:
					i[kName]
				except:
					continue

				if i.Class() == "Viewer":
					continue
				
				if convertedVal == None:
					splitVals = kVal.split(",")
					
					if len(splitVals) > 1:
						multiKnobVal = []
						for j in splitVals:
							try:
								multiKnobVal.append(float(j))
							except ValueError:
								nuke.message("Set a number as a value.")
								return
						convertedVal = multiKnobVal
					else:
						convertedVal = kVal

				try:
					i[kName].setValue(convertedVal)
					updatedNodes+=1
				except:
					try:
						i[kName].setValue(float(convertedVal))
						updatedNodes+=1
					except:
						continue

		if updatedNodes == 1:
			nuke.message("sb SetKnobValue updated {0} knobs.".format(updatedNodes))
		else:
			nuke.message("sb SetKnobValue updated {0} knobs.".format(updatedNodes))

		# End undo command.
		undo.end()

# Run main script.
def sb_setKnobValue():
	sb_setKnobValue_Panel().show()
