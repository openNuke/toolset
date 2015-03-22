################

"""
	sb_convertCornerPin
	Simon Bjork
	April 2014
	Latest update August 2014
	bjork.simon@gmail.com

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your menu.py:

	import sb_convertCornerPin
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand("Python/sb ConvertCornerPin", 'sb_convertCornerPin.sb_convertCornerPin()', '')

"""

################

import nuke
import nukescripts
import nuke.rotopaint as rp
import threading

################

def sb_convertCornerPin_Data():

	data = {}
	data["scriptName"] = "sb_convertCornerPin"
	data["scriptVersion"] = "1.1"

	return data

def getCornerPinMatrixAtFrame(node, frame, refFrame):
	
	projectionMatrixTo = nuke.math.Matrix4()
	projectionMatrixFrom = nuke.math.Matrix4()

	toValues = []
	fromValues = []

	for i in range(1,5):
		for j in range(2):
			toVal = node["to{0}".format(i)].valueAt(frame)[j]
			fromVal = node["to{0}".format(i)].valueAt(refFrame)[j] 

			toValues.append(toVal)
			fromValues.append(fromVal)

	projectionMatrixTo.mapUnitSquareToQuad(toValues[0], toValues[1], toValues[2], toValues[3], toValues[4], toValues[5], toValues[6], toValues[7])
	projectionMatrixFrom.mapUnitSquareToQuad(fromValues[0], fromValues[1], fromValues[2], fromValues[3], fromValues[4], fromValues[5], fromValues[6], fromValues[7])

	matrix = projectionMatrixTo*projectionMatrixFrom.inverse()    
	matrix.transpose()

	return matrix

def createTrackerHack(numTracks, startFrame):

	# Creates a tracker node and adds trackers.
	# Use this as a (ugly) workaround when creating trackers from a Python Panel, as you don't have to dive in to the threading stuff.

	startFrame = str(startFrame)

	addTrack = """{ {curve K x%s 1} "track 1" {curve x%s 630} {curve x%s 200} {curve K x%s 0} {curve K x%s 0} 1 0 0 {curve x%s 0} 0 0 -32 -32 32 32 -22 -22 22 22 {} {curve x%s 576} {curve x%s 146} {curve x%s 683} {curve x%s 253} {curve x%s 598} {curve x%s 168} {curve x%s 661} {curve x%s 231} {curve x%s 31.5} {curve x%s 31.5}  }""" % (startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame, startFrame)

	allTracks = ""

	for i in range(numTracks):
		fixName = addTrack.replace("track 1", "track {0}".format(i+1))
		if i != numTracks:
			allTracks = allTracks + fixName + "\n"
		else:
			allTracks = allTracks + fixName

	tracks = """{ 1 31 4 } 
	{ { 5 1 20 enable e 1 } 
	{ 3 1 75 name name 1 } 
	{ 2 1 58 track_x track_x 1 } 
	{ 2 1 58 track_y track_y 1 } 
	{ 2 1 63 offset_x offset_x 1 } 
	{ 2 1 63 offset_y offset_y 1 } 
	{ 4 1 27 T T 1 } 
	{ 4 1 27 R R 1 } 
	{ 4 1 27 S S 1 } 
	{ 2 0 45 error error 1 } 
	{ 1 1 0 error_min error_min 1 } 
	{ 1 1 0 error_max error_max 1 } 
	{ 1 1 0 pattern_x pattern_x 1 } 
	{ 1 1 0 pattern_y pattern_y 1 } 
	{ 1 1 0 pattern_r pattern_r 1 } 
	{ 1 1 0 pattern_t pattern_t 1 } 
	{ 1 1 0 search_x search_x 1 } 
	{ 1 1 0 search_y search_y 1 } 
	{ 1 1 0 search_r search_r 1 } 
	{ 1 1 0 search_t search_t 1 } 
	{ 2 1 0 key_track key_track 1 } 
	{ 2 1 0 key_search_x key_search_x 1 } 
	{ 2 1 0 key_search_y key_search_y 1 } 
	{ 2 1 0 key_search_r key_search_r 1 } 
	{ 2 1 0 key_search_t key_search_t 1 } 
	{ 2 1 0 key_track_x key_track_x 1 } 
	{ 2 1 0 key_track_y key_track_y 1 } 
	{ 2 1 0 key_track_r key_track_r 1 } 
	{ 2 1 0 key_track_t key_track_t 1 } 
	{ 2 1 0 key_centre_offset_x key_centre_offset_x 1 } 
	{ 2 1 0 key_centre_offset_y key_centre_offset_y 1 } 
	} 
	{ 
	 %s
	}""" % allTracks

	t = nuke.createNode("Tracker4")
	t["tracks"].fromScript(tracks)

	return t

class sb_convertCornerPin_Panel(nukescripts.PythonPanel):

	def __init__(self):
		scriptData = sb_convertCornerPin_Data()
		nukescripts.PythonPanel.__init__(self, '{0} v{1}'.format(scriptData["scriptName"], scriptData["scriptVersion"]))
		self.ff = nuke.Int_Knob("ff", "first frame")
		self.lf = nuke.Int_Knob("lf", "last frame")
		self.ref = nuke.Int_Knob("rf", "reference frame")
		self.stf = nuke.PyScript_Knob('stf', "Set frame")
		self.div1 = nuke.Text_Knob("divider1", "")
		self.output = nuke.Enumeration_Knob("output", "output", ["RotoPaint", "SplineWarp", "GridWarp", "CornerPin Match-move (Plane)", "CornerPin Stabilize (Plane)", "Tracker"])
		self.div2 = nuke.Text_Knob("divider2", "")
		self.createBtn = nuke.PyScript_Knob("createBtn", "create node")

		for i in [self.output, self.div1, self.ff, self.lf, self.ref, self.stf, self.div2, self.createBtn]:
			self.addKnob(i)

		self.ff.setValue( int( nuke.root()["first_frame"].value() ) )
		self.lf.setValue( int( nuke.root()["last_frame"].value() ) )
		self.ref.setValue( int( nuke.root()["frame"].value() ) )

	# Set knobChanged commands.
	def knobChanged(self, knob):
		
		if knob is self.createBtn:
			self.convertCornerPin()

		elif knob is self.stf:
			self.ref.setValue( int( nuke.root()["frame"].value() ) )

		elif knob is self.output:
			if self.output.value() == "CornerPin Match-move (Plane)" or self.output.value() == "CornerPin Stabilize (Plane)":
				self.ff.setEnabled(False)
				self.lf.setEnabled(False)
			else:
				self.ff.setEnabled(True)
				self.lf.setEnabled(True)

	# Main function.
	def convertCornerPin(self):

		# Get the selected node.
		try:
			n = nuke.selectedNode()
		except ValueError:
			nuke.message("Select a CornerPin node.")
			return

		if n.Class() != "CornerPin2D":
			nuke.message("Select a CornerPin node.")
			return

		n["selected"].setValue(False)

		# Collect values from panel.
		ff = self.ff.value()
		lf = self.lf.value()
		ref = self.ref.value()
		output = self.output.value()

		# Create nodes.
		if output == "RotoPaint" or output == "SplineWarp":

			if output == "RotoPaint":
				c = nuke.createNode("RotoPaint")
			else:
				c = nuke.createNode("SplineWarp3")

			curve = c['curves']
			root = curve.rootLayer
			newLayer = rp.Layer(curve)
			name = "tracked layer"
			newLayer.name = name
			root.append(newLayer)
			curve.changed()
			layer = curve.toElement(name)
			transform = layer.getTransform()

			for i in range(ff, lf+1):
				matrix = getCornerPinMatrixAtFrame(n, i, ref)
				for j in range(16):
					extraMatrixKnob = transform.getExtraMatrixAnimCurve(0,j)
					extraMatrixKnob.addKey(i,matrix[j])

			c["label"].setValue("reference frame: {0}".format(ref))

		elif output == "GridWarp":

			c = nuke.createNode("GridWarp3")
			c["source_grid_transform_matrix"].setAnimated()

			# Setup progress bar.
			task = nuke.ProgressTask('Adding keyframes...')
			progressCalc = 100.0/float(lf-ff)
			counter = 0

			for i in range(ff, lf+1):
				matrix = getCornerPinMatrixAtFrame(n, i, ref)
				for j in range(16):
					c["source_grid_transform_matrix"].setValueAt(matrix[j], i, j,)

				if task.isCancelled(): 
					print "Cancelled by user."
					break

				# Update progressbar.
				task.setProgress(int(counter*progressCalc))
				task.setMessage("Frame {0}".format(i))
				counter +=1

			del task

			c["label"].setValue("reference frame: {0}".format(ref))

		elif output == "CornerPin Match-move (Plane)" or output == "CornerPin Stabilize (Plane)":

			c = nuke.createNode("CornerPin2D")

			if output == "CornerPin Match-move (Plane)":
				cornerPinMain = "to"
				cornerPinRef = "from"
			else:
				cornerPinMain = "from"
				cornerPinRef = "to"

			main1 = "{0}1".format(cornerPinMain)
			main2 = "{0}2".format(cornerPinMain)
			main3 = "{0}3".format(cornerPinMain)
			main4 = "{0}4".format(cornerPinMain)

			c[main1].copyAnimations(n["to1"].animations())
			c[main2].copyAnimations(n["to2"].animations())
			c[main3].copyAnimations(n["to3"].animations())
			c[main4].copyAnimations(n["to4"].animations())

			# Add reference frame.
			tab = nuke.Tab_Knob("ref", "Reference frame")
			c.addKnob(tab)
			rf = nuke.Int_Knob("rf")
			c.addKnob(rf)
			rf.setLabel("Reference frame")
			c["rf"].setValue(ref)
			stf = nuke.PyScript_Knob('stf')
			stf.setLabel("Set to this frame")
			c.addKnob(stf)
			stf.setCommand( 'nuke.thisNode()["rf"].setValue(nuke.frame())' )

			c["{0}1".format(cornerPinRef)].setExpression("{0}(rf)".format(main1))
			c["{0}2".format(cornerPinRef)].setExpression("{0}(rf)".format(main2))
			c["{0}3".format(cornerPinRef)].setExpression("{0}(rf)".format(main3))
			c["{0}4".format(cornerPinRef)].setExpression("{0}(rf)".format(main4))

			c["label"].setValue("reference frame: [value rf]")

			# Focus on main tab.
			c["to1"].setFlag(0)

		elif output == "Tracker":

			# Need Nuke 7.0 to create a Tracker node.
			if int(nuke.NUKE_VERSION_MAJOR) < 7:
				nuke.message("You need to use Nuke 7.0 (or newer) to create a Tracker node.")
				return

			c = createTrackerHack(4, ff)

			tracker = c["tracks"]

			# Number of columns.
			numColumns = 31

			# Can we check all boxes to be used? Should we? Yes.

			# Add tracking data.
			for i in range(ff, lf+1):
				index = 0
				for j in [ n["to1"], n["to2"], n["to3"], n["to4"] ]:
					tracker.setValueAt(j.valueAt(i)[0], i, numColumns*index + 2)
					tracker.setValueAt(j.valueAt(i)[1], i, numColumns*index + 3)
					index = index +1

			c["reference_frame"].setValue(ref)

			tracker.setFlag(0)

		# Setup node.
		c["xpos"].setValue(n["xpos"].value()+50)
		c["ypos"].setValue(n["ypos"].value()+50)
		c["selected"].setValue(False)
		c.setInput(0, None)

# Run main script.
def sb_convertCornerPin():
	sb_convertCornerPin_Panel().show()
