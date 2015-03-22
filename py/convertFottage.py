################

"""
	sb_convertFootage
	Simon Bjork
	August 2014
	bjork.simon@gmail.com

	Synopsis: Speed up the process of converting footage (Read nodes) to another format/resolution/colorspace/naming convention.
	OS: Windows/OSX/Linux
	
	CAUTION: The script uses the Python threading module, which is a bit of a black box (to me). Use at own risk.

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your menu.py:

	import sb_convertFootage
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand("Python/sb ConvertFootage", 'sb_convertFootage.sb_convertFootage(showAsModal=False)', '')

	Note that you can set the showAsModal to True/False. Both options has pros/cons.

"""
################

import nuke
import nukescripts
import os
import threading
import PyOpenColorIO as OCIO
import re

################

def sb_convertFootage_Data():

	data = {}
	data["scriptName"] = "sb ConvertFootage"
	data["scriptVersion"] = "1.0"

	return data

def sb_convertFootage_Help():

	scriptData = sb_convertFootage_Data()

	hlpText = ("<b>{0} {1}</b>\n\n"
	"This script speeds up the process of converting footage to a different format/resolution/colorspace/naming convention. To use it, select one or several Read nodes, specify your settings and hit render.\n\n"
	"Below is a quick guide to the different knobs. Note than some knobs (custom filename, custom folder path, replace, with, prefix, suffix) can take TCL expressions (evaluated from the Read node), e.g.[value width]x[value height] to add the resolution as a suffix.\n\n"
	"<b>Filename base</b>\n\n"
	"Current filename: Use current filename (without framepadding and extension) as the base filename.\n\n"
	"Custom filename: Replace current filename with a custom filename. Most useful when rendering a single read node.\n\n"
	"Add number to filename (counting): Adds a counting number to the end of the custom name, e.g water01, water02, water03 etc. Useful when converting multiple elements of the same type.\n\n"
	"<b>Folder path base</b>\n\n"
	"Subfolder at current path (file extension): Renders footage to a subfolder at the current path (_EXR, _JPEG etc).\n\n"
	"Subfolder at current path (custom): Renders footage to a custom named subfolder at the current path.\n\n"
	"Custom path: Set a custom folder path.\n\n"
	"Add filename subfolder: Add a subfolder with the same name as the filename, e.g. shot01_plate.####.exr >> shot01_plate/shot01_plate.####.exr.\n\n"
	"<b>Replace word in filename</b>\n\n"
	"Replace word in filename: HelloWorld.exr, replace 'World' with 'Space' >> HelloSpace.exr. Note that the replace word can be empty (to remove matching word).\n\n"
	"<b>Prefix/Suffix</b>\n\n"
	"Add a prefix (at the beginning) or suffix (at the end) of the filename.\n\n"
	"<b>Colorspace options</b>\n\n"
	"Assume linearized input: Assumes that all Read nodes have been converted to linear gamma using the built-in luts. Set output colorspace for rendered footage.\n\n"
	"Specify input colorspace (pre Nuke): Set the input/output of your footage. This setting expects the input colorspace prior to Nuke (ignoring Read node colorspace).\n\n"
	"No color conversion: Uses raw workflow (no color conversion) for both input and output files.\n\n"
	"All colorspace conversions are made via OpenColorIO. Setup the OCIO envrionment variable to use custom configs.\n\n"
	"<b>Render action</b>\n\n"
	"Render selected: Renders the selected Read nodes.\n\n"
	"Setup nodes (no render): Creates all nodes (OCIO, Reformat, Write), but doesn't render. Useful if you want to handle the actual rendering on a render farm.\n\n"
	"Print render path (debugging): Prints the render path to the script editor. Useful when trying different parameters or debugging.\n\n"
	"<b>Post render action</b>\n\n"
	"Import: Imports the rendered footage. Support for the USE_OCIO environment variable (set to '1' to import using OCIO nodes).\n\n"
	"Replace: Replace the current file with the rendered file. Creates OCIO node if needed.\n\n"
	"Set as proxy: Sets the rendered footage as a proxy to current Read node.\n\n"
	"None: No post render action.\n\n").format(scriptData["scriptName"], scriptData["scriptVersion"])

	return hlpText

def getFileNameComponents(fileName):
	'''
	Split filename into components.
	Returns a list [<name>, <framepadding separator>, <framepadding>, <extension>]
	Assumes framepadding are at the end of the filename.
	Assumes the framepadding separator is ".", "_", "-".
	Make sure the filename uses numbers, not %04d or ####. Use <file knob>.evaluate() for this.

	Examples:
	getFileNameComponents(D:/images/img01.0001.exr)
	>> ['D:/images/img01', '.', '0001', 'exr']
	getFileNameComponents(D:/images/img01.exr)
	>> ['D:/images/img01', '', '', 'exr']
	'''
	splitExt= os.path.splitext(fileName)
	name = splitExt[0]
	ext = splitExt[1][1:]
	revName = name[::-1]

	if not revName[0].isdigit():
		return [name, "", "", ext]

	noNum = False

	for i in range(0, len(revName)):
		if not revName[i].isdigit():
			noNum = i

			if revName[noNum] in [".", "_", "-"]:
				separator = revName[noNum]
				padding = revName[:noNum][::-1]
				name = name[:-noNum-1]
				return [name, separator, padding, ext]
			else:
				return [name, "", "", ext]

def getOCIOConfig():
	return OCIO.GetCurrentConfig()

def getOCIOColorSpaces():	
	'''
	Get all OCIO colorspaces
	If a family name exist, return <family name>/<name>, otherwise return <name>.
	'''
	colorSpaces = []
	for i in getOCIOConfig().getColorSpaces():
		name = i.getName()
		familyName = i.getFamily()
		if familyName:
			colorSpaces.append("{0}/{1}".format(familyName, name))
		else:
			colorSpaces.append(name)

	return colorSpaces

def getOCIOFamilyAndName(colorSpaceName):
	'''
	Return colorspace family/name.
	If no family name, return name.
	'''
	colorFamily = False		
	for i in getOCIOConfig().getColorSpaces():
		if i.getName() == colorSpaceName:
			colorFamily = i.getFamily()
			break
	if colorFamily:
		colorSpaceName = "{0}/{1}".format(colorFamily, colorSpaceName)

	return colorSpaceName

def getOCIOLinear():	
	''' Get the default OCIO linear colorspace. '''	
	config = getOCIOConfig()
	try:
		defaultLin = config.getColorSpace(OCIO.Constants.ROLE_SCENE_LINEAR).getName()
		defaultLinFull = getOCIOFamilyAndName(defaultLin)
		return defaultLinFull
	except:
		return False

# Use this Class to do the rendering as you can't execute a render otherwise from a Python Panel (to my knowledge).
class sb_convertFootage_renderWrites(threading.Thread):

	def __init__(self, writeNode, firstFrame, lastFrame, readNode, colorSpace, colorSpaceOCIO, origRawVal, formatName, createdNodesList, postRender):
		# Start threading...
		threading.Thread.__init__(self)
		
		self.write = writeNode
		self.ff = firstFrame
		self.lf = lastFrame
		self.read = readNode
		self.colorspace = colorSpace
		self.colorspaceOCIO = colorSpaceOCIO
		self.origRawVal = origRawVal
		self.format = formatName
		self.createdNodes = createdNodesList
		self.postRender = postRender

	def renderAndCleanUp(self):
		''' Function that does the actual rendering (and cleans up afterwards).'''
		nuke.execute(self.write, self.ff, self.lf)

		nuke.tprint( "{0} ({1}) completed render: {2}".format(sb_convertFootage_Data()["scriptName"], self.read["name"].value(), self.write["file"].value()) )

		# Reset raw value.
		self.read["raw"].setValue(self.origRawVal)

		# Convert e.g. "default (Cineon)" to "Cineon" (if needed).
		colorNameFix = re.findall(r'\(([^]]*)\)', self.colorspace)
		if colorNameFix:
			self.colorspace = colorNameFix[0]

		# Post render actions.
		if self.postRender == "import":
			
			rn = nuke.createNode("Read", inpanel=False)
			rn["selected"].setValue(False)
			rn["file"].setValue(self.write["file"].value())
			rn["first"].setValue(self.ff)
			rn["last"].setValue(self.lf)
			rn["origfirst"].setValue(self.ff)
			rn["origlast"].setValue(self.lf)
			rn["format"].setValue(self.format)

			# Set colorspace. If found in default luts use that, otherwise add a OCIO node.
			if self.colorspace in rn["colorspace"].values() and not os.getenv("USE_OCIO") == "1":
				rn["colorspace"].setValue(self.colorspace)
			else:
				rn["raw"].setValue(True)
				rn["selected"].setValue(True)
				cs = nuke.createNode("OCIOColorSpace", inpanel=False)
				rn["selected"].setValue(False)
				cs["selected"].setValue(False)
				cs["ypos"].setValue(rn["ypos"].value() + 100)
				cs["tile_color"].setValue(8847615)
				cs.setInput(0, rn)
				cs["in_colorspace"].setValue(self.colorspaceOCIO)

		elif self.postRender == "replace":
			
			self.read["file"].setValue(self.write["file"].value())
			self.read["first"].setValue(self.ff)
			self.read["last"].setValue(self.lf)
			self.read["origfirst"].setValue(self.ff)
			self.read["origlast"].setValue(self.lf)
			self.read["format"].setValue(self.format)

			if not self.read["raw"].value():

				if self.colorspace in self.read["colorspace"].values():
					self.read["colorspace"].setValue(self.colorspace)
				else:
					self.read["raw"].setValue(True)
					self.read["selected"].setValue(True)
					cs = nuke.createNode("OCIOColorSpace", inpanel=False)
					cs["tile_color"].setValue(8847615)
					self.read["selected"].setValue(False)
					cs["selected"].setValue(False)
					cs.setInput(0, self.read)
					cs["in_colorspace"].setValue(self.colorspaceOCIO)

			self.read["reload"].execute()

		elif self.postRender == "set as proxy":
			self.read["proxy"].setValue(self.write["file"].value())

		# Delete nodes.
		for i in self.createdNodes:
			nuke.delete(i)

	def run(self):
		try:
			nuke.executeInMainThread(self.renderAndCleanUp, (), {})
		except Exception as e:
			print "ERROR: %s" % e

# Panel.
class sb_convertFootage_Panel(nukescripts.PythonPanel):

	def __init__(self):

		# Script data.
		scriptData = sb_convertFootage_Data()
		nukescripts.PythonPanel.__init__(self, '{0} v{1}'.format(scriptData["scriptName"], scriptData["scriptVersion"]))

		# Knobs.
		self.div1 = nuke.Text_Knob("divider1", "")
		self.fileName = nuke.Enumeration_Knob("fileName", "filename base", ["current filename", "custom filename"])
		self.customFileName = nuke.String_Knob("customFileName", "custom filename")
		self.addNumToName = nuke.Boolean_Knob("addNumToName", "add number to filename (counting)")
		self.addNumToName.setFlag(nuke.STARTLINE)

		self.div2 = nuke.Text_Knob("divider2", "")
		self.rootFolderMethod = nuke.Enumeration_Knob("rootFolderMethod", "folder path base", ["subfolder at current path (file format)", "subfolder at current path (custom)","custom path"])
		self.customSubFolder = nuke.String_Knob("customSubFolder", "custom subfolder")
		self.customRootFolder = nuke.File_Knob("customRootFolder", "custom folder path")
		self.fileNameSubFolder = nuke.Boolean_Knob("fileNameSubFolder", "add filename subfolder")
		self.fileNameSubFolder.setFlag(nuke.STARTLINE)
		
		self.div3 = nuke.Text_Knob("divider3", "")
		self.replace = nuke.Boolean_Knob("replace", "replace word in filename")
		self.replaceSrc = nuke.String_Knob("replaceSrc", "replace:")
		self.replaceDst = nuke.String_Knob("replaceDst", "with:")

		self.div4 = nuke.Text_Knob("divider4", "")
		self.prefix = nuke.String_Knob("prefix", "prefix")
		self.suffix = nuke.String_Knob("suffix", "suffix")

		self.div5 = nuke.Text_Knob("divider5", "")
		self.colorInMethod = nuke.Enumeration_Knob("colorInMethod", "input colorspace method", ["assume linearized input", "specify input colorspace (pre Nuke)", "no color conversion (raw)"])
		allColorSpaces = getOCIOColorSpaces()
		self.colorIn = nuke.CascadingEnumeration_Knob("colorIn", "colorspace in", allColorSpaces)
		self.colorOut = nuke.CascadingEnumeration_Knob("colorOut", "colorspace out", allColorSpaces)
		self.addColorToName = nuke.Boolean_Knob("addColorToName", "add colorspace to end of filename")
		self.addColorToName.setFlag(nuke.STARTLINE)

		self.div6 = nuke.Text_Knob("divider6", "")
		self.format = nuke.Enumeration_Knob("format", "format", ["current format", "reformat"])
		self.outFormat = nuke.Format_Knob("outFormat", "output format")
		self.resizeType = nuke.Enumeration_Knob("resizeType", "resize type", ["width", "height", "none"])
		self.resizeFilter = nuke.Enumeration_Knob("resizeFilter", "filter", ['Impulse', 'Cubic', 'Keys', 'Simon', 'Rifman', 'Mitchell', 'Parzen', 'Notch', 'Lanczos4', 'Lanczos6', 'Sinc4'])

		self.div7 = nuke.Text_Knob("divider7", "")
		self.frameRange = nuke.Enumeration_Knob("frameRange", "frame range", ["current range", "specify range"])
		self.ff = nuke.Int_Knob("ff", "first frame")
		self.lf = nuke.Int_Knob("lf", "last frame")

		self.div8 = nuke.Text_Knob("divider8", "")
		self.channels = nuke.Channel_Knob("channels", "channels")
		self.fileType = nuke.Enumeration_Knob("fileType", "file type", ["exr", "dpx", "jpeg", "tiff", "png"])

		self.div9 = nuke.Text_Knob("divider9", "")
		self.exrDataType = nuke.Enumeration_Knob("exrDataType", "data type", ["16 bit half", "32 bit float"])
		self.exrCompression = nuke.Enumeration_Knob("exrCompression", "compression", ["none", "Zip (1 scanline)", "Zip (16 scanlines)", "PIZ Wavelet (32 scanlines)", "RLE", "B44"])
		self.dpxDataType = nuke.Enumeration_Knob("dpxDataType", "data type", ["8 bit", "10 bit", "12 bit", "16 bit"])
		self.jpegQuality = nuke.Double_Knob("jpegQuality", "quality")
		self.jpegQuality.setRange(0,1)
		self.jpegSubSamp = nuke.Enumeration_Knob("jpegSubSamp", "sub-sampling", ["4:1:1", "4:2:2", "4:4:4"])
		self.tiffDataType = nuke.Enumeration_Knob("tiffDataType", "data type", ["8 bit", "16 bit", "32 bit float"])
		self.tiffCompression = nuke.Enumeration_Knob("tiffCompression", "compression", ["none", "PackBits", "LZW", "Deflate"])
		self.pngDataType = nuke.Enumeration_Knob("pngDataType", "data type", ["8 bit", "16 bit"])

		self.div10 = nuke.Text_Knob("divider10", "")
		self.renderAction = nuke.Enumeration_Knob("renderAction", "render action", ["render selected", "setup nodes (no render)", "print render path (debugging)"])
		self.postRenderAction = nuke.Enumeration_Knob("postRenderAction", "post render action", ["import", "replace", "set as proxy", "none"])
		
		self.div11 = nuke.Text_Knob("divider11", "")
		self.render = nuke.PyScript_Knob("render", "render")
		self.render.setFlag(nuke.STARTLINE)
		self.help = nuke.PyScript_Knob("help", " ? ")

		# Create a OK button. Do this as a hack so that OK/Cancel buttons arent added when using showModalDialg().
		self.okButton = nuke.Script_Knob( "OK" ) 
		self.addKnob( self.okButton )
		self.okButton.setVisible(False) 

		for i in [self.div1, self.fileName, self.customFileName, self.addNumToName, self.div2, self.rootFolderMethod, self.customRootFolder, self.customSubFolder, self.fileNameSubFolder, self.div3, self.replace, self.replaceSrc, self.replaceDst, self.div4, self.prefix, self.suffix, self.div5, self.colorInMethod, self.colorIn, self.colorOut, self.addColorToName, self.div6, self.format, self.outFormat, self.resizeType, self.resizeFilter, self.div7, self.frameRange, self.ff, self.lf, self.div8, self.channels, self.fileType, self.div9, self.exrDataType, self.exrCompression, self.dpxDataType, self.jpegQuality, self.jpegSubSamp, self.tiffDataType, self.tiffCompression, self.pngDataType, self.div10, self.renderAction, self.postRenderAction, self.div11, self.render, self.help]:
			self.addKnob(i)

		# Setup default values.
		self.fileNameSubFolder.setValue(True)
		self.addColorToName.setValue(True)
		self.ff.setValue( int(nuke.root()["first_frame"].value()) )
		self.lf.setValue( int(nuke.root()["last_frame"].value()) )
		self.resizeFilter.setValue("Cubic")

		# Set linear as default OCIO value.
		defaultLinSpace = getOCIOLinear()
		self.colorIn.setValue(defaultLinSpace)
		self.colorOut.setValue(defaultLinSpace)

		self.exrCompression.setValue("Zip (1 scanline")
		self.dpxDataType.setValue("10 bit")
		self.jpegQuality.setValue(0.8)
		self.jpegSubSamp.setValue("4:2:2")
		self.tiffDataType.setValue("16 bit")
		self.pngDataType.setValue("16 bit")

		# Hide knobs.
		self.customFileName.setVisible(False)
		self.addNumToName.setVisible(False)
		self.customSubFolder.setVisible(False)
		self.customRootFolder.setVisible(False)
		self.replaceSrc.setEnabled(False)
		self.replaceDst.setEnabled(False)
		self.colorIn.setVisible(False)
		self.outFormat.setVisible(False)
		self.resizeType.setVisible(False)
		self.resizeFilter.setVisible(False)
		self.ff.setVisible(False)
		self.lf.setVisible(False)

		self.dpxDataType.setVisible(False)
		self.jpegQuality.setVisible(False)
		self.jpegSubSamp.setVisible(False)
		self.tiffDataType.setVisible(False)
		self.tiffCompression.setVisible(False)
		self.pngDataType.setVisible(False)

	# Set knobChanged commands.
	def knobChanged(self, knob):

		if knob is self.fileName:
			if self.fileName.value() == "custom filename":
				self.customFileName.setVisible(True)
				self.addNumToName.setVisible(True)
			else:
				self.customFileName.setVisible(False)
				self.addNumToName.setVisible(False)

		if knob is self.rootFolderMethod:
			if self.rootFolderMethod.value() == "custom path":
				self.customRootFolder.setVisible(True)
				self.customSubFolder.setVisible(False)
			elif self.rootFolderMethod.value() == "subfolder at current path (custom)":
				self.customSubFolder.setVisible(True)
				self.customRootFolder.setVisible(False)
			else:
				self.customRootFolder.setVisible(False)
				self.customSubFolder.setVisible(False)

		elif knob is self.replace:
			if self.replace.value():
				self.replaceSrc.setEnabled(True)
				self.replaceDst.setEnabled(True)
			else:
				self.replaceSrc.setEnabled(False)
				self.replaceDst.setEnabled(False)

		elif knob is self.colorInMethod:
			if self.colorInMethod.value() == "specify input colorspace (pre Nuke)":
				self.colorIn.setVisible(True)
				self.colorOut.setVisible(True)
				self.addColorToName.setVisible(True)
			elif self.colorInMethod.value() == "no color conversion (raw)":
				self.colorIn.setVisible(False)
				self.colorOut.setVisible(False)
				self.addColorToName.setVisible(False)
			else:
				self.colorIn.setVisible(False)
				self.colorOut.setVisible(True)
				self.addColorToName.setVisible(True)

		elif knob is self.format:
			if self.format.value() == "current format":
				self.outFormat.setVisible(False)
				self.resizeType.setVisible(False)
				self.resizeFilter.setVisible(False)
			else:
				self.outFormat.setVisible(True)
				self.resizeType.setVisible(True)
				self.resizeFilter.setVisible(True)
		
		elif knob is self.frameRange:
			if self.frameRange.value() == "current range":
				self.ff.setVisible(False)
				self.lf.setVisible(False)
			else:
				self.ff.setVisible(True)
				self.lf.setVisible(True)

		elif knob is self.fileType:
			exrKnobs = [self.exrDataType, self.exrCompression]
			dpxKnobs = [self.dpxDataType]
			jpegKnobs = [self.jpegQuality, self.jpegSubSamp]
			tiffKnobs = [self.tiffDataType, self.tiffCompression]
			pngKnobs = [self.pngDataType]

			if self.fileType.value() == "exr":
				for i in exrKnobs:
					i.setVisible(True)
				for i in dpxKnobs+jpegKnobs+tiffKnobs+pngKnobs:
					i.setVisible(False)
			elif self.fileType.value() == "dpx":
				for i in dpxKnobs:
					i.setVisible(True)
				for i in exrKnobs+jpegKnobs+tiffKnobs+pngKnobs:
					i.setVisible(False)
			elif self.fileType.value() == "jpeg":
				for i in jpegKnobs:
					i.setVisible(True)
				for i in exrKnobs+dpxKnobs+tiffKnobs+pngKnobs:
					i.setVisible(False)
			elif self.fileType.value() == "tiff":
				for i in tiffKnobs:
					i.setVisible(True)
				for i in exrKnobs+dpxKnobs+jpegKnobs+pngKnobs:
					i.setVisible(False)
			elif self.fileType.value() == "png":
				for i in pngKnobs:
					i.setVisible(True)
				for i in exrKnobs+dpxKnobs+jpegKnobs+tiffKnobs:
					i.setVisible(False)

		elif knob is self.renderAction:
			if self.renderAction.value() == "render selected":
				self.postRenderAction.setEnabled(True)
			else:
				self.postRenderAction.setEnabled(False)

		elif knob is self.render:
			self.convertFootage()

		elif knob is self.help:
			nuke.message(sb_convertFootage_Help())

	# Main function.
	def convertFootage(self):

		# Setup variables from panel.
		fileNameMethod = self.fileName.value()
		addNum = self.addNumToName.value()
		customFileName = self.customFileName.value()
		rootFolderMethod = self.rootFolderMethod.value()
		customRootFolder = self.customRootFolder.value()
		customSubFolder = self.customSubFolder.value()
		fileNameSubFolder = self.fileNameSubFolder.value()

		replace = self.replace.value()
		replaceSrc = self.replaceSrc.value()
		replaceDst = self.replaceDst.value()

		prefix = self.prefix.value()
		suffix = self.suffix.value()

		colorInMethod = self.colorInMethod.value()
		colorIn = self.colorIn.value()
		colorOut = self.colorOut.value()
		addColorToName = self.addColorToName.value()

		reformat = self.format.value()
		outFormat = self.outFormat.value()
		resizeType = self.resizeType.value()
		resizeFilter = self.resizeFilter.value()

		frameRange = self.frameRange.value()
		ff = self.ff.value()
		lf = self.lf.value()

		channels = self.channels.value()
		fileType = self.fileType.value()

		exrDataType = self.exrDataType.value()
		exrCompression = self.exrCompression.value()
		dpxDataType = self.dpxDataType.value()
		jpegQuality = self.jpegQuality.value()
		jpegSubSamp = self.jpegSubSamp.value()
		tiffDataType = self.tiffDataType.value()
		tiffCompression = self.tiffCompression.value()
		pngDataType = self.pngDataType.value()

		renderAction = self.renderAction.value()
		postRenderAction = self.postRenderAction.value()

		# Make sure everything is filled in.
		if fileNameMethod == "custom filename" and not customFileName:
			nuke.message("Set a custom filename.")
			return

		if rootFolderMethod == "custom path" and not customRootFolder:
			nuke.message("Set a custom folder path.")
			return

		if rootFolderMethod == "subfolder at current path (custom)" and not customSubFolder:
			nuke.message("Set a custom subfolder name.")
			return

		# Collect read nodes.
		reads = nuke.selectedNodes("Read")

		if len(reads) == 0:
			nuke.message("Select a read node.")
			return

		# Deselect all nodes.
		nukescripts.clear_selection_recursive()

		# Get OCIO config.
		config = getOCIOConfig()

		# Node offsets.
		nox = 0
		noy = 125

		# Number in filename.
		currNum = 1

		# Loop over read nodes create render setups.
		for i in reads:

			currNode = i
			createdNodes = []

			# Setup/save values.
			formatName = i["format"].value()
			readLabel = i["label"].value()
			rawVal = i["raw"].value()

			# Framerange.
			if frameRange == "current range":
				ff = i["first"].value()
				lf = i["last"].value()

			# Setup filename. Use <knob> evalutate as it then will work with expressions.
			evalPath = i["file"].evaluate(i["first"].value())
			origFolderPath = evalPath.split("/")[0:-1]
			origFullFileName = evalPath.split("/")[-1]
			fileName, separator, framePadding, ext = getFileNameComponents(origFullFileName)

			if fileNameMethod == "custom filename":
				i["label"].setValue(customFileName)
				fileName = i["label"].evaluate()

			# Replace word.
			if replace and replaceSrc:
				i["label"].setValue(replaceSrc)
				replaceSrc = i["label"].evaluate()
				i["label"].setValue(replaceDst)
				replaceDst = i["label"].evaluate()
				fileName = fileName.replace(replaceSrc, replaceDst)

			# Add number to filename.
			if fileNameMethod == "custom filename" and addNum:
				if len(reads) < 100:
					formatNum = format(currNum,"02")
				else:
					formatNum = format(currNum, "03")
				fileName = "{0}{1}".format(fileName, formatNum)
				currNum+=1

			# Add prefix/suffix.
			if prefix:
				i["label"].setValue(prefix)
				fileName = "{0}{1}".format(i["label"].evaluate(), fileName)

			if suffix:
				i["label"].setValue(suffix)
				fileName = "{0}{1}".format(fileName, i["label"].evaluate())

			# Get colorspace out.
			if colorInMethod in ["assume linearized input", "specify input colorspace (pre Nuke)"]:
				
				colorSpaceOutOCIO = colorOut
				try:
					colorSpaceOut = colorSpaceOutOCIO.split("/")[1]
				except:
					colorSpaceOut = colorSpaceOutOCIO

				# Add colorspace to name. If there's already a matching colorspace name in the filename, replace that.
				if addColorToName:
					currColorSpaceName = config.parseColorSpaceFromString(fileName)
					if currColorSpaceName:
						fileName = fileName.replace(currColorSpaceName, colorSpaceOut)
					else:
						fileName = "{0}_{1}".format(fileName, colorSpaceOut)
			else:
				colorSpaceOutOCIO = False
				colorSpaceOut = False

			# Setup folder path.
			if rootFolderMethod == "custom path":
				i["label"].setValue(customRootFolder)
				folderPath = i["label"].evaluate()
			else:
				if rootFolderMethod == "subfolder at current path (custom)":
					subFolder = customSubFolder
				else:
					subFolder = "_{0}".format(fileType.upper())
				folderPath = "{0}/{1}".format("/".join(origFolderPath), subFolder)

			if not folderPath.endswith("/"):
				folderPath = "{0}/".format(folderPath)

			if fileNameSubFolder:
				folderPath = "{0}{1}/".format(folderPath, fileName)

			# Setup full render path.
			if framePadding:
				renderPath = "{0}{1}{2}{3}.{4}".format(folderPath, fileName, separator, "#"*len(framePadding), fileType)
			else:
				if ff == lf:
					renderPath = "{0}{1}.{2}".format(folderPath, fileName, fileType)
				else:
					paddingDef = 4
					currDigitLen = len(str(i["last"].value()))
					if currDigitLen > paddingDef:
						paddingDef = currDigitLen
					renderPath = "{0}{1}.{2}.{3}".format(folderPath, fileName, "#"*paddingDef, fileType)

			# If all we want to do is print the path, do that and jump out early.
			if renderAction == "print render path (debugging)":
				renderPathMsg = "{0} ({1}): {2}".format(sb_convertFootage_Data()["scriptName"], i["name"].value(), renderPath)
				print renderPathMsg
				continue

			# Create OCIO.
			if colorInMethod in ["assume linearized input", "specify input colorspace (pre Nuke)"]:
				currNode["selected"].setValue(True)
				c = nuke.createNode("OCIOColorSpace", inpanel=False)
				currNode["selected"].setValue(False)
				c["selected"].setValue(False)
				c.setInput(0, currNode)

				# Set input colorspace.
				if colorInMethod == "assume linearized":
					c["in_colorspace"].setValue(getOCIOLinear())
				elif colorInMethod == "specify input colorspace (pre Nuke)":
					i["raw"].setValue(True)
					ci = getOCIOFamilyAndName(colorIn)
					c["in_colorspace"].setValue(ci)

				# Set output colorspace.
				c["out_colorspace"].setValue(colorSpaceOutOCIO)

				currNode = c
				createdNodes.append(c)

			# If using no conversion mode.
			else:
				colorOut = i["colorspace"].value()
				i["raw"].setValue(True)

			# Create Reformat.
			if reformat == "reformat":
				currNode["selected"].setValue(True)
				rf = nuke.createNode("Reformat", inpanel=False)
				currNode["selected"].setValue(False)
				rf["selected"].setValue(False)
				rf.setInput(0, currNode)

				rf["format"].setValue(outFormat)
				rf["resize"].setValue(resizeType)
				rf["filter"].setValue(resizeFilter)

				formatName = outFormat

				currNode = rf
				createdNodes.append(rf)

			# Create Write node.
			currNode["selected"].setValue(True)
			w = nuke.createNode("Write", inpanel=False)
			currNode["selected"].setValue(False)
			w["selected"].setValue(False)
			w.setInput(0, currNode)
			createdNodes.append(w)

			w["raw"].setValue(True)
			w["channels"].setValue(channels)
			w["file_type"].setValue(fileType)

			if fileType == "exr":
				w["datatype"].setValue(exrDataType)
				w["compression"].setValue(exrCompression)
			elif fileType == "dpx":
				w["datatype"].setValue(dpxDataType)
			elif fileType == "jpeg":
				w["_jpeg_quality"].setValue(jpegQuality)
				w["_jpeg_sub_sampling"].setValue(jpegSubSamp)
			elif fileType == "tiff":
				w["datatype"].setValue(tiffDataType)
				w["compression"].setValue(tiffCompression)
			elif fileType == "png":
				w["datatype"].setValue(pngDataType)

			# Finally, set the path to the write node.
			w["file"].setValue(renderPath)

			# Reset label of read node.
			i["label"].setValue(readLabel)

			# Refocus on main tab of Read node.
			i["file"].setFlag(0)

			# Let's kick off a render, or be done with it!
			if renderAction == "render selected":
				if not os.path.exists(folderPath):
					try:
						os.makedirs(folderPath)
					except:
						for j in createdNodes:
							nuke.delete(j)
						raise Exception ("Couldn't create directory at {0}.".format(folderPath))

				t = sb_convertFootage_renderWrites(w, ff, lf, i, colorSpaceOut, colorSpaceOutOCIO, rawVal, formatName, createdNodes, postRenderAction)
				t.start()

			elif renderAction == "setup nodes (no render)":
				print "{0} created a render setup for {1}. Render path set to: {2}.".format(sb_convertFootage_Data()["scriptName"], i["name"].value(), renderPath)

		return True

# Run main script.
def sb_convertFootage(showAsModal=False):

	# Make sure OCIO is working correctly.
	if not getOCIOLinear():
		nuke.message("{0} couldn't find scene_linear role in current OCIO config. This rolde must be defined in order for the script (and OCIO overall) to work correctly.".format(sb_convertFootage_Data()["scriptName"]))
		return

	# Shwow panel.
	p = sb_convertFootage_Panel()
	p.setMinimumSize(700, 700)
	if showAsModal:
		p.showModalDialog()
	else:
		p.show()

# sb_convertFootage()
