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

class toolSetWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        global rootPath
        self.rootPath = rootPath
        QtGui.QWidget.__init__(self, parent)
        self.shortCutList = []                 
        self.loadToolPane()
                                    
    def loadToolPane(self):
        self.toolsDict = toolSetData().toolsDict #ToDo pass this to the class before registering the pane
        self.tabs = QtGui.QTabWidget(self)
        self.scriptsTab = QtGui.QWidget()
        self.nodesTab = QtGui.QWidget()  
        self.scroll= QtGui.QScrollArea(self)
        self.scriptsMainLayout = QtGui.QVBoxLayout()    
        
        self.nodesMainLayout = QtGui.QVBoxLayout()         
        for cat in ['nodes', 'python' ]: 
            self.widgetDict = {}
            types = self.toolsDict[cat].keys()
            types.sort()
            for type in types:
                if self.toolsDict[cat][type]:
                    groupBox = QtGui.QGroupBox(type)
                    self.widgetDict[type] = {}
                    columnCount = 0
                    rowCount = 0
                    grid = QtGui.QGridLayout()   
                    for tool in self.toolsDict[cat][type]:
                        ## If tool has 'label list then it has multiple buttons with different calls ##
                        if isinstance(tool['label'], list) :
                            stepRange = len(tool['label'])
                            toolLabel = tool['label']
                            toolCall = tool['call']
                        else:
                             stepRange = 1 
                             toolLabel = [tool['label']]
                             toolCall = [tool['call']]
                        for x in range(0,stepRange) :  
                                    button = QtGui.QPushButton(toolLabel[x])
                                    button.setToolTip(tool['tooltip'])
                                    grid.addWidget(button, rowCount, columnCount)                      
                                    buttonRunner = lambda toolPath = tool['file'], call = toolCall[x]: self.runTool( toolPath, call )
                                    self.connect( button, QtCore.SIGNAL( 'clicked()' ), buttonRunner )                         
                                    self.widgetDict[type][toolLabel[x]] = button                                                 
                                    if columnCount == 2:
                                        columnCount = 0
                                        rowCount += 1
                                    else:
                                        columnCount += 1
                        while 0 < columnCount < 3:
                                grid.addWidget(QtGui.QLabel(''), rowCount, columnCount)
                                columnCount += 1
                        print "button added: "+tool['file']
                    groupBox.setLayout(grid)                    
                if cat == 'python':
                    self.scriptsMainLayout.addWidget(groupBox)
                    
                    self.scroll.setWidget(groupBox)
                    self.scroll.setWidgetResizable(True)
                    self.scroll.setFixedWidth(400)
                    self.scriptsMainLayout  = QtGui.QVBoxLayout(self)
                    self.scriptsMainLayout .addWidget(self.scroll)
        
                    self.scriptsTab.setLayout(self.scriptsMainLayout)
                if cat == 'nodes':
                    self.nodesMainLayout.addWidget(groupBox)
                    self.nodesTab.setLayout(self.nodesMainLayout)
            self.tabs.addTab(self.scriptsTab, " Python ")
            self.tabs.addTab(self.nodesTab, " Nodes ")
        
    def runTool(self, toolPath, call):
        toolPath = os.path.join(rootPath, os.path.split(toolPath)[1])
        self.toolData = getData(toolPath).gotData
        if os.path.splitext(os.path.split(toolPath)[1])[1]==".nk":
            print os.path.splitext(os.path.split(toolPath)[1])[1]
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
            print call
            #code_obj = compile(self.toolData,  '<string>, 'exec')
            #exec(code_obj) in globals(), locals()
            #exec(call)
            exec(self.toolData+'\n'+call)
            
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
        self.rootPath = rootPath
        self.toolsDict={}
        ## Select Location of Release Path ##
        if self.licence():          
            ## Get Release Path  Dict ##
            self.toolLoadJsonDict = getData(os.path.join(self.rootPath, "_load.json")).gotData
            selectedToolList=[]
            selectedToolList = self.toolLoadJsonDict[self.selectToolList()]
            ## load self.toolDict and add to self.toolsDict ##
            for toolName in selectedToolList:
                print "json: "+toolName
                self.toolDict = getData(os.path.join(self.rootPath, toolName +'.json')).gotData
                self.addToolDict()
                
            
    def selectToolList(self):
            #### Select witch release to load ###
            toolChoices=self.toolLoadJsonDict.keys()
            pRelease = UI_enumerationSelect(toolChoices,'Select NukeTool selection from repository?')
            if pRelease.showModalDialog():
                self.selectedToolListName = pRelease.typeKnob.value() 
            return self.selectedToolListName
                                        
    def addToolDict(self): 
            ## load self.toolDict and add to self.toolsDict ##
            toolType = self.toolDict['type']
            category= self.toolDict['category']
            label = self.toolDict['label']
            file = self.toolDict['file']
            tooltip = self.toolDict['tooltip']
            originalAuthor = self.toolDict['originalAuthor']
            dateCreated = self.toolDict['dateCreated']
            status = self.toolDict['status']
            documentation = self.toolDict['documentation']
            source = self.toolDict['source']
            call = self.toolDict['call']
            ## HACK - tehre must be a cleaner way of doing this? ##
            ## Check if [toolType][category] exsits and if save so old 'toolList and extend with new tool ##
            if toolType in self.toolsDict:
                if category in self.toolsDict[toolType]:
                    toolList=self.toolsDict[toolType][category]
                else:
                    toolList=[] 
            else:
                toolList=[]
            toolList.extend([{'call':call,'file':file,'label':label,'tooltip':tooltip,'originalAuthor':originalAuthor,'dateCreated':dateCreated,'status':status,'source':source}])
            ## if [toolType][category] exists then add rather than replace ##
            if toolType in self.toolsDict.keys():
                    self.toolsDict[toolType].update({category:[]})
            else:
                    self.toolsDict.update({toolType:{category:[]}})    
            ## Add the toolList
            self.toolsDict[toolType][category] = self.toolsDict[toolType][category]+toolList
                    
    def licence(self):
        return nuke.ask(getData(os.path.join(self.rootPath, "LICENCE")).gotData)
########################
class isRootPathLocal():
    def __init__(self):
            global rootPath
            pLoc = UI_enumerationSelect(['web','local'], '_load.json file location?' )
            if pLoc.showModalDialog():
                selectedLocationLabel = pLoc.typeKnob.value()
            if selectedLocationLabel=='local':
                rootPath = os.path.split(nuke.getFilename('Select _load.json', '_load.json'))[0]
########################
class getData():
    def __init__(self,path):
        if path[0:4] == "http":
            try:
                response = urllib2.urlopen(path)
            except urllib2.request.URLError:
                nuke.message('errr. path to '+path+' not reached')
        else:
            response = open((path), 'r')
        if os.path.splitext(os.path.split(path)[1])[1] == '.json':
            self.gotData = json.load(response)
        else:
            self.gotData = response.read()
        response.close()
########################
      

def runPane():
    paneExistsCheck = nuke.getPaneFor('org.vfxwiki.nuketoolkit')
    if not paneExistsCheck:
        pane = nuke.getPaneFor('Properties.1')
        nukescripts.registerWidgetAsPanel('toolSetWidget', 'openNuke', 'org.vfxwiki.nuketoolkit', True).addToPane(pane)
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
 isRootPathLocal()    ## set the 'global rootPath'
 runPane()    ## create the panel running the ToolSetWidget() to load toolSetData()
run()

if 1==3:
    setUpMenus()
    
    
########################
