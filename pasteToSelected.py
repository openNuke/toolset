import nuke

def toggleSelection(node):
    newValue = not node['selected'].value()
    node['selected'].setValue(newValue)
    
def pasteToSelected ():
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
        toggleSelection(node)
