################

"""
	sb_distributeObjects
	Simon Bjork
	May 2014
	Version 1.1 (August 2014)
	bjork.simon@gmail.com

	Synopsis: Create a number of evenly distributed 3d objects between two (selected) 3d objects.
	OS: Windows/OSX/Linux

	To install the script:
	- Add the script to your Nuke pluginPath.
	- Add the following to your init.py/menu.py:

	import sb_distributeObjects
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand('Python/sb DistributeObjects', 'sb_distributeObjects.sb_distributeObjects()', "shift+w")

"""
################

import nuke
import nukescripts

################

def sb_distributeObjects_Data():

	data = {}
	data["scriptName"] = "sb DistributeObjects"
	data["scriptVersion"] = "1.0"
	return data

def sb_distributeObjects_Help():

	si = sb_distributeObjects_Data()


	helpStr = ("<b>{0} {1}</b>\n\n"

	"Select two or more 3d nodes and specify the number of objects to create (evenly) in-between.\n\n"

	"If you select more than two objects (to get a curved path for example), make sure you select the nodes in the correct path, as the script will follow the selection order. Preferably left to right order.\n\n"

	"The script works in x,y,z dimensions.".format(si["scriptName"], si["scriptVersion"] ))
	
	return helpStr.lstrip()

class sb_distributeObjects_Panel(nukescripts.PythonPanel):

	def __init__(self):
		scriptData = sb_distributeObjects_Data()
		nukescripts.PythonPanel.__init__(self, '{0} v{1}'.format(scriptData["scriptName"], scriptData["scriptVersion"]))
		self.num = nuke.Int_Knob("number", "number of nodes")
		self.transform = nuke.Enumeration_Knob("transform", "transform", ["translate", "translate/rotate", "translate/rotate/scale"])
		self.controller = nuke.Boolean_Knob("controller", "add master controls")
		self.controller.setFlag(nuke.STARTLINE)
		self.div1 = nuke.Text_Knob("divider1", "")
		self.help = nuke.PyScript_Knob("help", " ? ")
		self.help.setFlag(nuke.STARTLINE)
		self.div2 = nuke.Text_Knob("divider2", "")
		self.createNodes = nuke.PyScript_Knob("createNodes", "create nodes")

		for i in [self.num, self.transform, self.controller, self.div1, self.help, self.div2, self.createNodes]:
			self.addKnob(i)

		self.num.setValue(5)

	# Set knobChanged commands.
	def knobChanged(self, knob):
		if knob is self.createNodes:
			self.distributeObjects()
		elif knob is self.help:
			nuke.message(sb_distributeObjects_Help())

	# Main function.
	def distributeObjects(self):

		numObj = self.num.value()
		transform = self.transform.value()
		controller = self.controller.value()

		if not numObj:
			nuke.message("Enter a number.")
			return

		n = []
		for i in nuke.selectedNodes()[::-1]:
			try:
				i["translate"].value()[2]
				n.append(i)
			except:
				continue

		if len(n) < 2:
			nuke.message("Select two (3d) nodes.")
			return
		
		npx = n[0]["xpos"].value()
		npy = n[0]["ypos"].value()
		offset = 0

		# Begin undo command.
		undo = nuke.Undo() 
		undo.begin(sb_distributeObjects_Data()["scriptName"])

		# Create scene node.
		scene = nuke.createNode("Scene", inpanel=False)
		scene["selected"].setValue(False)
		scene["xpos"].setValue(n[0]["xpos"].value())
		scene["ypos"].setValue(n[0]["ypos"].value() + 500)
		currSceneInp = 0

		# Create controller.
		ctrlKnobs1 = ["translate", "rotate"]
		ctrlKnobs2 = ["scaling", "uniform_scale"]
		if controller:
			ctrl = nuke.createNode("NoOp", inpanel=False)
			ctrl["selected"].setValue(False)
			ctrlT = nuke.XYZ_Knob("translate", "translate")
			ctrlR = nuke.XYZ_Knob("rotate", "rotate")
			ctrlS = nuke.XYZ_Knob("scaling", "scale")
			ctrlUS = nuke.Double_Knob("uniform_scale", "uniform scale")

			for i in [ctrlT, ctrlR, ctrlS, ctrlUS]:
				ctrl.addKnob(i)

			ctrl["xpos"].setValue(n[0]["xpos"].value() - 100)
			ctrl["ypos"].setValue(n[0]["ypos"].value() - 100)
			ctrl["tile_color"].setValue(3448912)
			ctrl["note_font_size"].setValue(36)
			ctrl["label"].setValue("master controls")

			ctrlS.setValue([1.0,1.0,1.0])
			ctrlUS.setValue(1.0)

		for i in range(len(n)+1):

			# Setup selected nodes.
			n[i]["tile_color"].setValue(11993343)
			n[i]["selected"].setValue(False)

			scene.setInput(currSceneInp, n[i])
			currSceneInp+=1

			n[i]["xpos"].setValue(npx+offset)
			n[i]["ypos"].setValue(npy)
			offset = offset + 100

			if controller:
				for j in ctrlKnobs1:
					n[i][j].setExpression("{0}+{1}.{0}".format(j, ctrl["name"].value() ))
				for j in ctrlKnobs2:
					n[i][j].setExpression("{0}*{1}.{0}".format(j, ctrl["name"].value() ))

			# Break out if it's the last selected node.
			if i == len(n)-1:
				break

			# Setup variables.
			ax, ay, az = n[i]["translate"].value()
			bx, by, bz = n[i+1]["translate"].value()

			arx, ary, arz = n[i]["rotate"].value()
			brx, bry, brz = n[i+1]["rotate"].value()

			asx, asy, asz = n[i]["scaling"].value()
			bsx, bsy, bsz = n[i+1]["scaling"].value()

			aus = n[i]["uniform_scale"].value()
			bus = n[i+1]["uniform_scale"].value()

			# Number of nodes.
			numNodes = float(numObj)+1

			# Translate calculation.			
			txCalc = (bx-ax)/numNodes
			tyCalc = (by-ay)/numNodes
			tzCalc = (bz-az)/numNodes

			# Rotation calculation.
			rxCalc = (brx-arx)/numNodes
			ryCalc = (bry-ary)/numNodes
			rzCalc = (brz-arz)/numNodes

			# Scale calculation.
			sxCalc = (bsx-asx)/numNodes
			syCalc = (bsy-asy)/numNodes
			szCalc = (bsz-asz)/numNodes
			usCalc = (bus-aus)/numNodes

			# Create in-between nodes.		
			for j in range(1,int(numNodes)):

				c = nuke.createNode(n[i].Class(), inpanel = False)
				c["selected"].setValue(False)

				# Translate.
				newX = ax+(txCalc*j)
				newY = ay+(tyCalc*j)
				newZ = az+(tzCalc*j)
				c["translate"].setValue([newX, newY, newZ])

				# Rotate.
				if transform in ["translate/rotate", "translate/rotate/scale"]:

					newRX = arx+(rxCalc*j)
					newRY = ary+(ryCalc*j)
					newRZ = arz+(rzCalc*j) 
					c["rotate"].setValue([newRX, newRY, newRZ])

					# Scale.
					if transform == "translate/rotate/scale":

						newSX = asx+(sxCalc*j)
						newSY = asy+(syCalc*j)
						newSZ = asy+(szCalc*j)
						newUS = aus+(usCalc*j)
						c["scaling"].setValue([newSX, newSY, newSZ])
						c["uniform_scale"].setValue(newUS)

				if controller:
					for k in ctrlKnobs1:
						c[k].setExpression("{0}+{1}.{0}".format(k, ctrl["name"].value() ))
					for k in ctrlKnobs2:
						c[k].setExpression("{0}*{1}.{0}".format(k, ctrl["name"].value() ))



				if npx == "":
					npx = n[i]["xpos"].value()
					npy = n[i]["ypos"].value()
		
				c["xpos"].setValue(npx + offset)
				c["ypos"].setValue(npy)

				scene.setInput(currSceneInp, c)
				currSceneInp+=1

				offset = offset + 100

		# End undo command.
		undo.end()

# Run main script.
def sb_distributeObjects():
	sb_distributeObjects_Panel().show()
