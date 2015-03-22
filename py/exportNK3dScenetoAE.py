################

"""

    sb_exportNukeSceneToAE
    Simon Bjork
    February 2014
    Version 1.0
    bjork.simon@gmail.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_exportNukeSceneToAE
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
    sb_tools.addCommand("Python/sb ExportNukeSceneToAE", 'sb_exportNukeSceneToAE.sb_exportNukeSceneToAE()', '')

"""

################

import nuke
import nukescripts
import os
import math

################

def sb_exportNukeSceneToAE_version():
    version = 1.0
    return version

def sb_exportNukeSceneToAE_info():

    return ("Nuke scene exported with sb_exportNukeSceneToAE.py.\n"
            "Import scene to After Effects using sb_importNukeScene.jsx.\n"
            "Rotation order has been converted to ZYX (After Effects)\n"
            "Render aspect ratio has been converted to square pixels (if needed).\n"
            "Download scripts at www.bjorkvisuals.com.")

def sb_exportNukeSceneToAE_help():

    return ("sb_exportNukeSceneToAE {0}\n"
            "Copyright (c) 2014 Simon Bjork\n"
            "www.bjorkvisuals.com\n\n"
            "This script exports the selected 3d nodes for use in Adobe After Effects.\n\n"
            "To import the scene into After Effects use sb_importNukeScene.jsx.\n\n"
            "Currently the script supports Camera, Card and Axis nodes. Unfortunately there is no support for TransformGeo nodes.\n\n"
            "The script exports the world position of objects, which means that it will work properly with parenting chains (for example a Camera connected to an Axis). You only need to select the final object in the parenting chain.\n\n"
            "It's important to make sure that you set the correct format before exporting. This is the render resolution of your 3d scene (bg input of ScanlineRenderer). In most cases this is the project format, but there are cases where you want to render your 3d scene into a different format.\n\n"
            "To use the script, select all 3d nodes you want to export, set a file path (.txt), set render format, set the first and last frame and click export camera.\n\n"
            "If you have any questions, bug reports or feature requests, contact me at bjork.simon@gmail.com.").format(sb_exportNukeSceneToAE_version())

def convertMatrixToPosRotScale(node, frame, rotationOrder = "ZXY"):

    # This function is completely based on Ivan Busquets consolidateNodeTransforms() and Ean Carrs consolidateAnimatedNodeTransforms().
    # This function will convert matrix values to position, rotation, scale values.
    # It will return the following list: posX, posY, posZ, rotX, rotY, rotZ, scaleX, scaleY, scaleZ
    # Currently supports ZXY and ZYX rotation order (Nuke and After Effects)

    supported_rotations = ["ZXY", "ZYX"]
    if not rotationOrder in supported_rotations:
        print "This function currently supports ZXY and ZYX rotation order (Nuke and After Effects)."
        return False

    m = nuke.math.Matrix4()

    if node.Class() == "Card" or node.Class() == "Card2":
        k = node["matrix"]
    else:
        k = node["world_matrix"]

    k_time_aware = k.getValueAt(frame)

    for y in range(k.height()):
        for x in range(k.width()):
            m[x+(y*k.width())] = k_time_aware[y + k.width()*x]

    transM =nuke.math.Matrix4(m)
    transM.translationOnly()
    rotM = nuke.math.Matrix4(m)
    rotM.rotationOnly()
    scaleM = nuke.math.Matrix4(m)
    scaleM.scaleOnly()

    posX = transM[12]
    posY = transM[13]
    posZ = transM[14]

    if rotationOrder == "ZXY":
        rotations = rotM.rotationsZXY()
    elif rotationOrder == "ZYX":
        rotations = rotM.rotationsZYX()
    rotX = math.degrees(rotations[0])
    rotY = math.degrees(rotations[1])
    rotZ = math.degrees(rotations[2])

    scaleX = scaleM.xAxis().x
    scaleY = scaleM.yAxis().y
    scaleZ = scaleM.zAxis().z

    return [posX, posY, posZ, rotX, rotY, rotZ, scaleX, scaleY, scaleZ]

def checkIfAnimated(node):
    animated = False
    for i in node.knobs():
        if node[i].isAnimated():
            animated = True
            break
    return animated

# Build the UI.
class sb_exportNukeSceneToAE_Panel(nukescripts.PythonPanel):

    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'sb_exportNukeSceneToAE v{0}'.format(sb_exportNukeSceneToAE_version()))
        self.file = nuke.File_Knob("file_path", "file path")
        self.format = nuke.Format_Knob("format,", "render format")
        self.ff = nuke.Int_Knob("ff", "first frame")
        self.lf = nuke.Int_Knob("lf", "last frame")
        self.div1 = nuke.Text_Knob("divider1", "")
        self.help = nuke.PyScript_Knob("help", "?")
        self.div2 = nuke.Text_Knob("divider2", "")
        self.export_objects = nuke.PyScript_Knob("export_objects", "export objects")

        for i in [self.file, self.format, self.ff, self.lf, self.div1, self.help, self.div2, self.export_objects]:
            self.addKnob(i)

        # Set values to knobs
        self.ff.setValue(int(nuke.root()["first_frame"].value()))
        self.lf.setValue(int(nuke.root()["last_frame"].value()))

    # Set knobChanged commands.
    def knobChanged(self, knob):
        if knob is self.export_objects:
            self.write_scene_data()
        elif knob is self.help:
            nuke.message(sb_exportNukeSceneToAE_help())

    # Main function.
    def write_scene_data(self):

        # Need Nuke 7.0 to run script (rotation order conversion).
        if int(nuke.NUKE_VERSION_MAJOR) < 7:
            nuke.message("You need to use Nuke 7.0 (or newer) in order to run this script.")
            return

        # Get data from panel.
        file_path = self.file.value()
        render_width = self.format.value().width()
        render_height = self.format.value().height()
        render_par = self.format.value().pixelAspect()
        first_frame = self.ff.value()
        last_frame = self.lf.value()

        # Set folder path.
        if file_path == "":
            nuke.message("Set a file path.")
            return

        no_ext, ext = os.path.splitext(file_path)

        if not ext == ".txt":
            file_path ="{0}.txt".format(file_path)

        # Makes sure supported nodes are selected.
        sn = nuke.selectedNodes()
        accepted_nodes = []

        accepted_classes = ["Camera", "Camera2", "Card", "Card2", "Axis", "Axis2"]
        for i in sn:
            if i.Class() in accepted_classes:
                accepted_nodes.append(i)

        if len(accepted_nodes) == 0:
            nuke.message("Select a Camera, Card or Axis node.")
            return

        # Make sure no cameras are scaled.
        scaled_cameras = []

        for i in accepted_nodes:
            if i.Class() == "Camera" or i.Class() == "Camera2":
                if i["scaling"].notDefault() == True or i["uniform_scale"].notDefault() == True:
                    scaled_cameras.append(i)

        if len(scaled_cameras) > 0:
            unsupported_scale = ""
            for i in scaled_cameras:
                unsupported_scale = "{0}{1}\n".format(unsupported_scale, i["name"].value())
            nuke.message("Scaled cameras are not supported by After Effects. The following cameras are scaled: \n\n{0}".format (unsupported_scale.strip())) 
            return

        # Make sure no objects are scewed.
        skewed_objects = []

        for i in accepted_nodes:
            if i["skew"].notDefault() == True:
                skewed_objects.append(i)

        if len(skewed_objects) > 0:
            unsupported_skew = ""
            for i in skewed_objects:
                unsupported_skew = "{0}{1}\n".format(unsupported_skew, i["name"].value())
            nuke.message( "Skewed obects are not supported by After Effects. The following nodes are skewed: \n\n{0}".format (unsupported_skew.strip()))
            return

        # Convert render resolution to square pixels.
        render_width = int(round(render_width*render_par))
        render_par = 1

        # Try to write the file.
        try:

            # Open the text file.
            with open(file_path, 'w') as theFile:

                # Set the number and type of divider characters.
                divider = "#"*100

                # Scene data.
                nk = "Scene Nuke script:\t{0}".format(nuke.root()["name"].value())
                proj_width = "Scene project width:\t{0}".format(nuke.root()["format"].value().width())
                width = "Scene width:\t{0}".format(render_width)
                height = "Scene height:\t{0}".format(render_height)
                par = "Scene pixel aspect ratio:\t{0}".format(render_par)
                fps = "Scene frame rate:\t{0}".format(int(nuke.root()["fps"].value()))
                ff = "Scene first frame:\t{0}".format(first_frame)
                lf = "Scene last frame:\t{0}".format(last_frame)

                scene_data = "{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}".format(nk, proj_width, width, height, par, fps, ff, lf)

                # Write information and scene data.
                theFile.write("{0}\n{1}\n{0}\n{2}\n".format(divider, sb_exportNukeSceneToAE_info(), scene_data))

                exported_objects = ""

                # Loop over the accepted nodes.
                for n in accepted_nodes:

                    # Find node type.
                    if n.Class() == "Camera" or n.Class() == "Camera2":
                        node_type = "Camera"
                    elif n.Class() == "Card" or n.Class() == "Card2":
                        node_type = "Card"
                    elif n.Class() == "Axis" or n.Class() == "Axis2":
                        node_type = "Axis"

                    # Write object information.
                    object_type = "Object type:\t{0}".format(node_type)
                    object_name = "Name:\t{0}".format(n["name"].value())

                    if node_type == "Camera":
                        hap_value = "{0:.5f}".format(n["haperture"].value())
                        hap = "Horizontal aperture:\t{0}".format(hap_value)
                        columns = "Frame\tPositionX\tPositionY\tPositionZ\tRotationX\tRotationY\tRotationZ\tFocal Length"
                        theFile.write("{0}\n{1}\n{2}\n{3}\n\n{4}\n".format(divider, object_type, object_name, hap, columns))

                    elif node_type == "Card":
                        if nuke.dependencies(n):
                            cardFormatNode = nuke.dependencies(n)[0]
                        else:
                            cardFormatNode = n
                        card_width = "Card width:\t{0}".format(cardFormatNode.format().width() )
                        card_height = "Card height:\t{0}".format(cardFormatNode.format().height() )
                        if not n["image_aspect"].value():
                            card_height = card_width
                        card_par = "Card pixel aspect ratio:\t{0}".format(cardFormatNode.format().pixelAspect() )
                        columns = "Frame\tPositionX\tPositionY\tPositionZ\tRotationX\tRotationY\tRotationZ\tScaleX\tScaleY\tScaleZ"
                        theFile.write("{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n\n{6}\n".format(divider, object_type, object_name, card_width, card_height, card_par, columns))

                    elif node_type == "Axis":
                        columns = "Frame\tPositionX\tPositionY\tPositionZ\tRotationX\tRotationY\tRotationZ\tScaleX\tScaleY\tScaleZ"
                        theFile.write("{0}\n{1}\n{2}\n\n{3}\n".format(divider, object_type, object_name, columns))

                    # Loop through the frame range and write data.
                    for i in range(first_frame, last_frame + 1):

                        # Get data from matrix.
                        posX, posY, posZ, rotX, rotY, rotZ, scaleX, scaleY, scaleZ = convertMatrixToPosRotScale(n, i, "ZYX")

                        # Set object specific values.
                        if node_type == "Camera":
                            focal = n["focal"].valueAt(i)
                            node_data = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(i, posX, posY, posZ, rotX, rotY, rotZ, focal)

                        elif node_type == "Card" or node_type == "Axis":
                            node_data = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}".format(i, posX, posY, posZ, rotX, rotY, rotZ, scaleX, scaleY, scaleZ)

                        # Write data. 
                        if not i == last_frame:
                            node_data = "{0}\n".format(node_data)

                        theFile.write(node_data)

                        # Check if a knob is animated.
                        # If there is no animation, just write the first frame.
                        if not checkIfAnimated(n):
                            break

                    # Make a new line for the next node.
                    theFile.write("\n")

                    # Success!
                    #print "{0} was successfully exported.".format(n["name"].value())
                    exported_objects = "{0}\n{1}".format(exported_objects, n["name"].value())

                # Add a divider as the last step.
                theFile.write(divider)

        # Catch errors.
        except IOError, e:
            if e.errno == 13:
                nuke.message("You do not have access to write a file to: {0}.".format(file_path))
                return
            else:
                nuke.message("Can't write file to: {0}.".format(file_path))
                return

        # Success!
        nuke.message("The following objects were successfully exported:\n{0}".format(exported_objects))

# Run main script.
def sb_exportNukeSceneToAE():
    sb_exportNukeSceneToAE_Panel().show()
