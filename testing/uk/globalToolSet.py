################

"""
    sb_globalToolSet
    Simon Bjork
    March 2014
    bjork.simon@gmail.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your menu.py:

    import sb_globalToolSet
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
    sb_tools.addCommand("Python/sb GlobalToolSet", 'sb_globalToolSet.sb_globalToolSet("D:/tools/ToolSets/")', '')

"""

################

import os
import nuke
import errno

################

def sb_globalToolSet(defaultPath):

    # Create the panel.
    p = nuke.Panel( "sb_globalToolSet" )
    p.addFilenameSearch('Folder path', defaultPath)
    p.addSingleLineInput('Subfolder', '(Optional)')
    p.addSingleLineInput('ToolSet name', '')
    result = p.show()
    
    if result:
    
        n = nuke.selectedNodes()
    
        if len(n) == 0:
            nuke.message("No nodes selected.")
            return

        folderPath = p.value("Folder path")
        name = p.value("ToolSet name")
        sub = p.value("Subfolder")

        if folderPath == "":
            nuke.message("Specify a folder path.")
            return

        if not folderPath.endswith("/"):
            folderPath = "{0}/".format(folderPath)

        if name == "":
            nuke.message("Specify a name.")
            return

        if sub == "" or sub == "(Optional)":
            folderPath = folderPath
        else:
            folderPath = "{0}{1}/".format(folderPath, sub.replace(" ", "_"))

        if not os.path.exists(folderPath):
            try:
                os.makedirs(folderPath)
            except:
                print "Can't create folder at:\n\n{0}".format(folderPath)
                return

        nameFix = name.replace(" ", "_")

        # Create the file.
        toolset = "{0}{1}.nk".format(folderPath, nameFix)
        nuke.nodeCopy(toolset)

        print "{0}.nk was successfully exported as a ToolSet.".format(nameFix)
