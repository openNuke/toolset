#rafal kaniewski
# todo mov not working
import nuke
from PySide import QtGui

def run(node):
  clipboard = QtGui.QApplication.clipboard()


  filename = node['file'].evaluate()

  filesplit =  filename.rsplit('.',-2)
  filesplit[1] = '%0'+str(len(filesplit[1]))+'d'
  filep = '.'.join(filesplit) 
  filenameFrame =  nuke.getFileNameList(os.path.dirname(filep))[0].rsplit(' ',-1)[1]

  clipboard.setText(( filep+" "+filenameFrame))
  nuke.nodePaste("%clipboard%")
  
  #run(nuke.selectedNode())
