import nuke
from PySide import QtGui
clipboard = QtGui.QApplication.clipboard()
clipboard.setText(( nuke.filename( nuke.toNode('comp1'), nuke.REPLACE )))
nuke.nodePaste("%clipboard%")
