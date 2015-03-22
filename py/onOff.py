################

"""
    sb_onOff
    Simon Bjork
    October 2012
    bjork.simon@gmail.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_onOff
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
    sb_tools.addCommand('Python/sb OnOff', 'sb_onOff.sb_onOff()', 'shift+d')

"""

################

import nuke

################

def sb_onOff():

    sn = nuke.selectedNodes()

    if len(sn) == 0:
        nuke.message("Select a node.")
        return

    frame = int(nuke.frame())

    p = nuke.Panel( "sb_onoff" )
    p.addSingleLineInput( "first frame:", "")
    p.addSingleLineInput( "last frame:", "")
    result = p.show()

    if result:

        ff = int(p.value("first frame:"))
        lf = int(p.value("last frame:"))

        for i in nuke.selectedNodes():
            m = nuke.createNode("Multiply", inpanel = False)
            m["channels"].setValue("all")
            val = m["value"]
            val.setAnimated()
            val.setValueAt(1, ff)
            val.setValueAt(1, lf)
            val.setValueAt(0, ff-1)
            val.setValueAt(0, lf+1)
            m.setInput(0, i)
            m["xpos"].setValue(i["xpos"].value())
            m["ypos"].setValue(i["ypos"].value() + 75)
            m["selected"].setValue(False)
            i["selected"].setValue(False)
