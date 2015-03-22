####################

"""
    sb_addViewerLuts
    Simon Bjork
    May 2013
    bjork.simon@gmail.com

    Search for supported lut files in a folder and adds them as viewer luts.

    Supported naming convention is <input_colorspace>2<name of lut>.extension
    For example: log2kodak_2383.csp

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the following to your init.py:

    import sb_addViewerLuts
    sb_addViewerLuts.sb_addViewerLuts("D:/library/colour/luts/", addCineonLut = True)

"""

####################

import os
import re
import nuke

################

def sb_addViewerLuts(lutPath, addCineonLut = True):

    lutFormats = ["3dl", "csp", "cube", "vf", "lut"]
    colorspace = ["linear", "cineon","log", "logC", "AlexaV3LogC", "panalog", "slog", "sRGB", "rec709"]

    if os.path.exists(lutPath) == False:
        print "sb_addViewerLuts: LUT folder does not exsist."
        return

    # Make sure there is a / in the end of the folder path.
    if not lutPath.endswith("/"):
        lutPath = "{0}/".format(lutPath)

    # Get supported luts.
    allFiles = nuke.getFileNameList(lutPath)
    luts = []
    for i in allFiles:
        for j in lutFormats:
            if i.endswith( "." + j.lower() ):
                luts.append(i)
    
    if len(luts) == 0:
        print "No supported luts available."
        return

    added_luts = []
    skipped_luts = []

    for i in luts:
        lutOK = False
        input = ""
        currLutPath = lutPath + i
        splitFileName = os.path.splitext(i)
        lutName = splitFileName[0].strip()
        lutExt = splitFileName[1][1:].strip().lower()
        try:
            splitLutName = re.split('2',lutName,1)
            displayName = splitLutName[1].replace("_", " ")
        except IndexError:
            skipped_luts.append(i)
            continue

        # Get the input colorspace.
        for k in colorspace:
            if splitLutName[0].lower() == k.lower():
                input = k
                lutOK = True
                break

        if lutOK:
            # Get correct naming for input space.
            if input == "linear":
                input = "Linear"
            elif input == "lin":
                input = "Linear" 
            elif input == "cineon":
                input = "Cineon" 
            elif input == "log":
                input = "Cineon"
            elif input == "logC":
                input = "AlexaV3LogC"
            elif input == "alexav3logc":
                input = "AlexaV3LogC"
            elif input == "panalog":
                input = "Panalog"
            elif input == "slog":
                input = "SLog"
            elif input == "srgb":
                input = "sRGB"
            elif input == "rec709":
                input = "rec709"

            # Register the lut.
            lutSyntax = "vfield_file {0} colorspaceIn {1}".format(currLutPath, input)
            nuke.ViewerProcess.register(displayName, nuke.createNode, ("Vectorfield", lutSyntax))
            added_luts.append(i)

    # Add default Cineon as a lut.
    if addCineonLut:
        nuke.ViewerProcess.register("Cineon", nuke.createNode, ("ViewerProcess_1DLUT", "current Cineon"))
        added_luts.append("Cineon")

    # Give feedback in terminal.
    if len(skipped_luts) > 0:
        print "sb_addViewerLuts did not register the following LUTs as they do not use the supported naming convention: {0}".format(", ".join(skipped_luts))

    if len(added_luts) > 0:
        print "sb_addViewerLuts registered the following LUTs: {0}".format(", ".join(added_luts))
    else:
        print "sbAddViewerLuts did not register any LUTs."
