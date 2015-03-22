################

"""

    sb_bakeWorldPosition
    Simon Bjork
    February 2014
    Version 1.0
    bjork.simon@gmail.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_bakeWorldPosition
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
    sb_tools.addCommand("Python/sb BakeWorldPosition", 'sb_bakeWorldPosition.sb_bakeWorldPosition()', '')

"""

################

import nuke
import _nukemath
import math

################

def getWorldPosition(frame, node, rotationOrder):

    # Based on Ivan Busquets consolidateNodeTransforms() function.
    # This function will convert matrix values to position, rotation, scale values.

    matrixList = node["world_matrix"].valueAt(frame)

    # Reorder list and put it into a matrix.
    order = [0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15]

    matrix = _nukemath.Matrix4()

    for i in range(16):
        matrix[i] = matrixList[ order[i] ]

    posMatrix = _nukemath.Matrix4(matrix)
    posMatrix.translationOnly()
    rotMatrix = _nukemath.Matrix4(matrix)
    rotMatrix.rotationOnly()
    scaleMatrix = _nukemath.Matrix4(matrix)
    scaleMatrix.scaleOnly()

    position = [ float(posMatrix[12]), float(posMatrix[13]), float(posMatrix[14]) ]

    if rotationOrder == "XYZ":
        rotations = rotMatrix.rotationsXYZ()
    elif rotationOrder == "XZY":
        rotations = rotMatrix.rotationsXZY()
    elif rotationOrder == "YXZ":
        rotations = rotMatrix.rotationsYXZ()
    elif rotationOrder == "YZX":
        rotations = rotMatrix.rotationsYZX()
    elif rotationOrder == "ZXY":
        rotations = rotMatrix.rotationsZXY()
    elif rotationOrder == "ZYX":
        rotations = rotMatrix.rotationsZYX()
    else:
        rotations = rotMatrix.rotationsZXY()

    rotation = [math.degrees(rotations[0]), math.degrees(rotations[1]), math.degrees(rotations[2])]

    scale = [scaleMatrix.xAxis().x, scaleMatrix.yAxis().y, scaleMatrix.zAxis().z]

    return [position, rotation, scale]

def duplicateNode(srcNode, destNode, skipKnobList):

    errorKnobs = []

    for i in srcNode.knobs():
        if i in skipKnobList + ["name", "xpos", "ypos"]:
            continue

        try:
            destNode[i].fromScript(srcNode[i].toScript())
        except NameError:
            errorKnobs.append(i)

    if len(errorKnobs) > 0:
        errorStr = "\n".join(errorKnobs)
        print "The following knobs could not be copied:\n\n{0}".format(errorStr)

def sb_bakeWorldPosition():

    
    nodes = []

    for i in nuke.selectedNodes():
        if i.Class() in ["Axis", "Axis2", "Camera", "Camera2", "Light", "Light2"]:
            nodes.append(i)


    if len(nodes) == 0:
        nuke.message("Select a Camera, Axis or Light node.")
        return

    p = nuke.Panel( "sb_BakeWorldPosition" )
    p.addEnumerationPulldown('Rotation order:', 'Current XYZ XZY YXZ YZX ZXY ZYX')
    p.addSingleLineInput( "First frame:", nuke.root().firstFrame() )
    p.addSingleLineInput( "Last frame:", nuke.root().lastFrame() )
    result = p.show()

    if not result:
        return

    try:
        ff = int(p.value("First frame:"))
        lf = int(p.value("Last frame:"))
    except:
        nuke.message("Set a correct frame range.")
        return

    baked = []

    for i in nodes:

        i["selected"].setValue(False)
        
        n = nuke.createNode(i.Class(), inpanel = False)
        n["name"].setValue("{0}_{1}".format(i["name"].value(), "BAKED"))
        n["xpos"].setValue(i["xpos"].value())
        n["ypos"].setValue(i["ypos"].value() + 100)
        n.setInput(0, None)

        duplicateNode(i, n, ["translate", "rotate", "scaling", "uniform_scale", "skew", "pivot", "useMatrix", "matrix", "world_matrix"])

        selRotationOrder = p.value('Rotation order:')

        if selRotationOrder == "Current":
            n["rot_order"].setValue(i["rot_order"].value())
        else:
            n["rot_order"].setValue(selRotationOrder)

        for j in ["translate", "rotate", "scaling"]:
            n[j].setAnimated()

        # Setup progress bar.
        task = nuke.ProgressTask('Baking keyframes...')
        progressCalc = 100.0/float(lf-ff)
        counter = 0

        for k in range(ff,lf+1):

            if task.isCancelled(): 
                print "Cancelled by user."
                return
            
            pos, rot, scale = getWorldPosition(k, i, selRotationOrder)

            for l in range(3):
                n["translate"].setValueAt(pos[l], k, l)
                n["rotate"].setValueAt(rot[l], k, l)
                n["scaling"].setValueAt(scale[l], k, l)

            # Update progressbar.
            task.setProgress(int(counter*progressCalc))
            task.setMessage("Frame {0}".format(k))
            counter +=1

        del task

        baked.append(i["name"].value())

    bakedStr = "\n".join(baked)
    print "The following nodes were successfully baked:\n\n{0}".format(bakedStr)
