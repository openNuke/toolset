################

"""
    sb_convertTracker
    Simon Bjork
    April 2014
    simon@bjorkvisuals.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_convertTracker
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
    sb_tools.addCommand('Python/sb ConvertTracker', 'sb_convertTracker.sb_convertTracker()', "")

"""

################

import nuke
import nukescripts
import nuke.rotopaint as rp
import threading

################


def sb_convertTracker_Data():

    data = {}
    data["scriptName"] = "sb_convertTracker"
    data["scriptVersion"] = "1.0"

    return data

def getTrackerNames(node):

    '''
    # Returns a list with the names of all tracks in the node.
    # Can also be used to get the number of tracks available, by checking the length of the returned list.

    '''

    n = node["tracks"].toScript()
    rows = n.split("\n")[34:]

    trackers = []

    for i in rows:
        try:
            # Fancy, ey...
            trkName = i.split("}")[1].split("{")[0][2:-2]
            if trkName != "":
                trackers.append(trkName)
        except:
            continue

    return trackers

def getTrackerValueAtFrame(node, trackIndex, frame):

    ''' 
    # Returns x, y values of a track.
    
    '''
    numColumns = 31

    x = node["tracks"].getValueAt(frame, numColumns*trackIndex + 2)
    y = node["tracks"].getValueAt(frame, numColumns*trackIndex + 3)

    return [x, y]

def getMatrixFromTracker(node, trackIndexList, frame, refFrame):

    '''
    # Returns a matrix based on four tracks.

    '''

    if node.Class() != "Tracker4" or len(trackIndexList) != 4:
        return False
    
    projectionMatrixTo = nuke.math.Matrix4()
    projectionMatrixFrom = nuke.math.Matrix4()

    toValues = []
    fromValues = []

    numColumns = 31

    for i in range( 0, len(trackIndexList) ):
        for j in range(2):
            toVal = node["tracks"].getValueAt(frame, numColumns*trackIndexList[i] + (2+j))
            fromVal = node["tracks"].getValueAt(refFrame, numColumns*trackIndexList[i] + (2+j))

            toValues.append(toVal)
            fromValues.append(fromVal)

    projectionMatrixTo.mapUnitSquareToQuad(toValues[0], toValues[1], toValues[2], toValues[3], toValues[4], toValues[5], toValues[6], toValues[7])
    projectionMatrixFrom.mapUnitSquareToQuad(fromValues[0], fromValues[1], fromValues[2], fromValues[3], fromValues[4], fromValues[5], fromValues[6], fromValues[7])

    matrix = projectionMatrixTo*projectionMatrixFrom.inverse()    
    matrix.transpose()

    return matrix

class sb_convertTracker_Panel(nukescripts.PythonPanel):

    def __init__(self):

        scriptData = sb_convertTracker_Data()
        nukescripts.PythonPanel.__init__(self, '{0} v{1}'.format(scriptData["scriptName"], scriptData["scriptVersion"]))

        trackerList = getTrackerNames(nuke.selectedNode())

        self.bl = nuke.Enumeration_Knob("bl", "bottom left", trackerList)
        self.br = nuke.Enumeration_Knob("br", "bottom right", trackerList)
        self.ur = nuke.Enumeration_Knob("ur", "upper right", trackerList)
        self.ul = nuke.Enumeration_Knob("ul", "upper left", trackerList)
        self.div1 = nuke.Text_Knob("divider1", "")
        self.ff = nuke.Int_Knob("ff", "first frame")
        self.lf = nuke.Int_Knob("lf", "last frame")
        self.ref = nuke.Int_Knob("rf", "reference frame")
        self.stf = nuke.PyScript_Knob('stf', "Set frame")
        self.div2 = nuke.Text_Knob("divider2", "")
        self.output = nuke.Enumeration_Knob("output", "output", ["CornerPin Match-move (Plane)", "CornerPin Stabilize (Plane)", "CornerPin Match-move (Distort)", "CornerPin Stabilize (Distort)", "RotoPaint", "SplineWarp", "GridWarp"])
        self.div3 = nuke.Text_Knob("divider3", "")
        self.createBtn = nuke.PyScript_Knob("createBtn", "create node")

        for i in [ self.output, self.div1, self.bl, self.br, self.ur, self.ul, self.div2, self.ff, self.lf, self.ref, self.stf, self.div3, self.createBtn]:
            self.addKnob(i)

        # Set values.
        self.bl.setValue(0)
        self.br.setValue(1)
        self.ur.setValue(2)
        self.ul.setValue(3)

        self.ff.setValue( int( nuke.root()["first_frame"].value() ) )
        self.lf.setValue( int( nuke.root()["last_frame"].value() ) )
        self.ref.setValue( int( nuke.root()["frame"].value() ) )

    # Set knobChanged commands.
    def knobChanged(self, knob):
        
        if knob is self.createBtn:
            self.createNode()

        elif knob is self.output:
            if self.output.value() == "CornerPin Match-move (Distort)" or self.output.value() == "CornerPin Stabilize (Distort)":
                self.ref.setEnabled(False)
            else:
                self.ref.setEnabled(True)

        elif knob is self.stf:
            self.ref.setValue( int( nuke.root()["frame"].value() ) )

    def createNode(self):

        # Do some error checking, making sure the node is still selected.
        try:
            node = nuke.selectedNode()
            n = node["tracks"]
        except ValueError:
            nuke.message("Select a tracker node.")
            return

        if self.bl.numValues() < 4:
            nuke.message("The script requires at least four tracks in the select node.")
            return

        node["selected"].setValue(False)

        # Setup variables.
        ff = self.ff.value()
        lf = self.lf.value()
        ref = self.ref.value()
        output = self.output.value()

        blIndex = int(self.bl.getValue())
        brIndex = int(self.br.getValue())
        urIndex = int(self.ur.getValue())
        ulIndex = int(self.ul.getValue())

        # Create nodes.
        if output in ["CornerPin Match-move (Plane)", "CornerPin Stabilize (Plane)", "CornerPin Match-move (Distort)", "CornerPin Stabilize (Distort)"]:

            c = nuke.createNode("CornerPin2D")

            if output == "CornerPin Match-move (Plane)" or output == "CornerPin Match-move (Distort)":
                cornerPinMain = "to"
                cornerPinRef = "from"
            else:
                cornerPinMain = "from"
                cornerPinRef = "to"

            main1 = "{0}1".format(cornerPinMain)
            main2 = "{0}2".format(cornerPinMain)
            main3 = "{0}3".format(cornerPinMain)
            main4 = "{0}4".format(cornerPinMain)

            for i in [main1, main2, main3, main4]:
                c[i].setAnimated()

            for i in range(ff, lf+1):
                for j in range(2):
                    c[main1].setValueAt(getTrackerValueAtFrame(node, blIndex, i)[j], i, j)
                    c[main2].setValueAt(getTrackerValueAtFrame(node, brIndex, i)[j], i, j)
                    c[main3].setValueAt(getTrackerValueAtFrame(node, urIndex, i)[j], i, j)
                    c[main4].setValueAt(getTrackerValueAtFrame(node, ulIndex, i)[j], i, j)

            if output == "CornerPin Match-move (Plane)" or output == "CornerPin Stabilize (Plane)":

                # Add reference frame.
                tab = nuke.Tab_Knob("ref", "Reference frame")
                c.addKnob(tab)
                rf = nuke.Int_Knob("rf")
                c.addKnob(rf)
                rf.setLabel("Reference frame")
                c["rf"].setValue(ref)
                stf = nuke.PyScript_Knob('stf')
                stf.setLabel("Set to this frame")
                c.addKnob(stf)
                stf.setCommand( 'nuke.thisNode()["rf"].setValue(nuke.frame())' )

                c["{0}1".format(cornerPinRef)].setExpression("{0}(rf)".format(main1))
                c["{0}2".format(cornerPinRef)].setExpression("{0}(rf)".format(main2))
                c["{0}3".format(cornerPinRef)].setExpression("{0}(rf)".format(main3))
                c["{0}4".format(cornerPinRef)].setExpression("{0}(rf)".format(main4))

                c["label"].setValue("reference frame: [value rf]")

            # Focus on main tab.
            c["to1"].setFlag(0)

        elif output == "RotoPaint" or output == "SplineWarp":

            if output == "RotoPaint":
                c = nuke.createNode("RotoPaint")
            else:
                c = nuke.createNode("SplineWarp3")

            curve = c['curves']
            root = curve.rootLayer
            newLayer = rp.Layer(curve)
            name = "tracked layer"
            newLayer.name = name
            root.append(newLayer)
            curve.changed()
            layer = curve.toElement(name)
            transform = layer.getTransform()

            for i in range(ff, lf+1):
                matrix = getMatrixFromTracker(node, [blIndex,brIndex,urIndex,ulIndex], i, ref)
                for j in range(16):
                    extraMatrixKnob = transform.getExtraMatrixAnimCurve(0,j)
                    extraMatrixKnob.addKey(i,matrix[j])

            c["label"].setValue("reference frame: {0}".format(ref))

        elif output == "GridWarp":

            c = nuke.createNode("GridWarp3")
            c["source_grid_transform_matrix"].setAnimated()

            # Setup progress bar.
            task = nuke.ProgressTask('Adding keyframes...')
            progressCalc = 100.0/float(lf-ff)
            counter = 0

            for i in range(ff, lf+1):
                
                matrix = getMatrixFromTracker(node, [blIndex,brIndex,urIndex,ulIndex], i, ref)
                
                for j in range(16):
                    c["source_grid_transform_matrix"].setValueAt(matrix[j], i, j,)

                if task.isCancelled(): 
                    print "Cancelled by user."
                    break

                # Update progressbar.
                task.setProgress(int(counter*progressCalc))
                task.setMessage("Frame {0}".format(i))
                counter +=1

            del task

            c["label"].setValue("reference frame: {0}".format(ref))

        # Setup node.
        c["xpos"].setValue(node["xpos"].value()+50)
        c["ypos"].setValue(node["ypos"].value()+50)
        c["selected"].setValue(False)
        c.setInput(0, None)

# Run main script.
def sb_convertTracker():

    try:
        selNode = nuke.selectedNode()
    except ValueError:
        nuke.message("Select a tracker node.")
        return

    if selNode.Class() != "Tracker4":
        nuke.message("Select a tracker node.")
        return

    sb_convertTracker_Panel().show()
