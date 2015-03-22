import nuke
import nukescripts
import re

#http://www.nukepedia.com/python/nodegraph/massivepanel/
class MassivePanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'MassivePanel', 'com.ohufx.MassivePanel')



############# setting help messages
        KnobInfo = " type knob's name in, also you can Ctrl+Drag&Drop from the knob you want to adjust , then if you will click in value knob and back click in Knob field it will automaticly extract knob name for you (trying to make it better in next version :)" 
        ArrayInfo = "You have to set what exactly you want to change, All - will set same value on xyz, X , Y , Z - will set value only on your selection x,y or z"
        ValueInfo = "set new value for selected nodes" 
        IncrInfo = "set here increment between values, for example if value=3 and increment 2 - you will have 3,5,7,9..."
        KindInfo = "put String if you want to set string and finally put Expression if you entering expression"
        FindWhatInfo = "find string in knob"
        ReplaceWhatInfo = "replace with this string "
#############creating knobs


        self.Knob = nuke.String_Knob( KnobInfo, "Knob:")
        self.Print = nuke.PyScript_Knob("Print values from selected knob for every selected node","Print")
        self.Value = nuke.String_Knob(ValueInfo,"Value:")
        self.Value.clearFlag(nuke.STARTLINE)

        self.Array = nuke.Enumeration_Knob(ArrayInfo,"Array:",[ "All","X","Y","Z","W"],)
        self.Array.clearFlag(nuke.STARTLINE)
        self.Kind = nuke.Enumeration_Knob(KindInfo,"                                                                        Kind:",[ "Float","String", "Expression"],)
        self.Kind.clearFlag(nuke.STARTLINE)
        self.Increment = nuke.String_Knob(IncrInfo,"Increment:","0")
        self.Increment.setFlag(nuke.STARTLINE)
        self.GetKnob = nuke.PyScript_Knob("Show all knobs of selected node","GetKnob")
        self.GetKnob.setFlag(nuke.STARTLINE)
        self.Go = nuke.PyScript_Knob("Go", "<b>Go")
        
        self.setAnimation = nuke.PyScript_Knob("setAnimated", "setA")
        self.clearAnimation = nuke.PyScript_Knob("clearAnimation", "clearA")
        #self.setAnimation.setFlag(nuke.STARTLINE)
        
        self.FindWhat = nuke.String_Knob( FindWhatInfo, "FindWhat:")
        self.FindWhat.clearFlag(nuke.STARTLINE)
        self.ReplaceWhat = nuke.String_Knob( ReplaceWhatInfo, "ReplaceWhat:")
        self.ReplaceWhat.clearFlag(nuke.STARTLINE)
        self.Replace = nuke.PyScript_Knob("Replace","Replace")
        self.Replace.clearFlag(nuke.STARTLINE)
        
        
        self.BeginA = nuke.Tab_Knob( 'Basic', None, 1 ) 
        self.BeginA.setFlag(0x00000001)        
        self.EndA = nuke.Tab_Knob( '', None, -1 )       

        self.Begin = nuke.Tab_Knob( 'Additional', None, 1 )
        self.Begin.setFlag(0x00000001)
        self.End = nuke.Tab_Knob( '', None, -1 )

        self.BeginSearch = nuke.Tab_Knob( 'Search and Replace', None, 1 )
        self.BeginSearch.setFlag(0x00000001)
        self.EndSearch = nuke.Tab_Knob( '', None, -1 )
        
        self.Divider = nuke.Text_Knob("")
        self.Refresh = nuke.PyScript_Knob("Refresh takes pannel, do it usually on script reopen", "Refresh")
        self.Refresh.clearFlag(nuke.STARTLINE)

        self.Reset1 = nuke.PyScript_Knob("Reset Take","<font color='Black'>Reset take1")
        self.Take1 = nuke.PyScript_Knob("select nodes you want to affect and press me", "take1")
        self.Take1.setFlag(nuke.STARTLINE)
        self.Disable1 = nuke.Boolean_Knob("disable/enable specifed nodes","disable")
        self.Disable1.clearFlag(nuke.STARTLINE)
        self.Float1 = nuke.String_Knob("set here desired value","value:")
        self.Float1.clearFlag(nuke.STARTLINE)
        self.Array1= nuke.String_Knob("set here knob you want to affect","knob:")
        self.Array1.clearFlag(nuke.STARTLINE)

        self.Reset2 = nuke.PyScript_Knob("Reset Take","<font color='Black'>Reset take2")
        self.Take2 = nuke.PyScript_Knob("select nodes you want to affect and press me", "take2")
        self.Take2.setFlag(nuke.STARTLINE)
        self.Disable2 = nuke.Boolean_Knob("disable/enable specifed nodes","disable")
        self.Disable2.clearFlag(nuke.STARTLINE)
        self.Float2 = nuke.String_Knob("set here desired value","value:")
        self.Float2.clearFlag(nuke.STARTLINE)
        self.Array2= nuke.String_Knob("set here knob you want to affect","knob:")
        self.Array2.clearFlag(nuke.STARTLINE)


        self.Reset3 = nuke.PyScript_Knob("Reset Take","<font color='Black'>Reset take3")
        self.Take3 = nuke.PyScript_Knob("select nodes you want to affect and press me", "take3")
        self.Take3.setFlag(nuke.STARTLINE)
        self.Disable3 = nuke.Boolean_Knob("disable/enable specifed nodes","disable")
        self.Disable3.clearFlag(nuke.STARTLINE)
        self.Float3 = nuke.String_Knob("set here desired value","value:")
        self.Float3.clearFlag(nuke.STARTLINE)
        self.Array3= nuke.String_Knob("set here knob you want to affect","knob:")
        self.Array3.clearFlag(nuke.STARTLINE)


        self.Reset4 = nuke.PyScript_Knob("Reset Take","<font color='Black'>Reset take4")
        self.Take4 = nuke.PyScript_Knob("select nodes you want to affect and press me", "take4")
        self.Take4.setFlag(nuke.STARTLINE)
        self.Disable4 = nuke.Boolean_Knob("disable/enable specifed nodes","disable")
        self.Disable4.clearFlag(nuke.STARTLINE)
        self.Float4 = nuke.String_Knob("set here desired value","value:")
        self.Float4.clearFlag(nuke.STARTLINE)
        self.Array4= nuke.String_Knob("set here knob you want to affect","knob:")
        self.Array4.clearFlag(nuke.STARTLINE)


        self.Reset5 = nuke.PyScript_Knob("Reset Take","<font color='Black'>Reset take5")
        self.Take5 = nuke.PyScript_Knob("select nodes you want to affect and press me", "take5")
        self.Take5.setFlag(nuke.STARTLINE)
        self.Disable5 = nuke.Boolean_Knob("disable/enable specifed nodes","disable")
        self.Disable5.clearFlag(nuke.STARTLINE)
        self.Float5 = nuke.String_Knob("set here desired value","value:")
        self.Float5.clearFlag(nuke.STARTLINE)
        self.Array5= nuke.String_Knob("set here knob you want to affect","knob:")
        self.Array5.clearFlag(nuke.STARTLINE)




        self.Reset6 = nuke.PyScript_Knob("Reset Take","<font color='Black'>Reset take6")
        self.Take6 = nuke.PyScript_Knob("select nodes you want to affect and press me", "take6")
        self.Take6.setFlag(nuke.STARTLINE)
        self.Low6 = nuke.Boolean_Knob("low/high value","low")
        self.Low6.clearFlag(nuke.STARTLINE)
        self.Array6= nuke.String_Knob("set here knob you want to affect","knob:")
        self.Array6.clearFlag(nuke.STARTLINE)
        self.lowVal6 = nuke.String_Knob("set here low value","low:")
        self.lowVal6.clearFlag(nuke.STARTLINE)
        self.highVal6 = nuke.String_Knob("set here high value","high:")
        self.highVal6.clearFlag(nuke.STARTLINE)

        self.Reset7 = nuke.PyScript_Knob("Reset Take","<font color='Black'>Reset take7")
        self.Take7 = nuke.PyScript_Knob("select nodes you want to affect and press me", "take7")
        self.Take7.setFlag(nuke.STARTLINE)
        self.Low7 = nuke.Boolean_Knob("low/high value","low")
        self.Low7.clearFlag(nuke.STARTLINE)
        self.Array7= nuke.String_Knob("set here knob you want to affect","knob:")
        self.Array7.clearFlag(nuke.STARTLINE)
        self.lowVal7 = nuke.String_Knob("set here low value","low:")
        self.lowVal7.clearFlag(nuke.STARTLINE)
        self.highVal7 = nuke.String_Knob("set here high value","high:")
        self.highVal7.clearFlag(nuke.STARTLINE)
        self.Saturation = nuke.PyScript_Knob("set saturation 2.5", "Saturation","VP.Saturation()")
        self.Saturation.clearFlag(nuke.STARTLINE)
		
        self.Flip = nuke.PyScript_Knob("flip the picture", "Flip","VP.Flip()",icon = "Flip.png")
        self.Flip.clearFlag(nuke.STARTLINE)
		
        self.Flop = nuke.PyScript_Knob("flop the picture", "Flop","VP.Flop()")
        self.Flop.clearFlag(nuke.STARTLINE)
		
        self.Grid = nuke.PyScript_Knob("show grid on the picture", "Grid","VP.Grid()")
        self.Grid.clearFlag(nuke.STARTLINE)
		
        self.Text = nuke.PyScript_Knob("help","                  help                  ","nukescripts.start('http://www.youtube.com/watch?v=vZbzoROjjKA')")
        self.Text.clearFlag(nuke.STARTLINE)





############applying knobs to panel in order
        for k in (self.BeginA,self.Knob,self.Value,self.Go,self.Increment,self.Array,self.Kind,self.EndA,self.Begin,self.GetKnob,self.Print,self.setAnimation,self.clearAnimation,self.End,self.BeginSearch,self.FindWhat,self.ReplaceWhat,self.Replace,self.EndSearch,self.Divider,self.Refresh,self.Text,self.Saturation,self.Flip,self.Flop,self.Grid,self.Take1,self.Disable1,self.Array1,self.Float1,self.Reset1,self.Take2,self.Disable2,self.Array2,self.Float2,self.Reset2,self.Take3,self.Disable3,self.Array3,self.Float3,self.Reset3,self.Take4,self.Disable4,self.Array4,self.Float4,self.Reset4,self.Take5,self.Disable5,self.Array5,self.Float5,self.Reset5,self.Take6,self.Low6,self.Array6,self.lowVal6,self.highVal6,self.Reset6,self.Take7,self.Low7,self.Array7,self.lowVal7,self.highVal7,self.Reset7):
            self.addKnob(k)


############### setting basic function
    def knobChanged(self,knob):
            if knob ==self.Knob:
              string = self.Knob.value()
              if ':' in string:
                  firstSplit = string.rsplit('.')[1] 
                  self.Knob.setValue(firstSplit)
            elif knob == self.Print:
              n = nuke.selectedNodes()
              x = self.Knob.value()
              data = ""
              for one in n:
                value = one[x].value()
                value = str(value)
                name = one['name'].value()
                data1 = name + "---" + x + "---" + value +"\n"
                data = data + data1
              nuke.message(data)
              
            elif knob == self.GetKnob:
                b = nuke.selectedNode()
                allKnobs = "ALL KNOBS:\n"
                for i in range (b.getNumKnobs()):
                    knob =  b.knob (i).name()
                    allKnobs = allKnobs + knob+"\n"
                nuke.message(allKnobs)
            elif knob == self.setAnimation:
                string = self.Knob.value()
                nodesA = nuke.selectedNodes()
                for nodeA in nodesA:
                    xx = nodeA[string].value()
                    nodeA[string].setAnimated()
                    nodeA[string].setValue(xx)                  
            elif knob == self.clearAnimation:
                string = self.Knob.value()
                nodesA = nuke.selectedNodes()
                for nodeA in nodesA:
                    nodeA[string].clearAnimated()                
            elif knob == self.Go:
                s = self.Value.value()
                Knob = self.Knob.value()
                Value = self.Value.value()
                array = self.Array.value()
                kind = self.Kind.value()
                incr = self.Increment.value()
                incr = float(incr)  
                u = 0
                n = nuke.selectedNodes()


######## setting float values
                if array== "All" and kind == "Float":
                     Value = float(Value)
                     for n in n:
                        n[Knob].setValue(Value+u)
                        u = incr+ u
                if array== "X" and kind == "Float":
                     Value = float(Value)
                     for n in n:
                        n[Knob].setValue(Value+u,0) 
                        u = incr+ u  
                if array== "Y" and kind == "Float":
                     Value = float(Value)
                     for n in n:
                        n[Knob].setValue(Value+u,1) 
                        u = incr+ u  
                if array== "Z" and kind == "Float":
                     Value = float(Value)
                     for n in n:
                        n[Knob].setValue(Value+u,2)
                        u = incr+ u
                if array== "W" and kind == "Float":
                     Value = float(Value)
                     for n in n:
                        n[Knob].setValue(Value+u,3)
                        u = incr+ u

    ######## setting string values

                if array== "All" and kind == "String":
                     for n in n:
                        n[Knob].setValue(Value)
                if array== "X" and kind == "String":
                     for n in n:
                        n[Knob].setValue(Value,0) 
                if array== "Y" and kind == "String":
                     for n in n:
                        n[Knob].setValue(Value,1) 
                if array== "Z" and kind == "String":
                     for n in n:
                        n[Knob].setValue(Value,2)
                if array== "W" and kind == "String":
                     for n in n:
                        n[Knob].setValue(Value,3)


    ######## setting expression  values

                if array== "All" and kind == "Expression":
                     for n in n:
                        n[Knob].setExpression(Value)
                if array== "X" and kind == "Expression":
                     for n in n:
                        n[Knob].setExpression(Value,0) 
                if array== "Y" and kind == "Expression":
                     for n in n:
                        n[Knob].setExpression(Value,1) 
                if array== "Z" and kind == "Expression":
                     for n in n:
                        n[Knob].setExpression(Value,2)
                if array== "W" and kind == "Expression":
                     for n in n:
                        n[Knob].setExpression(Value,3)  
            elif knob == self.Replace:
                knob = self.Knob.value()
                print knob
                findSTR = self.FindWhat.value()
                print findSTR
                replaceSTR = self.ReplaceWhat.value()
                print replaceSTR
                replNodes = nuke.selectedNodes()
                for boy in replNodes:
                    newVal = boy[knob].value().replace(findSTR,replaceSTR)
                    boy[knob].setValue(newVal)

################################Takes:
            elif knob == self.Reset1:
                if nuke.ask('This will reset current Take, are you sure you up to it?'):
                    w = nuke.toNode("root")
                    takesInfo = nuke.Root().knob('label').getValue()
                    o1= takesInfo.split(",")[0]
                    o2= takesInfo.split(",")[1]
                    o3= takesInfo.split(",")[2]
                    o4= takesInfo.split(",")[3]
                    o5= takesInfo.split(",")[4]
                    o6= takesInfo.split(",")[5]
                    o7= takesInfo.split(",")[6]
                    n =nuke.allNodes()
                    for t in n:
                       lab = t['label'].value()
                       if "take1" in lab:
                           lab = lab.replace("take1","")
                           t['label'].setValue(lab)
                           self.Float1.setValue("")
                           self.Array1.setValue("")
                           self.Take1.setLabel("take1")
                           w['label'].setValue("take1"+","+o2+","+o3+","+o4+","+o5+","+o6+","+o7)
                else:
                    print "okay no problem"
            elif knob == self.Reset2:
                if nuke.ask('This will reset current Take, are you sure you up to it?'):
                    w = nuke.toNode("root")
                    takesInfo = w['label'].value()
                    o1= takesInfo.split(",")[0]
                    o2= takesInfo.split(",")[1]
                    o3= takesInfo.split(",")[2]
                    o4= takesInfo.split(",")[3]
                    o5= takesInfo.split(",")[4]
                    o6= takesInfo.split(",")[5]
                    o7= takesInfo.split(",")[6]
                    n =nuke.allNodes()
                    for t in n:
                       lab = t['label'].value()
                       if "take2" in lab:
                           lab = lab.replace("take2","")
                           t['label'].setValue(lab)
                           self.Float2.setValue("")
                           self.Array2.setValue("")
                           self.Take2.setLabel("take2")
                           w['label'].setValue(o1+","+"take2"+","+o3+","+o4+","+o5+","+o6+","+o7)
                else:
                    print "okay no problem"
            elif knob == self.Reset3:
                if nuke.ask('This will reset current Take, are you sure you up to it?'):
                    w = nuke.toNode("root")
                    takesInfo = w['label'].value()
                    o1= takesInfo.split(",")[0]
                    o2= takesInfo.split(",")[1]
                    o3= takesInfo.split(",")[2]
                    o4= takesInfo.split(",")[3]
                    o5= takesInfo.split(",")[4]
                    o6= takesInfo.split(",")[5]
                    o7= takesInfo.split(",")[6]
                    n =nuke.allNodes()
                    for t in n:
                       lab = t['label'].value()
                       if "take3" in lab:
                           lab = lab.replace("take3","")
                           t['label'].setValue(lab)
                           self.Float3.setValue("")
                           self.Array3.setValue("")
                           self.Take3.setLabel("take3")
                           w['label'].setValue(o1+","+o2+","+"take3"+","+o4+","+o5+","+o6+","+o7)
                else:
                    print "okay no problem"
            elif knob == self.Reset4:
                if nuke.ask('This will reset current Take, are you sure you up to it?'):
                    w = nuke.toNode("root")
                    takesInfo = w['label'].value()
                    o1= takesInfo.split(",")[0]
                    o2= takesInfo.split(",")[1]
                    o3= takesInfo.split(",")[2]
                    o4= takesInfo.split(",")[3]
                    o5= takesInfo.split(",")[4]
                    o6= takesInfo.split(",")[5]
                    o7= takesInfo.split(",")[6]
                    n =nuke.allNodes()
                    for t in n:
                       lab = t['label'].value()
                       if "take4" in lab:
                           lab = lab.replace("take4","")
                           t['label'].setValue(lab)
                           self.Float4.setValue("")
                           self.Array4.setValue("")
                           self.Take4.setLabel("take4")
                           w['label'].setValue(o1+","+o2+","+o3+","+"take4"+","+o5+","+o6+","+o7)
                else:
                    print "okay no problem"
            elif knob == self.Reset5:
                if nuke.ask('This will reset current Take, are you sure you up to it?'):
                    w = nuke.toNode("root")
                    takesInfo = w['label'].value()
                    o1= takesInfo.split(",")[0]
                    o2= takesInfo.split(",")[1]
                    o3= takesInfo.split(",")[2]
                    o4= takesInfo.split(",")[3]
                    o5= takesInfo.split(",")[4]
                    o6= takesInfo.split(",")[5]
                    o7= takesInfo.split(",")[6]
                    n =nuke.allNodes()
                    for t in n:
                       lab = t['label'].value()
                       if "take5" in lab:
                           lab = lab.replace("take5","")
                           t['label'].setValue(lab)
                           self.Float5.setValue("")
                           self.Array5.setValue("")
                           self.Take5.setLabel("take5")
                           w['label'].setValue(o1+","+o2+","+o3+","+o4+","+"take5"+","+o6+","+o7)
                else:
                    print "okay no problem"


            elif knob == self.Reset6:
                if nuke.ask('This will reset current Take, are you sure you up to it?'):
                    w = nuke.toNode("root")
                    takesInfo = w['label'].value()
                    o1= takesInfo.split(",")[0]
                    o2= takesInfo.split(",")[1]
                    o3= takesInfo.split(",")[2]
                    o4= takesInfo.split(",")[3]
                    o5= takesInfo.split(",")[4]
                    o6= takesInfo.split(",")[5]
                    o7= takesInfo.split(",")[6]
                    n =nuke.allNodes()
                    for t in n:
                       lab = t['label'].value()
                       if "take6" in lab:
                           t['label'].setValue("")
                           self.Array6.setValue("")
                           self.lowVal6.setValue("")
                           self.highVal6.setValue("")
                           self.Take6.setLabel("take6")
                           w['label'].setValue(o1+","+o2+","+o3+","+o4+","+o5+","+"take6"+","+o7)
                else:
                    print "okay no problem"



            elif knob == self.Reset7:
                if nuke.ask('This will reset current Take, are you sure you up to it?'):
                    w = nuke.toNode("root")
                    takesInfo = w['label'].value()
                    o1= takesInfo.split(",")[0]
                    o2= takesInfo.split(",")[1]
                    o3= takesInfo.split(",")[2]
                    o4= takesInfo.split(",")[3]
                    o5= takesInfo.split(",")[4]
                    o6= takesInfo.split(",")[5]
                    o7= takesInfo.split(",")[6]
                    n =nuke.allNodes()
                    for t in n:
                       lab = t['label'].value()
                       if "take7" in lab:
                           #lab = lab.replace("take7","")
                           t['label'].setValue("")
                           self.Array7.setValue("")
                           self.lowVal7.setValue("")
                           self.highVal7.setValue("")
                           self.Take7.setLabel("take7")
                           w['label'].setValue(o1+","+o2+","+o3+","+o4+","+o5+","+o6+",take7")
                else:
                    print "okay no problem"




            elif knob == self.Refresh:
                
                try:
                    n = nuke.selectedNodes("Dot") 
                    for t in n:
                        if t.Class()=="Dot":
                            dep = t.dependencies(nuke.INPUTS)[0]
                            x = dep['xpos'].value()
                            y = dep['ypos'].value()
                            if "red" in t['name'].value():
                                t['xpos'].setValue(x+3)
                                t['ypos'].setValue(y+111)
                            if "green" in t['name'].value():
                                t['xpos'].setValue(x+35)
                                t['ypos'].setValue(y+111)
                            if "blue" in t['name'].value():
                                t['xpos'].setValue(x+65)
                                t['ypos'].setValue(y+111)
                except:
                    print ""
    
                w = nuke.toNode("root")
                takesInfo = nuke.Root().knob('label').getValue()
                take1info= takesInfo.split(",")[0]
                take2info= takesInfo.split(",")[1]
                take3info= takesInfo.split(",")[2]
                take4info= takesInfo.split(",")[3]
                take5info= takesInfo.split(",")[4]
                take6info= takesInfo.split(",")[5]
                take7info= takesInfo.split(",")[6]
                if take1info != "take1":
                    self.Array1.setValue(take1info)
                if take2info != "take2":
                    self.Array2.setValue(take2info)
                if take3info != "take3":
                    self.Array3.setValue(take3info)
                if take4info != "take4":
                    self.Array4.setValue(take4info)
                if take5info != "take5":
                    self.Array5.setValue(take5info)
                if take6info != "take6":
                    self.Array6.setValue(take6info)
                if take7info != "take7":
                    self.Array7.setValue(take7info)

                n =nuke.allNodes()
                for t in n:
                    if "take1" in t['label'].value():
                        d1 = t["disable"].value()
                        self.Disable1.setValue(d1)                   
                        take1refresh =t['name'].value()
                        val1 = str(t[take1info].value())
                        take1refresh=take1refresh[:10]
                        self.Take1.setLabel(take1refresh)
                        tmp1 = self.Float1.getValue()
                        if tmp1 == "False" or tmp1 == "True":
                            self.Float1.setValue("")
                       
                    elif "take2" in t['label'].value():
                        d2 = t["disable"].value()
                        self.Disable2.setValue(d2)
                        val2 = str(t[take2info].value())
                        self.Float2.setValue(val2)           
                        take2refresh =t['name'].value()
                        take2refresh=take2refresh[:10]
                        self.Take2.setLabel(take2refresh)
                        tmp2 = self.Float2.getValue()
                        if tmp2 == "False" or tmp2 == "True":
                            self.Float2.setValue("")
                            
                    elif "take3" in t['label'].value():
                        d3 = t["disable"].value()
                        self.Disable3.setValue(d3)
                        val3 = str(t[take3info].value())
                        self.Float3.setValue(val3)           
                        take3refresh =t['name'].value()
                        take3refresh=take3refresh[:10]
                        self.Take3.setLabel(take3refresh)
                        tmp3 = self.Float3.getValue()
                        if tmp3 == "False" or tmp3 == "True":
                            self.Float3.setValue("")
                            
                    elif "take4" in t['label'].value():
                        d4 = t["disable"].value()
                        self.Disable4.setValue(d4)
                        val4 = str(t[take4info].value())
                        self.Float4.setValue(val4)           
                        take4refresh =t['name'].value()
                        take4refresh=take4refresh[:10]
                        self.Take4.setLabel(take4refresh)
                        tmp4 = self.Float4.getValue()
                        if tmp4 == "False" or tmp4 == "True":
                            self.Float4.setValue("")

                    elif "take5" in t['label'].value():
                        d5 = t["disable"].value()
                        self.Disable5.setValue(d5)
                        val5 = str(t[take5info].value())
                        self.Float5.setValue(val5)           
                        take5refresh =t['name'].value()
                        take5refresh=take5refresh[:10]
                        self.Take5.setLabel(take5refresh)
                        tmp5 = self.Float5.getValue()
                        if tmp5 == "False" or tmp5 == "True":
                            self.Float5.setValue("")



                    elif "take6" in t['label'].value(): #go to all take7 nodes
                        val6 = str(t['label'].value())  #get value from the knob
                        val6 = val6.replace('take6/',"")
                        val6 = val6.replace('[',"")
                        val6 = val6.replace(']',"")
                        lowrefref6 =val6.split(',')[0]
                        highrefref6 =val6.split(',')[1]
                        self.lowVal6.setValue(lowrefref6)            #set value to low
                        self.highVal6.setValue(highrefref6)          #set value to high
                        take6refresh =t['name'].value()
                        take6refresh=take6refresh[:10]
                        self.Take6.setLabel(take6refresh)
                        tmp6 = self.lowVal6.getValue()
                        if tmp6 == "False" or tmp6 == "True":
                            self.lowVal6.setValue("")


                    elif "take7" in t['label'].value(): #go to all take7 nodes
                        val7 = str(t['label'].value())  #get value from the knob
                        val7 = val7.replace('take7/',"")
                        val7 = val7.replace('[',"")
                        val7 = val7.replace(']',"")
                        lowrefref7 =val7.split(',')[0]
                        highrefref7 =val7.split(',')[1]
                        self.lowVal7.setValue(lowrefref7)            #set value to low
                        self.highVal7.setValue(highrefref7)          #set value to high
                        take7refresh =t['name'].value()
                        take7refresh=take7refresh[:10]
                        self.Take7.setLabel(take7refresh)
                        tmp7 = self.lowVal7.getValue()
                        if tmp7 == "False" or tmp7 == "True":
                            self.lowVal7.setValue("")
                            
            elif knob == self.Take1:
                if nuke.ask("This will add selected nodes to Take1 group, cancel to abort"):
                    n =nuke.selectedNodes()
                    for t in n:
                       t['label'].setValue('take1')
                       take1name =t['name'].value()
                       take1name=take1name[:10]
                       self.Take1.setLabel(take1name)
                    aa1 = self.Array1.value()
                    if aa1 == "":
                        aa1="disable"
                        self.Array1.setValue(aa1)
                    w = nuke.toNode("root")
                    rootcheck = w['label'].value()
                    if rootcheck == "":
                        takesSet = w['label'].setValue("take1,take2,take3,take4,take5,take6,take7")
                        takes = w['label'].value()
                        Take1replace = takes.replace("take1",aa1)
                        w['label'].setValue(Take1replace)
                    else:
                        Take1replace = rootcheck.replace("take1",aa1)
                        w['label'].setValue(Take1replace)
                else:
                    print ""
            elif knob == self.Disable1:
                d1 = self.Disable1.value()
                n =nuke.allNodes()
                for t in n:
                    if "take1" in t['label'].value():
                        t['disable'].setValue(d1)                   
            elif knob == self.Float1:
                f1 = float(self.Float1.value())
                a1 = self.Array1.value()
                n =nuke.allNodes()
                for t in n:
                    if "take1" in t['label'].value():
                        t[a1].setValue(f1)
                        
                        
            elif knob == self.Take2:
                if nuke.ask("This will add selected nodes to Take2 group, cancel to abort"):           
                    n =nuke.selectedNodes()
                    aa2 = self.Array2.value()
                    if aa2 == "":
                        aa2="disable"
                        self.Array2.setValue(aa2)
                    w = nuke.toNode("root")
                    rootcheck = w['label'].value()
                    if rootcheck == "":
                        takesSet = w['label'].setValue("take1,take2,take3,take4,take5,take6,take7")
                    takes = w['label'].value()
                    Take2replace = takes.replace("take2",aa2)
                    w['label'].setValue(Take2replace)
                    for t in n:
                       t['label'].setValue('take2')
                       take2name =t['name'].value()
                       take2name=take2name[:10]
                       self.Take2.setLabel(take2name)
                else:
                    print ""                   
            elif knob == self.Disable2:
                d2 = self.Disable2.value()
                n =nuke.allNodes()
                for t in n:
                    if "take2" in t['label'].value():
                        t['disable'].setValue(d2)                   
            elif knob == self.Float2:
                f2 = float(self.Float2.value())
                a2 = self.Array2.value()
                n =nuke.allNodes()
                for t in n:
                    if "take2" in t['label'].value():
                        t[a2].setValue(f2)
                            
                            
            elif knob == self.Take3:
                if nuke.ask("This will add selected nodes to Take3 group, cancel to abort"):                
                    n =nuke.selectedNodes()
                    aa3 = self.Array3.value()
                    if aa3 == "":
                        aa3="disable"
                        self.Array3.setValue(aa3)
                    w = nuke.toNode("root")
                    rootcheck = w['label'].value()
                    if rootcheck == "":
                        takesSet = w['label'].setValue("take1,take2,take3,take4,take5,take6,take7")
                    takes = w['label'].value()
                    Take3replace = takes.replace("take3",aa3)
                    w['label'].setValue(Take3replace)
                    for t in n:
                       t['label'].setValue('take3')
                       take3name =t['name'].value()
                       take3name=take3name[:10]
                       self.Take3.setLabel(take3name)
                else:
                    print ""                   
            elif knob == self.Disable3:
                d3 = self.Disable3.value()
                n =nuke.allNodes()
                for t in n:
                    if "take3" in t['label'].value():
                        t['disable'].setValue(d3)                   
            elif knob == self.Float3:
                f3 = float(self.Float3.value())
                a3 = self.Array3.value()
                n =nuke.allNodes()
                for t in n:
                    if "take3" in t['label'].value():
                        t[a3].setValue(f3)
                            
                            
            elif knob == self.Take4:
                if nuke.ask("This will add selected nodes to Take4 group, cancel to abort"):           
                    n =nuke.selectedNodes()
                    aa4 = self.Array4.value()
                    if aa4 == "":
                        aa4="disable"
                        self.Array4.setValue(aa4)
                    w = nuke.toNode("root")
                    rootcheck = w['label'].value()
                    if rootcheck == "":
                        takesSet = w['label'].setValue("take1,take2,take3,take4,take5,take6,take7")
                    takes = w['label'].value()
                    Take4replace = takes.replace("take4",aa4)
                    w['label'].setValue(Take4replace)
                    for t in n:
                       t['label'].setValue('take4')
                       take4name =t['name'].value()
                       take4name=take4name[:10]
                       self.Take4.setLabel(take4name)
                else:
                    print ""                      
            elif knob == self.Disable4:
                d4 = self.Disable4.value()
                n =nuke.allNodes()
                for t in n:
                    if "take4" in t['label'].value():
                        t['disable'].setValue(d4)                   
            elif knob == self.Float4:
                f4 = float(self.Float4.value())
                a4 = self.Array4.value()
                n =nuke.allNodes()
                for t in n:
                    if "take4" in t['label'].value():
                        t[a4].setValue(f4)
                        
                            
            elif knob == self.Take5:
                if nuke.ask("This will add selected nodes to Take5 group, cancel to abort"):            
                    n =nuke.selectedNodes()
                    aa5 = self.Array5.value()
                    if aa5 == "":
                        aa5="disable"
                        self.Array5.setValue(aa5)
                    w = nuke.toNode("root")
                    rootcheck = w['label'].value()
                    if rootcheck == "":
                        takesSet = w['label'].setValue("take1,take2,take3,take4,take5,take6,take7")
                    takes = w['label'].value()
                    Take5replace = takes.replace("take5",aa5)
                    w['label'].setValue(Take5replace)
                    for t in n:
                       t['label'].setValue('take5')
                       take5name =t['name'].value()
                       take5name=take5name[:10]
                       self.Take5.setLabel(take5name)
                else:
                    print ""                      
            elif knob == self.Disable5:
                d5 = self.Disable5.value()
                n =nuke.allNodes()
                for t in n:
                    if "take5" in t['label'].value():
                        t['disable'].setValue(d5)                   
            elif knob == self.Float5:
                f5 = float(self.Float5.value())
                a5 = self.Array5.value()
                n =nuke.allNodes()
                for t in n:
                    if "take5" in t['label'].value():
                        t[a5].setValue(f5)
                            
                            

            elif knob == self.Take6:
                if nuke.ask("This will add selected nodes to Take6 group, cancel to abort"):            
                    n =nuke.selectedNodes()
                    aa6 = self.Array6.value()
                    if aa6 == "":
                        aa6="disable"
                        self.Array6.setValue(aa6)
                    w = nuke.toNode("root")
                    rootcheck = w['label'].value()
                    if rootcheck == "":
                        takesSet = w['label'].setValue("take1,take2,take3,take4,take5,take6,take7")
                    takes = w['label'].value()
                    Take6replace = takes.replace("take6",aa6)
                    w['label'].setValue(Take6replace)
                    for t in n:
                       t['label'].setValue('take6')
                       take6name =t['name'].value()
                       take6name=take6name[:10]
                       self.Take6.setLabel(take6name)
                else:
                    print ""                       
            elif knob == self.Low6:
                d6 = self.Low6.value()
                loval6 = float(self.lowVal6.value())
                hival6 = float(self.highVal6.value())
                array6 = self.Array6.value()
                memory = str([loval6,hival6])
                n =nuke.allNodes()
                for t in n:
                    h = t['label'].value()
                    if "take6" in h:
                        try:
                            kill = h.split("/")[1]
                            h = h.replace("/"+kill,"")
                        except:
                            print ""
                        t['label'].setValue(h+"/"+memory)
                        if d6 == 1:
                            t[array6].setValue(loval6)     
                        else:
                            t[array6].setValue(hival6)

     

            elif knob == self.Take7:
                if nuke.ask("This will add selected nodes to Take7 group, cancel to abort"):            
                    n =nuke.selectedNodes()
                    aa7 = self.Array7.value()
                    if aa7 == "":
                        aa7="disable"
                        self.Array7.setValue(aa7)
                    w = nuke.toNode("root")
                    rootcheck = w['label'].value()
                    if rootcheck == "":
                        takesSet = w['label'].setValue("take1,take2,take3,take4,take5,take6,take7")
                    takes = w['label'].value()
                    Take7replace = takes.replace("take7",aa7)
                    w['label'].setValue(Take7replace)
                    for t in n:
                       t['label'].setValue('take7')
                       take7name =t['name'].value()
                       take7name=take7name[:10]
                       self.Take7.setLabel(take7name)
                else:
                    print ""                       
            elif knob == self.Low7:
                d7 = self.Low7.value()
                loval7 = float(self.lowVal7.value())
                hival7 = float(self.highVal7.value())
                array7 = self.Array7.value()
                memory = str([loval7,hival7])
                n =nuke.allNodes()
                for t in n:
                    h = t['label'].value()
                    if "take7" in h:
                        try:
                            kill = h.split("/")[1]
                            h = h.replace("/"+kill,"")
                        except:
                            print ""
                        t['label'].setValue(h+"/"+memory)
                        if d7 == 1:
                            t[array7].setValue(loval7)     
                        else:
                            t[array7].setValue(hival7)

                                         

                        
            elif knob == self.Array1:        
                w = nuke.toNode("root")
                takesInfo = nuke.Root().knob('label').getValue()
                o1= takesInfo.split(",")[0]
                o2= takesInfo.split(",")[1]
                o3= takesInfo.split(",")[2]
                o4= takesInfo.split(",")[3]
                o5= takesInfo.split(",")[4]
                o6= takesInfo.split(",")[5]
                o7= takesInfo.split(",")[6]               
                aa1 = self.Array1.value()
                w['label'].setValue(aa1+","+o2+","+o3+","+o4+","+o5+","+o6+","+o7)              
            elif knob == self.Array2:        
                w = nuke.toNode("root")
                takesInfo = nuke.Root().knob('label').getValue()
                o1= takesInfo.split(",")[0]
                o2= takesInfo.split(",")[1]
                o3= takesInfo.split(",")[2]
                o4= takesInfo.split(",")[3]
                o5= takesInfo.split(",")[4]
                o6= takesInfo.split(",")[5]
                o7= takesInfo.split(",")[6]               
                aa2 = self.Array2.value()
                w['label'].setValue(o1+","+aa2+","+o3+","+o4+","+o5+","+o6+","+o7)                               
            elif knob == self.Array3:        
                w = nuke.toNode("root")
                takesInfo = nuke.Root().knob('label').getValue()
                o1= takesInfo.split(",")[0]
                o2= takesInfo.split(",")[1]
                o3= takesInfo.split(",")[2]
                o4= takesInfo.split(",")[3]
                o5= takesInfo.split(",")[4]
                o6= takesInfo.split(",")[5]
                o7= takesInfo.split(",")[6]               
                aa3 = self.Array3.value()
                w['label'].setValue(o1+","+o2+","+aa3+","+o4+","+o5+","+o6+","+o7)                               
            elif knob == self.Array4:        
                w = nuke.toNode("root")
                takesInfo = nuke.Root().knob('label').getValue()
                o1= takesInfo.split(",")[0]
                o2= takesInfo.split(",")[1]
                o3= takesInfo.split(",")[2]
                o4= takesInfo.split(",")[3]
                o5= takesInfo.split(",")[4]
                o6= takesInfo.split(",")[5]
                o7= takesInfo.split(",")[6]               
                aa4 = self.Array4.value()
                w['label'].setValue(o1+","+o2+","+o3+","+aa4+","+o5+","+o6+","+o7)                             
            elif knob == self.Array5:        
                w = nuke.toNode("root")
                takesInfo = nuke.Root().knob('label').getValue()
                o1= takesInfo.split(",")[0]
                o2= takesInfo.split(",")[1]
                o3= takesInfo.split(",")[2]
                o4= takesInfo.split(",")[3]
                o5= takesInfo.split(",")[4]
                o6= takesInfo.split(",")[5]
                o7= takesInfo.split(",")[6]               
                aa5 = self.Array5.value()
                w['label'].setValue(o1+","+o2+","+o3+","+o4+","+aa5+","+o6+","+o7)                              


            elif knob == self.Array6:        
                w = nuke.toNode("root")
                takesInfo = nuke.Root().knob('label').getValue()
                o1= takesInfo.split(",")[0]
                o2= takesInfo.split(",")[1]
                o3= takesInfo.split(",")[2]
                o4= takesInfo.split(",")[3]
                o5= takesInfo.split(",")[4]
                o6= takesInfo.split(",")[5]
                o7= takesInfo.split(",")[6]               
                aa6 = self.Array6.value()
                w['label'].setValue(o1+","+o2+","+o3+","+o4+","+o5+","+aa6+","+o7)

            elif knob == self.Array7:        
                w = nuke.toNode("root")
                takesInfo = nuke.Root().knob('label').getValue()
                o1= takesInfo.split(",")[0]
                o2= takesInfo.split(",")[1]
                o3= takesInfo.split(",")[2]
                o4= takesInfo.split(",")[3]
                o5= takesInfo.split(",")[4]
                o6= takesInfo.split(",")[5]
                o7= takesInfo.split(",")[6]               
                aa7 = self.Array7.value()
                w['label'].setValue(o1+","+o2+","+o3+","+o4+","+o5+","+o6+","+aa7)
                                
                
def addMassivePanel():
    myPanel = MassivePanel()
    return myPanel.addToPane()
paneMenu = nuke.menu('Pane')
paneMenu.addCommand('MassivePanel', addMassivePanel)
nukescripts.registerPanel( 'com.ohufx.MassivePanel', addMassivePanel)

