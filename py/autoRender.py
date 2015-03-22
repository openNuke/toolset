################

"""
	sb_autoRender
	Simon Bjork
	April 2014
	Version 1.1 (August 2014)
	bjork.simon@gmail.com

	Synopsis: Automatically setup write paths when rendering. Customizable to fit most pipelines.
	OS: Windows/OSX/Linux

	To install the script:
	- Add the script to your Nuke pluginPath.
	- Add the following to your init.py/menu.py:

	#init.py	
	import sb_autoRender
	nuke.addBeforeRender(sb_autoRender.sb_autoRender)

	#menu.py (default setup)
	import sb_autoRender
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand('Python/sb AutoRender', 'sb_autoRender.sb_autoRender()', "shift+w")

	--------------------------

	You also have the option to set default values to most of the knobs depending on your pipeline.
	The syntax for adding a custom version of sb_autoWrite:
	<menu-bar>.addCommand("<name in menu>", 'sb_autoRender.sb_autoRenderNode("<root folder method>", "<user input (search word/environment variables)>", "<custom path>", "<render name>", "<custom name>", "<render type>", "<prefix>", "<suffix>", "<add colorspace to filename>", "<use OCIO for color conversions>", "<channels>", "<colorspace>", "<file extension>", "<main render folder>", "<precomp render folder>", "<proxy render folder>", "<framepadding separator (._-)>", "framepadding (#)" )', '')
	Note that the environment variable USE_OCIO (set to "1") will override the useOCIO argument.
	Some knobs (prefix, suffix, custom path, custom render name) can be written as TCL expressions and evaluated at rendertime. For example you could add _[value channels] to write the channels as a suffix.

	To make the custom setup more readable, I recommend using something like the following in your menu.py::

	import sb_autoRender
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )

	# Setup knobs.
	sb_autoRenderSettings = {}
	sb_autoRenderSettings["method"] = "search word"
	sb_autoRenderSettings["userInput"] = "comp"
	sb_autoRenderSettings["customRootPath"] = ""
	sb_autoRenderSettings["renderName"] = "script name"
	sb_autoRenderSettings["customName"] = ""
	sb_autoRenderSettings["renderType"] = "main render"
	sb_autoRenderSettings["prefix"] = ""
	sb_autoRenderSettings["suffix"] = ""
	sb_autoRenderSettings["addColorToFileName"] = True
	sb_autoRenderSettings["useOCIO"] = True
	sb_autoRenderSettings["channels"] = "rgb"
	sb_autoRenderSettings["colorspace"] = "AlexaV3LogC"
	sb_autoRenderSettings["fileType"] = "dpx"
	sb_autoRenderSettings["mainRenderFolder"] = "publish/comp"
	sb_autoRenderSettings["precompRenderFolder"] = "publish/precomp"
	sb_autoRenderSettings["proxyRenderFolder"] = "publish/proxy"
	sb_autoRenderSettings["framePaddingSeparator"] = "."
	sb_autoRenderSettings["framePadding"] = "####"

	# Add to menu.
	sb_tools.addCommand('Python/sb AutoRender', '''sb_autoRender.sb_autoRenderNode(
	sb_autoRenderSettings["method"],
	sb_autoRenderSettings["userInput"], 
	sb_autoRenderSettings["customRootPath"],
	sb_autoRenderSettings["renderName"],
	sb_autoRenderSettings["customName"],
	sb_autoRenderSettings["renderType"],
	sb_autoRenderSettings["prefix"],
	sb_autoRenderSettings["suffix"],
	sb_autoRenderSettings["addColorToFileName"],
	sb_autoRenderSettings["useOCIO"],
	sb_autoRenderSettings["channels"],
	sb_autoRenderSettings["colorspace"],
	sb_autoRenderSettings["fileType"],
	sb_autoRenderSettings["mainRenderFolder"],
	sb_autoRenderSettings["precompRenderFolder"],
	sb_autoRenderSettings["proxyRenderFolder"],
	sb_autoRenderSettings["framePaddingSeparator"],
	sb_autoRenderSettings["framePadding"]
	)''', "shift+w")

"""
################

import os
import nuke
import re
import PyOpenColorIO as OCIO

################

def sb_autoRenderCreateRenderDirs(path):

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		try:
			os.makedirs(dirname)
		except OSError:
			pass

def getNodeInput(node, input, ignoreNode='Dot'):

	''' 
	Get input from node, ignoring a specific node.
	print getNodeInput(nuke.selectedNode(), 0)
	'''    
	found = False     
	while not found:
		# Get input.        
		currInput = node.input(input)        
		# If no input is found, return False.
		if currInput == "" or currInput == None:
			return False
		if currInput.Class() == ignoreNode:
			# If not found, keep looking.
			return getNodeInput( currInput, 0, ignoreNode ) 
		else: 
			found = True 
			return currInput

def replaceEnvsInsideBrackets(str):

	'''
	Replace envrionment variables within brackets
	myStr = "My temp dir is: [TEMP]
	print replaceEnvsInsideBrackets(myStr)
	>> My temp dir is: C:/Users/Simon/AppData/Local/Temp
	'''
	foundEnvs = re.findall(r'\[([^]]*)\]', str)
	
	for i in foundEnvs:
		env = i
		val = os.getenv(env.replace("'", "").replace('"', ''))
		if not val:
			raise Exception ("Could not find environment variable: {0}".format(env))
		str = str.replace("[{0}]".format(env), val.replace("\\", "/"))

	return str

def rootFolderHelp():

	helpText = """

	<b>Root folder method</b> 

	The root folder works as the base for the full render path. This is the key parameter in having the script automatically work out where you want your renders located.
	 
	<b>-Search word:</b>
	Search for a specific word in the file path of the current Nuke script. The root folder will then be set one level up from the search word. For example, let's say we have a script saved at D:/show/shot01/nuke/shot01_v001.nk, and we use 'nuke' as search word. The root folder will then be set to D:/projects/show/shot01/.

	<b>- Environment variables:</b>
	Evaluate environment variables to build the root folder. Use [<name>] syntax for environment variables. For example: D:/projects/[SHOW]/[SEQ]/[SHOT]/.

	<b>- Custom path:</b>
	Manually set the root folder.

	"""
	return helpText

def sb_autoRenderNode(rootFolderMethod = "search word", rootFolderUserInput = "projectfiles", customRenderPath = "", renderName = "script name", customName = "", renderType = "main render", prefix = "", suffix = "", addColorToFileName = True, useOCIO = True,  channels = "rgb", colorspace = "linear", fileType = "exr", mainRenderFolder = "renders/main", precompRenderFolder = "render/precomp", proxyRenderFolder = "render/proxy", framePaddingSep = ".", framePadding = "#####"):

	# Environment variable that override the argument.
	# The USE_OCIO env is also used by sb_createRead.py.
	if os.getenv("USE_OCIO") == "1":
		useOCIO = True

	if useOCIO:
		o = nuke.createNode("OCIOColorSpace")

		# Get family name (if used in the config).
		config = OCIO.GetCurrentConfig()
		colorFamily = ""
		
		for i in config.getColorSpaces():
			if i.getName() == colorspace:
				colorFamily = i.getFamily()
				break
		if colorFamily:
			colorspace = "{0}/{1}".format(colorFamily, colorspace)

		o["out_colorspace"].setValue(colorspace)
		o["tile_color"].setValue(8847615)
		
		n = nuke.createNode("Write")
		n.setInput(0, o)
		n["xpos"].setValue(o["xpos"].value())
		n["ypos"].setValue(o["ypos"].value()+75)
		n["raw"].setValue(True)

		o["selected"].setValue(True)
		n["selected"].setValue(True)
	else:
		n = nuke.createNode("Write")

	n["tile_color"].setValue(4289462527)
	n["label"].setValue("sb AutoRender")
	name = n["name"].value()

	# Add main tab.
	mainTab = nuke.Tab_Knob("sb_autoRender", "sb AutoRender")
	rootFolderMethodKnob = nuke.Enumeration_Knob("rootFolderMethod", "root folder method", ["search word", "environment variables", "custom path"])
	rootFolderMethodKnob.clearFlag(nuke.STARTLINE)
	rootFolderHelpKnob = nuke.PyScript_Knob("rootFolderHelpKnob", "?", "")
	rootFolderHelpKnob.clearFlag(nuke.STARTLINE)
	rootFolderUserInputKnob = nuke.String_Knob("rootFolderUserInput", "user input")
	customRootFolderKnob = nuke.File_Knob("customRootFolderPath", "custom path")
	div1 = nuke.Text_Knob("divider1", "")
	renderNameKnob = nuke.Enumeration_Knob("renderName", "render name", ["script name", "custom name"])
	customNameKnob = nuke.String_Knob("customName", "custom name")
	div2 = nuke.Text_Knob("divider2", "")
	renderTypeKnob = nuke.Enumeration_Knob("renderType", "render type", ["main render", "precomp render", "proxy render", "none"])
	div3 = nuke.Text_Knob("divider3", "")
	prefixKnob = nuke.String_Knob("prefix", "prefix")
	suffixKnob = nuke.String_Knob("suffix", "suffix")
	hiddenEvalKnob = nuke.File_Knob("hiddenEvalKnob", "hiddenEvalKnob")
	div4 = nuke.Text_Knob("divider4", "")
	addColorNameKnob = nuke.Boolean_Knob('addColorSpaceName', "add colorspace to filename")
	useOCIOKnob = nuke.Boolean_Knob("use_ocio", "use OCIO for color conversions")
	useOCIOKnob.setFlag(nuke.STARTLINE)
	div5 = nuke.Text_Knob("divider5", "")
	channelsKnob = nuke.Link_Knob("c", "channels")
	colorspaceKnob = nuke.Link_Knob("cs", "colorspace")
	rawKnob = nuke.Link_Knob("raw_color", "raw")
	rawKnob.clearFlag(nuke.STARTLINE)
	fileTypeKnob = nuke.Link_Knob("ft", "file type")
	div6 = nuke.Text_Knob("divider6", "")
	renderKnob = nuke.PyScript_Knob("rl", "render", "nukescripts.render_panel((nuke.thisNode(),), False)")

	# Link knobs.
	channelsKnob.setLink("channels")
	colorspaceKnob.setLink("colorspace")
	rawKnob.setLink("raw")
	fileTypeKnob.setLink("file_type")

	# Set default values.
	rootFolderMethodKnob.setValue(rootFolderMethod)
	rootFolderUserInputKnob.setValue(rootFolderUserInput)
	customRootFolderKnob.setValue(customRenderPath)
	rootFolderHelpKnob.setValue( "nuke.message('''{}''')".format(rootFolderHelp()) )
	renderNameKnob.setValue(renderName)
	customNameKnob.setValue(customName)
	renderTypeKnob.setValue(renderType)
	prefixKnob.setValue(prefix)
	suffixKnob.setValue(suffix)
	addColorNameKnob.setValue(addColorToFileName)
	useOCIOKnob.setValue(useOCIO)
	n["channels"].setValue(channels)
	n["colorspace"].setValue(colorspace)
	n["file_type"].setValue(fileType)

	if useOCIOKnob:
		n["colorspace"].setEnabled(False)
		n["raw"].setEnabled(False)

	# Show/Hide knobs.
	hiddenEvalKnob.setVisible(False)

	if rootFolderMethodKnob.value() == "search word":
		rootFolderUserInputKnob.setVisible(True)
		rootFolderUserInputKnob.setLabel("search word")
		customRootFolderKnob.setVisible(False)
	elif rootFolderMethodKnob.value() == "environment variables":
		rootFolderUserInputKnob.setVisible(True)
		rootFolderUserInputKnob.setLabel("env variables/path")
		customRootFolderKnob.setVisible(False)
	elif rootFolderMethodKnob.value() == "custom path":
		rootFolderUserInputKnob.setVisible(False)
		customRootFolderKnob.setVisible(True)

	if renderNameKnob.value() == "custom name":
		customNameKnob.setVisible(True)
	else:
		customNameKnob.setVisible(False)

	for i in [mainTab, rootFolderMethodKnob, rootFolderHelpKnob, rootFolderUserInputKnob, customRootFolderKnob, div1, renderNameKnob, customNameKnob, div2, renderTypeKnob, div3, prefixKnob, suffixKnob, hiddenEvalKnob, div4, addColorNameKnob, useOCIOKnob, div5, channelsKnob, colorspaceKnob, rawKnob, fileTypeKnob, div6, renderKnob]:
		n.addKnob(i)

	# Add settings tab.
	settingsTab = nuke.Tab_Knob("sb_autoRenderSettings", "Settings")
	mainRenderFolderKnob = nuke.String_Knob("mainRenderFolder", "main render")
	precompRenderFolderKnob = nuke.String_Knob("precompRenderFolder", "precomp render")
	proxyRenderFolderKnob = nuke.String_Knob("proxyRenderFolder", "proxy render")
	framePaddingSepKnob = nuke.String_Knob("framePaddingSep", "frame padding separator")
	framePaddingKnob = nuke.String_Knob("framePadding", "frame padding")
	div7 = nuke.Text_Knob("divider7", "")
	noRenderKnob = nuke.Boolean_Knob("no_render", "no render (debugging)")

	for i in [settingsTab, mainRenderFolderKnob, precompRenderFolderKnob, proxyRenderFolderKnob, framePaddingSepKnob, framePaddingKnob, div7, noRenderKnob]:
		n.addKnob(i)

	mainRenderFolderKnob.setValue(mainRenderFolder)
	precompRenderFolderKnob.setValue(precompRenderFolder)
	proxyRenderFolderKnob.setValue(proxyRenderFolder)
	framePaddingSepKnob.setValue(framePaddingSep)
	framePaddingKnob.setValue(framePadding)

	# Focus on main tab.
	rootFolderMethodKnob.setFlag(0)

def sb_autoRender():

	n = nuke.thisNode()

	# If not a sb_autoRender node, return.
	try:
		n["sb_autoRender"]
	except:
		return

	# Make sure user variables work.
	mainRenderFolder = n["mainRenderFolder"].value()
	precompRenderFolder = n["precompRenderFolder"].value()
	proxyRenderFolder = n["proxyRenderFolder"].value()
	framePaddingSep = n["framePaddingSep"].value()
	framePadding = n["framePadding"].value()

	for i in [mainRenderFolder, precompRenderFolder, proxyRenderFolder, framePaddingSep, framePadding]:
		if not i:
			raise Exception ("Set a value to the {0} knob (Settings tab)".format( i.name() ))

	scriptPath = nuke.root()["name"].value()

	# Get the root folder path.
	rootFolderMethod = n["rootFolderMethod"].value()	

	if rootFolderMethod in ["search word", "environment variables"]:
		rootFolderUserInput = n["rootFolderUserInput"].value()
		if not rootFolderUserInput:
			raise Exception ("User input knob is not set.")

		if rootFolderMethod == "search word":
			swIndex = scriptPath.find(rootFolderUserInput)
			if swIndex == -1:
				noSwMatchMsg = "Can't find '{0}' in the current script's filepath.".format(rootFolderUserInput)
				raise Exception (noSwMatchMsg)
			else:
				rootFolderPath = scriptPath[0:swIndex]
		elif rootFolderMethod == "environment variables":
			rootFolderPath = replaceEnvsInsideBrackets(rootFolderUserInput)
	else:
		rootFolderPath = n["customRootFolderPath"].evaluate()
		if not rootFolderPath:
			raise Exception ("Custom render path knob is not set.")

	if not rootFolderPath.endswith("/"):
		rootFolderPath = "{0}/".format(rootFolderPath)

	# Get render type (main, pre, proxy).
	renderType = n["renderType"].value()

	if renderType == "main render":
		renderFolder = mainRenderFolder
	elif renderType == "precomp render":
		renderFolder = precompRenderFolder
	elif renderType == "proxy render":
		renderFolder = proxyRenderFolder
	elif renderType == "none":
		renderFolder = ""
		rootFolderPath = rootFolderPath[:-1]

	# Use "hack" to be able to evalute the knob. Useful as we then can use expressions in the prefix/suffix knobs (for example _[value channels]).
	prefix = n["prefix"].value()
	suffix = n["suffix"].value()
	evalKnob = n["hiddenEvalKnob"]

	if prefix != "":
		evalKnob.setValue(prefix)
		prefix = evalKnob.evaluate()

	if suffix != "":
		evalKnob.setValue(suffix)
		suffix = evalKnob.evaluate()

	# Colorspace.
	if n["use_ocio"].value():
		connectedNode = getNodeInput(n, 0)
		if connectedNode.Class() != "OCIOColorSpace":
			raise Exception ("Add a OCIOColorSpace node before the write node.\n\nIf you don't want to use OCIO, uncheck the 'Use OCIO for color conversions' checkbox.")
		if connectedNode["disable"].value():
			raise Exception("Enable the OCIOColorSpace node or uncheck the 'Use OCIO for color conversions' checkbox.")
		colorSpaceName = connectedNode["out_colorspace"].value().split("/")[-1]
	else:
		colorSpaceName = n["colorspace"].value()

	addColorSpaceName = n["addColorSpaceName"].value()

	# Build the folder path for the render.
	renderName = n["renderName"].value()

	if renderName == "script name":
		scriptName = os.path.splitext(scriptPath.split("/")[-1])[0]
		if addColorSpaceName:
			renderFolderPath = "{0}{1}/{2}{3}{4}_{5}/{2}{3}{4}_{5}".format(rootFolderPath, renderFolder, prefix, scriptName, suffix, colorSpaceName)
		else:
			renderFolderPath = "{0}{1}/{2}{3}{4}/{2}{3}{4}".format(rootFolderPath, renderFolder, prefix, scriptName, suffix)
	elif renderName == "custom name":
		customRenderName = n["customName"].value()
		if not customRenderName:
			customRenderNameMsg = "Custom render name knob is empty."
			raise Exception (customRenderNameMsg)
		if addColorSpaceName:
			renderFolderPath = "{0}{1}/{2}{3}{4}_{5}/{2}{3}{4}_{5}".format(rootFolderPath, renderFolder, prefix, customRenderName, suffix, colorSpaceName)
		else:
			renderFolderPath = "{0}{1}/{2}{3}{4}/{2}{3}{4}".format(rootFolderPath, renderFolder, prefix, customRenderName, suffix)

	# Build full path.
	ext = n["file_type"].value()
	if ext.lower() in ["mov", "yuv"]:
		# Skip frame-padding if rendering a movie file.
		renderPath = "{0}.{1}".format(renderFolderPath, ext)
	else:
		renderPath = "{0}{1}{2}.{3}".format(renderFolderPath, framePaddingSep, framePadding, ext)

	if n["no_render"].value():
		raise Exception ("Render path: {0}".format(renderPath))

	# Set path, create folders and continue with render.
	if nuke.root()["proxy"].value():
		n["proxy"].setValue(renderPath)
	else:
		n["file"].setValue(renderPath)
	
	sb_autoRenderCreateRenderDirs(renderPath)
	sb_autoRenderMsg = "sb AutoRender ({0}): {1}".format(n["name"].value(), renderPath)
	nuke.tprint(sb_autoRenderMsg)

def sb_autoRenderKnobChanged():

	n = nuke.thisNode()
	k = nuke.thisKnob()

	if k.name() in ["xpos", "ypos", "selected", "onCreate", "onDestroy"]:
		return

	# If not a sb_autoRender node, return.
	try:
		n["sb_autoRender"]
	except:
		return

	if k.name() == "rootFolderMethod":
		
		rfui = n["rootFolderUserInput"]
		crfp = n["customRootFolderPath"]
		
		if n["rootFolderMethod"].value() == "search word":
			rfui.setVisible(True)
			rfui.setLabel("search word")
			crfp.setVisible(False)
		elif n["rootFolderMethod"].value() == "environment variables":
			rfui.setVisible(True)
			rfui.setLabel("env variables/path")
			crfp.setVisible(False)
		elif n["rootFolderMethod"].value() == "custom path":
			rfui.setVisible(False)
			crfp.setVisible(True)

	if k.name() == "renderName":

		if n["renderName"].value() == "custom name":
			n["customName"].setVisible(True)
		else:
			n["customName"].setVisible(False)

	if k.name() == "use_ocio":

		if n["use_ocio"].value():
			n["colorspace"].setEnabled(False)
			n["raw"].setEnabled(False)
			n["raw"].setValue(True)
		else:
			n["colorspace"].setEnabled(True)
			n["raw"].setEnabled(True)
			n["raw"].setValue(False)

nuke.addKnobChanged(sb_autoRenderKnobChanged, nodeClass = "Write")
