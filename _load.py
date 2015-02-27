import PySide
from PySide import QtGui
from PySide import QtCore
import nuke, nukescripts
import os, re
import json 
import urllib2

global rootPath 
rootPath = "https://raw.githubusercontent.com/opennuke/toolkit/master/" #path must start with http

########################

class ToolSetWidget(QtGui.QWidget):
	def __init__(self,parent=None):
		global rootPath
		QtGui.QWidget.__init__(self, parent)
		self.shortCutList = []				 
		self.loadToolPane()
									
	def loadToolPane(self):
		self.toolDict = toolSetData().run().toolDict #ToDo pass this to the class before registering the pane
		self.tabs = QtGui.QTabWidget(self)
		self.scriptsTab = QtGui.QWidget()
		self.nodesTab = QtGui.QWidget()		   
		self.scriptsMainLayout = QtGui.QVBoxLayout() 
		self.nodesMainLayout = QtGui.QVBoxLayout()		 
		
		for cat in ['scripts', 'nodes']:		
			self.widgetDict = {}
			types = self.toolDict[cat].keys()
			types.sort()
			for type in types:
				if self.toolDict[cat][type]:
					groupBox = QtGui.QGroupBox(type)
					self.widgetDict[type] = {}
					columnCount = 0
					rowCount = 0
					grid = QtGui.QGridLayout()				  
					for tool in self.toolDict[cat][type]:
							button = QtGui.QPushButton(tool['label'])
							button.setToolTip(tool['tooltip'])
							grid.addWidget(button, rowCount, columnCount)					  
							buttonRunner = lambda toolPath = tool['file'], pycall = tool['pycall']: self.runTool( toolPath, pycall )
							self.connect( button, QtCore.SIGNAL( 'clicked()' ), buttonRunner )						 
							self.widgetDict[type][tool['label']] = button												 
							if columnCount == 2:
								columnCount = 0
								rowCount += 1
							else:
								columnCount += 1
					while 0 < columnCount < 3:
						grid.addWidget(QtGui.QLabel(''), rowCount, columnCount)
						columnCount += 1
					groupBox.setLayout(grid)					
				if cat == 'scripts':
					self.scriptsMainLayout.addWidget(groupBox)
					self.scriptsTab.setLayout(self.scriptsMainLayout)
				if cat == 'nodes':
					self.nodesMainLayout.addWidget(groupBox)
					self.nodesTab.setLayout(self.nodesMainLayout)
			self.tabs.addTab(self.scriptsTab, " Scripts ")
			self.tabs.addTab(self.nodesTab, " Nodes ")
		
	def runTool(self, toolPath, pycall):
		toolPath = os.path.join(rootPath, os.path.split(toolPath)[1])
		self.toolData = toolSetData().getData(toolPath).gotData
		print os.path.splitext(os.path.split(toolPath)[1])[1]
		if os.path.splitext(os.path.split(toolPath)[1])[1]==".nk":
			clipboard = QtGui.QApplication.clipboard()
			clipboard.setText(self.toolData)
			if len(nuke.selectedNodes()):	
				sn = nuke.selectedNode()
				np=nuke.nodePaste("%clipboard%")
				g=nuke.selectedNode()
				g.setInput(0, sn)
				g.setXpos(sn.xpos())
				g.setYpos(sn.ypos()+ 60)
			else:
				nuke.nodePaste("%clipboard%")
		elif os.path.splitext(os.path.split(toolPath)[1])[1]==".py":
			print self.toolData
			#exec self.toolData
			print "================"
			print pycall
			#exec pycall
			
########################				
	
class UI_enumerationSelect(nukescripts.PythonPanel):
	def __init__(self,labelChoices,title):
		self.title=title
		self.labelChoices=labelChoices
		nukescripts.PythonPanel.__init__(self, self.title)
		self.typeKnob = nuke.Enumeration_Knob('select', 'Select release', self.labelChoices)
		self.addKnob(self.typeKnob)
		
########################  
	  
class toolSetData():
	def __init__(self):
		global rootPath
		self.rootPath=rootPath
		self.toolDict={}
		
	def run(self):
		if self.licence():		  
			selectLocPath() #### Select Location of Release Path ####
			self.toolSet=getData(self.selectedLocPath).gotData() #### 
			selectToolList() #### Select selection of tools ####
			self.selectedToolList = toolSetDict[self.selectedToolList]  #### return list from selection
			makeToolDict()
	
	def selectLocPath(self):
			pLoc = UI_enumerationSelect(['web','local'], '_load.json file location?' )
			if pLoc.showModalDialog():
				selectedLocationLabel = pLoc.typeKnob.value()
				if selectedLocationLabel=='local':
					self.rootPath = os.path.split(nuke.getFilename('Select _load.json', '_load.json'))[0]
			self.selectedLocPath = os.path.join(self.rootPath, "_load.json")
			
	def selectToolList(self):
			#### Get ToolSet  Data ####
			#### Select witch release to load ###
			toolChoices=self.toolSetLists.keys()
			#for x in toolDict:
				#releaseLabelChoices.append(x['label'])
			pRelease = UI_enumerationSelect(toolChoices,'Select NukeTool selection from repository?')
			if pRelease.showModalDialog():
				self.selectedToolList = pRelease.typeKnob.value() 
				
			
			
	def makeToolDict(self):
			print selectToolSetList
			for tool in selectToolSetList:		
				#### Load Tool Selection ####
				toolsetPath = os.path.join(self.rootPath, tool+'.json')
				self.toolDict = toolSetData().getData(toolsetPath).gotData
				print '================--=====[]['
				print self.toolDict

					
	def licence(self):
		return nuke.ask("LICENCE \nBy downloading a file from this repository you agree to the general license terms below. Copyright (c) 2010 till present All rights reserved. Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. Neither the name of Nukepedia nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOO/ OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n\n Do You Agree to the above licence?")
		
	def getData(self,path):
			if path[0:4] == "http":
				try:
					response = urllib2.urlopen(path)
					print "LOADING HTTP DATA"
				except urllib2.request.URLError:
					nuke.message('errr. path to '+path+' not reached')
			else:
					response = open((path), 'r')
					print "LOADING LOCAL DATA"
			if os.path.splitext(os.path.split(path)[1])[1] == '.json':
				print "JSON FROM:"+path
				self.gotData = json.load(response)
				print self.gotData
			else:
				self.gotData = response.read()
				print "FROM:"+path
			response.close()
	  
		
########################

def runPane():
	paneExistsCheck = nuke.getPaneFor('org.vfxwiki.nuketoolkit')
	if not paneExistsCheck:
		pane = nuke.getPaneFor('Properties.1')
		nukescripts.registerWidgetAsPanel('ToolSetWidget', 'Web Tools', 'org.vfxwiki.nuketoolkit', True).addToPane(pane)
	else:
		nuke.message("errr. unable to load pane, as it already exists. \nClose the 'WebTools' pane, and try again.")

def setUpMenus():
	#Set up base menu for scripts and nodes:
	toolbar = nuke.menu("Nuke")
	menuEdit = toolbar.findItem('Edit').items()
	count=0
	for x in menuEdit:
		count=count+1	 
		if x.name() == 'Node':
			menuIndex=count
	menuTopEdit = toolbar.addMenu('Edit/Scripts', index=menuIndex)
	toolSetBar = nuke.menu("Nodes").findItem('ToolSets')
	toolSetMenu = toolSetBar.addMenu('WebTools', index=3)
	nukescripts.traversePluginPaths(toolSetMenu, False, [], True)
	
########################
		
def run(): 
 runPane()	  
run()

if 1==3:
	setUpMenus()
	
	
########################
