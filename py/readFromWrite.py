import nuke
from PySide import QtGui
clipboard = QtGui.QApplication.clipboard()

node = nuke.selectedNode()
filename = node['file'].evaluate()

filesplit =  filename.rsplit('.',-2)
filesplit[1] = '%0'+str(len(filesplit[1]))+'d'
filep = '.'.join(filesplit) 
filenameFrame =  nuke.getFileNameList(os.path.dirname(filep))[0].rsplit(' ',-1)[1]

clipboard.setText(( filep+" "+filenameFrame))
nuke.nodePaste("%clipboard%")
