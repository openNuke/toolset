####################

"""
    sb_autoAddGizmos
    Simon Bjork
    May 2013
    bjork.simon@gmail.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_autoAddGizmos
    sb_autoAddGizmos.sb_autoAddGizmos("D:/tools/nuke/simon/gizmos/", "Gizmos", "GizmosIcon.png")

    # Adds gizmos from a specified folder to a menu.
    # The icon path is not requied.
    # The menu can be an already exsisting menu.
    # Make sure the gizmo path also exist in your Nuke environment.

"""

####################

import os
import nuke

################

def sb_autoAddGizmos(gizmoPath, menuName, subMenuName = "", mainIcon = "", subIcon = ""):

    if not os.path.exists(gizmoPath):
        return

    # Get supported luts.
    allFiles = nuke.getFileNameList(gizmoPath)
    gizmos = []
    for i in allFiles:
        if i.endswith(".gizmo"):
            gizmos.append(i)
    
    if len(gizmos) == 0:
        print "sb_autoAddGizmos: No gizmos found."
        return

    t = nuke.toolbar("Nodes")
    customMenu = t.findItem(menuName)

    if not customMenu:
        customMenu = t.addMenu(menuName, icon = mainIcon)

    if subMenuName:
        customMenu = customMenu.addMenu(subMenuName, icon = subIcon)

    for i in sorted(gizmos):
        gizmoName = os.path.splitext(i)[0].strip()
        gizmoNameFix = gizmoName.replace("_", " ")
        customMenu.addCommand(gizmoNameFix, "nuke.createNode(\"" + gizmoName +"\")")
