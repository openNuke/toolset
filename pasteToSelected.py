#author: Frank Rueter
#dateCreated: 19/02/2012
#source: http://www.nukepedia.com/python/nodegraph/pasteToSelected/ 
#licence:https://github.com/openNuke/toolkit/blob/master/LICENCE
#version:1.1
#Documentation:http://www.nukepedia.com/python/pasteToSelected
import nuke
class pasteToSelected():
    def __init__(self):
        if not nuke.selectedNodes():
            nuke.nodePaste('%clipboard%')
            return
        selection = nuke.selectedNodes()
        for self.node in selection:
            self.toggleSelection()
        for self.node in selection:
            self.node['selected'].setValue(1)
            self.nuke.nodePaste('%clipboard%')
            self.node['selected'].setValue(0)
        for self.node in selection:
            self.toggleSelection(self.node)
    
    def toggleSelection(self):
        newValue = not self.node['selected'].value()
        self.node['selected'].setValue(newValue)
    
