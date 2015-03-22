################

"""
    sb_dagPosition
    Simon Bjork
    Version 1.0
    September 2014
    bjork.simon@gmail.com

    Synopsis: Save/Load DAG positions. Simpler (and quicker) version of the built-in bookmark function. Support for maximum 10 positions.
    OS: Windows/OSX/Linux

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_dagPosition
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )

    sb_tools.addCommand("Python/sb DAGPosition/sb LoadDAGPosition1", 'sb_dagPosition.sb_loadDagPosition(1)', 'F1')
    sb_tools.addCommand("Python/sb DAGPosition/sb LoadDAGPosition2", 'sb_dagPosition.sb_loadDagPosition(2)', 'F2')
    sb_tools.addCommand("Python/sb DAGPosition/sb LoadDAGPosition3", 'sb_dagPosition.sb_loadDagPosition(3)', 'F3')
    sb_tools.addCommand("Python/sb DAGPosition/sb LoadDAGPosition4", 'sb_dagPosition.sb_loadDagPosition(4)', 'F4')
    sb_tools.addCommand("Python/sb DAGPosition/sb LoadDAGPosition5", 'sb_dagPosition.sb_loadDagPosition(5)', 'F5')

    sb_tools.addCommand("Python/sb DAGPosition/sb SaveDAGPosition1", 'sb_dagPosition.sb_saveDagPosition(1)', 'shift+F1')
    sb_tools.addCommand("Python/sb DAGPosition/sb SaveDAGPosition2", 'sb_dagPosition.sb_saveDagPosition(2)', 'shift+F2')
    sb_tools.addCommand("Python/sb DAGPosition/sb SaveDAGPosition3", 'sb_dagPosition.sb_saveDagPosition(3)', 'shift+F3')
    sb_tools.addCommand("Python/sb DAGPosition/sb SaveDAGPosition4", 'sb_dagPosition.sb_saveDagPosition(4)', 'shift+F4')
    sb_tools.addCommand("Python/sb DAGPosition/sb SaveDAGPosition5", 'sb_dagPosition.sb_saveDagPosition(5)', 'shift+F5')

"""
################

import nuke

################

def sb_saveDagPosition(num):

    ''' Save DAG position in a text knob (Root node).'''

    if num<1 or num>10:
        nuke.message("Currently support for position 1-10.")
        return

    try:
        n = nuke.selectedNodes()[0]
    except IndexError:
        nuke.message("Select a node.")
        return

    zoom = nuke.zoom()
    xpos = n["xpos"].value()
    ypos = n["ypos"].value()

    try:
        dagKnob = nuke.root()["sb_dagPosition"]
    except NameError:
        conf = nuke.ask("sb DAGPosition needs to save position data in the Root node. Click Yes to continue.\n\nNote: This dialog will only pop up the first time you save a position.")
        if not conf:
            return

        dagKnob = nuke.String_Knob("sb_dagPosition", "sb DAGPosition")
        nuke.root().addKnob(dagKnob)
        dagKnob.setValue("0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0")
        dagKnob.setFlag(nuke.STARTLINE)
        dagKnob.setEnabled(False)
        nuke.root()["name"].setFlag(0)

    try:
        dagValues = dagKnob.value().split(";")
        dagValues.pop(num-1)
        newVal = ",".join( [str(zoom), str(xpos), str(ypos)] )
        dagValues.insert(num-1, newVal)
        dagKnob.setValue(";".join(dagValues))
    except Exception as e:
        nuke.message("sb DAGPosition couldn't save position values.\n\nERROR: {0}.".format(e))
        return False

def sb_loadDagPosition(num):

    ''' Read value from knob and focus DAG. '''

    if num<1 or num>10:
        nuke.message("Currently support for position 1-10.")
        return

    try:
        dagKnob = nuke.root()["sb_dagPosition"]
        dagPosValues = dagKnob.value().split(";")[num-1]
        zoom, xpos, ypos = dagPosValues.split(",")
        nuke.zoom(float(zoom), [float(xpos), float(ypos)])
    except Exception as e:
        nuke.message("sb DAGPosition couldn't load position values.\n\nERROR: {0}.".format(e))
