#///////////////////////////////////////////////////////////////////////////////////#

#Backdrop Manager
#created by: Michael De Caria (decariamichael@gmail.com) www.michaeldecaria.com
#20.10.14
#version: 2.4
#about: Lets you manage all your backdrops in real-time with just one panel
#to run: Add the following to your menu.py file
#http://www.nukepedia.com/python/ui/backdrop-manager
'''
import BackdropManager
from BackdropManager import addBackdropManager

paneMenu = nuke.menu( 'Pane' )
paneMenu.addCommand( 'Backdrop Manager', addBackdropManager )
nukescripts.registerPanel('com.ohufx.Backdrop', addBackdropManager )
'''

#///////////////////////////////////////////////////////////////////////////////////#


import os
import nuke
import nukescripts

class BackdropManager(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'Backdrop Manager', 'com.ohufx.Backdrop')
        # DEFINE DICTIONARIES/LIST
        self.elements = []
        self.key = {}
        self.fontset = {}
        self.fontsize = {}
        self.fontcol = {}
        self.nodes = False
        # CREATE KNOBS
        self.srcNodes = { 'All': nuke.allNodes(), 'Selected': nuke.selectedNodes() }
        self.nodesChoice = nuke.Enumeration_Knob( 'nodes', 'Source Nodes', ['All', 'Selected'] )       
        self.label = nuke.Enumeration_Knob( 'backdrop', 'Backdrop Label', self.comeon() )
        self.cv = nuke.Multiline_Eval_String_Knob( 'newlabel', 'New Label' )
        self.warning = nuke.Text_Knob( 'warning', '<span style="color:red">No Backdrops Selected</span>' )
        self.warning.setVisible( False )
        self.warning.clearFlag( nuke.STARTLINE )
        self.size = nuke.Int_Knob( 'fontsize', '' )
        self.size.setValue( 20 )
        self.size.clearFlag( nuke.STARTLINE )
        self.size.setValue( self.fontsize[self.key[self.label.value()]] )
        self.font = nuke.Font_Knob( 'font', 'Font' )
        self.font.setValue(self.fontset[self.key[ self.label.value()]] )
        self.fontcolor = nuke.ColorChip_Knob( 'fontcolor', 'color' )
        self.fontcolor.setValue(self.fontcol[ self.key[self.label.value()]] )
        self.backcolor = nuke.ColorChip_Knob( 'backcolor', 'backcolor' )
        self.backcolor.setValue( self.key[self.key[self.label.value()]] )
        self.cv.setValue( self.label.value() )
        bnode = self.key[self.label.value()]
        if self.cv.value() == bnode.knob( 'name' ).value():
            self.cv.setValue( '' )
        # ADD KNOBS
        for k in ( self.nodesChoice, self.label, self.warning, self.cv, self.backcolor, self.font, self.size, self.fontcolor):
            self.addKnob( k )

    def comeon( self ):
        # SHOW ERROR IF NO BACKDROPS FOUND
        if any( n.Class() == 'BackdropNode' for n in nuke.allNodes() ):
            pass
        else:
            nuke.message( 'No Backdrops Found!' )
            raise KeyError, 'No Backdrops Found!'
        # CHECKING IF ANY OF THE SELECTED NODES ARE BACKDROPS
        for b in nuke.selectedNodes():
                if b.Class()=='BackdropNode':
                    self.nodes = True
        # RESETS LIST BY DELETING THE CURRENT ONE
        del self.elements[:]
        for a in self.srcNodes[self.nodesChoice.value()]:
            if a.Class()=='BackdropNode':
                # IF BACKDROP IS BLANK THEN TEMPORARILY CHANGE IT TO ITS NAME
                if a.knob( 'label' ).value() == '':
                        a.knob( 'label' ).setValue( a.knob( 'name' ).value())
                # ALLOCATING BACKDROP VALUES TO DICTIONARIES
                self.key[a.knob( 'label' ).value()] = a
                self.key[a] = a.knob( 'tile_color' ).value()
                self.fontset[a] = a.knob( 'note_font' ).value()
                self.fontsize[a] = int(a.knob( 'note_font_size' ).value())
                self.fontcol[a] = a.knob( 'note_font_color' ).value()
                g = a.knob( 'label' ).value()
                self.elements.append(g)
                # CHANGE TEMPORARILY BACKDROPS BACK TO BLANK
        for b in self.srcNodes[self.nodesChoice.value()]:
            if b.knob( 'label' ).value() == b.knob( 'name' ).value():
                b.knob( 'label' ).setValue( '' )
        return self.elements

    def knobChanged( self, knob ):
        if knob in ( self.label, self.nodesChoice ):
            # SET VALUES TO NODE KEYS IN THE DICTIONARIES
            try:
                self.label.setValues( self.comeon() )
                self.backcolor.setValue( self.key[self.key[self.label.value()]] )
                self.font.setValue( self.fontset[self.key[self.label.value()]] )
                self.size.setValue( self.fontsize[self.key[self.label.value()]] )
                self.fontcolor.setValue( self.fontcol[self.key[self.label.value()]] )
                self.cv.setValue( self.label.value())
                bnode = self.key[self.label.value()]
                if self.cv.value() == bnode.knob( 'name').value():
                    self.cv.setValue( '' )
            except:
                self.label.setValues( self.comeon() )
            if self.nodesChoice.getValue() == 0:
                self.warning.setVisible( False )
            else:
                if self.nodes == False:
                        self.warning.setVisible( True )
                else:
                        self.warning.setVisible( False )
        # CHANGE ITEM IN LIST IF ITS NOT SELECTED
        if knob is self.nodesChoice:
            try:
                self.key[self.label.value()]
            except:
                if self.nodes == True:
                   self.label.setValue( 0 )
                   self.backcolor.setValue( self.key[self.key[self.label.value()]] )
                   self.font.setValue( self.fontset[self.key[self.label.value()]] )
                   self.size.setValue( self.fontsize[self.key[self.label.value()]] )
                   self.fontcolor.setValue( self.fontcol[self.key[self.label.value()]] )
        # SET LABEL IF THERE IS A BACKDROP
        if knob is self.cv:
            if self.nodesChoice.getValue() == 1 and self.nodes == False:
                pass
            else:
                bnode = self.key[self.label.value()]
                bnode.knob( 'label' ).setValue( self.cv.value() )
                self.label.setValues( self.comeon() )
        # SET OTHER VALUES TO CURRENT SETTINGS
        if knob in ( self.size, self.font, self.fontcolor, self.backcolor ):
            if self.nodesChoice.getValue() == 1 and self.nodes == False:
                pass
            else:
                bnode = self.key[self.label.value()]
                bnode.knob( 'note_font' ).setValue(self.font.value())
                bnode.knob( 'note_font_size' ).setValue( self.size.value() )
                bnode.knob( 'note_font_color' ).setValue( self.fontcolor.value() )
                bnode.knob( 'tile_color' ).setValue( self.backcolor.value() )
                bnode.knob( 'label' ).setValue( self.cv.value() )
                self.label.setValues( self.comeon() )

# FUNCTION TO ADD IT AS A PANEL
def addBackdropManager():
    global backdropManager
    backdropManager = BackdropManager()
    return backdropManager.addToPane()
