#ExrMerge v1.0
#Desarrollado por Jose A. Enriquez (Zabander) 21-11-2014.
#hacked by Rafal 1)removed the write node 2)added stringSplit to tidy the name to remove version, show, shot; 3) changed into class
#todo , do noBeauty, make gui, new group name, bring back option to create write, fix error traps (i.e. if read not selected); backStringSplit, clean ui

class channelMergeFromRead():
    def __init__(self):
    
        import os
        import nuke
        self.lista = []
        self.add = 1
        #self.node = 0
        self.node2 = 0
        self.currentlayerName = ""
        self.newdir = ""
        self.dic = {}
        self.mainBeautyLayer = 0
        self.sGroup = []
        self.isGroup = True
        self.nIncrement = 1
        self.splitString =''
        self.removeFront=''
        self.removeBack=''


    #Permite seleccionar al passe beauty

    def mainBeauty(self):
            #try:
            for nodes in self.lista:
                self.dic[nodes] = os.path.split(nodes.knob('file').value())[1]
            
            p = nuke.Panel('ExrMerge by Zabander')
            p.addEnumerationPulldown('BeautyLayer', self.dic.values()+['noBeauty'])
            p.addSingleLineInput('self.splitString', '_')
            p.addEnumerationPulldown('self.removeFront', '4 0 1 2 3 4 5 6 7 8 9 10')
            p.addEnumerationPulldown('self.removeBack', '2 0 1 2 3 4 5 6 7 8 9 10')
            ret = p.show()
            c = p.value('BeautyLayer')
            self.splitString =p.value('self.splitString')
            self.removeFront=p.value('self.removeFront')
            self.removeBack=p.value('self.removeBack')
            result = c.split("'")[1]
            for mKey, name in self.dic.items():
                if result == name:
                    self.mainBeautyLayer = mKey
                else:
                    pass
           #except:
            
           #pass

    #Agrega los read nodes a la self.lista
    def readNodes(self):
            #try:
            sNodes = nuke.selectedNodes()
            len(sNodes)
            if len(sNodes) >= 2:
                for node in sNodes:
                    node.autoplace()
                    if node.Class()  == "Read":
                       nodeName = node 
                       self.lista.append(nodeName)         
                    else:
                         nuke.message("One of your nodes is not a read node: %s, it will be excluded." % node.self.name()) 
                self.mainBeauty()
                if self.mainBeautyLayer=='0':
                    nuke.ask('err broken.. sorry')
                else:
                    beautyIndex = self.lista.index(self.mainBeautyLayer)
                self.lista[beautyIndex], self.lista[0] = self.lista[0], self.lista[beautyIndex]   
                self.node = self.lista[0]  
                self.node.knob("selected").setValue(False)
            else:
                nuke.message ("Please select more than 1 node")
            #except:
            # self.isGroup = False
            


    #Define el nombre del nodo a ser usado

    def name(self,node):
        path = node["file"].value()
        filename = os.path.basename(path)
        filenamesplit = filename.split(".")
        self.currentlayerName = str(self.splitString.join(filenamesplit[0:len(filenamesplit)-2]))


    #Generar Shuffle y transferir atributos

    def exrCompile (self,x, y):
        s1 = nuke.nodes.ShuffleCopy()
        self.sGroup.append(s1)
        s1.autoplace()
        if  s1.canSetInput(0, self.node) and s1.canSetInput(1,self.node2):        
            s1.setInput( 0, self.node)
            s1.setInput( 1, self.node2)
            chan =  s1["in2"].value()
            s1["red"].setValue('red')
            s1["green"].setValue('green')
            s1["blue"].setValue('blue')
            s1["alpha"].setValue('alpha')
            self.name(self.node2)
            nameTemp=''
            listTemp=[]
            listTemp=str.split(self.currentlayerName,'_')
            for x in range(int(float(self.removeFront)),len(listTemp)-int(float(self.removeBack)),1):
                nameTemp= nameTemp+'_'+listTemp[x]
            currentlayerNameRed = str(nameTemp) + ".red"
            currentlayerNameGreen = str(nameTemp) + ".green"
            currentlayerNameBlue = str(nameTemp) + ".blue"
            currentlayerNameAlpha = str(nameTemp) + ".alpha"
             
            nuke.Layer(nameTemp,[currentlayerNameRed, currentlayerNameGreen,currentlayerNameBlue, currentlayerNameAlpha])
            s1["out"].setValue(nameTemp)              
            self.node = s1
            self.node.knob("selected").setValue(False)
            self.node2.knob("selected").setValue(False)  

        else:
            pass
        
    #Evalua cada uno de los nodos de la self.lista y ejecuta exrCompile

    
    def selector(self):
        for item in self.lista[1:]:
            self.node2 = self.lista[self.add]


            self.exrCompile(self.node, self.node2)
            if self.add < len(self.lista):
                self.add =+ self.add + 1        
            else:
                self.add =+ self.add + 0
                pass
            if self.mainBeautyLayer=='0':
                pass
            item.knob("selected").setValue(False) 
        
    def makeGroup(self): 
        if len(self.lista) >= 2:
            for shuffleknob in self.sGroup:
                shuffleknob['selected'].setValue(True) 
            node = nuke.collapseToGroup(show=False)
            node.autoplace()
            gName = node.name()
            nuke.toNode(gName)["name"].setValue("Exr Merge %s" %self.nIncrement)
            self.nIncrement += 1
            #node.lock_connections(True)
        else:
            pass


    def executeScript(self):
        self.readNodes()
        if len(self.lista) >= 2 and self.isGroup == True:
            self.selector()
            self.makeGroup()
           
        else:
            print "Process Stopped"
            pass
     
channelMergeFromRead().executeScript()
