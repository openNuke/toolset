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
        for node in selection:
            toggleSelection(node)
        for node in selection:
            node['selected'].setValue(1)
            nuke.nodePaste('%clipboard%')
            node['selected'].setValue(0)
        for node in selection:
            self.toggleSelection(node)
    
    def toggleSelection(self.node):
        newValue = not node['selected'].value()
        node['selected'].setValue(newValue)
    
