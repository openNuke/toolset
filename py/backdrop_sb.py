####################

"""
    sb_backdrop
    Simon Bjork
    bjork.simon@gmail.com

    To install the script:

    - Add the script to your Nuke pluginPath.
    - Add the one of the following methods to your menu.py:

    # Override default functions.
    import sb_backdrop
    nukescripts.autoBackdrop = sb_backdrop
    nuke.toolbar("Nodes").addCommand('Other/Backdrop', 'sb_backdrop.sb_backdrop()','')

    # Custom menu.
    import sb_backdrop
    sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
    sb_tools.addCommand("Python/sb Backdrop", 'sb_backdrop.sb_backdrop()', '')

"""

####################

import nuke
import random

################

def sb_backdrop():

# Create the panel.
    p = nuke.Panel( "sb Backdrop" )
    p.addSingleLineInput('Backdrop name', '')
    p.addSingleLineInput('Font size', '92')
    result = p.show()
    
    if not result:
        return
    
    bd_name = p.value("Backdrop name")
    font_size = p.value("Font size")

    if not font_size.isdigit():
        font_size = 92
    else:
        font_size = int(font_size)

    ok_colors =  [726945023, 758728703, 1194668799, 1161185279, 658977535, 1145521407, 1095189759, 942753791, 994522623]
    ran_num = random.randrange(0,len(ok_colors))
    color = ok_colors[ran_num]

    selNodes = nuke.selectedNodes()
    if not selNodes:
        n = nuke.createNode("BackdropNode", inpanel=False)
        n["tile_color"].setValue(color)
        n["note_font_size"].setValue(font_size)
        n["label"].setValue(bd_name)
        return

    # Calculate bounds for the backdrop node.
    bdX = min([node.xpos() for node in selNodes])
    bdY = min([node.ypos() for node in selNodes])
    bdW = max([node.xpos() + node.screenWidth() for node in selNodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in selNodes]) - bdY

    # Expand the bounds to leave a little border. Elements are offsets for left, top, right and bottom edges respectively
    left, top, right, bottom = (-200, -250, 200, 200)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    n = nuke.createNode("BackdropNode", inpanel=False)
    n["xpos"].setValue(bdX)
    n["bdwidth"].setValue(bdW)
    n["ypos"].setValue(bdY)
    n["bdheight"].setValue(bdH)
    n["tile_color"].setValue(color)
    n["note_font_size"].setValue(font_size)
    n["label"].setValue(bd_name)

    # revert to previous selection
    n['selected'].setValue(False)
    for node in selNodes:
        node['selected'].setValue(True)

    return n
