#ExrMerge v1.0 from nukepedia
#Desarrollado por Jose A. Enriquez (Zabander) 21-11-2014.
#hacked by Rafal 1)removed the write node 2)added stringSplit to tidy the name to remove version, show, shot; 3) changed into class 4) added folder method
#todo , do noBeauty, make gui, new group name, bring back option to create write, fix error traps (i.e. if read not selected); backStringSplit, clean ui
import os
import nuke
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
        self.readNodes=[]
        self.folderCount='2'


    #Permite seleccionar al passe beauty

    def mainBeauty(self):
            #try:
            for nodes in self.lista:
                self.dic[nodes] = os.path.split(nodes.knob('file').value())[1]          
            readNames = self.dic.values()
            readNames.sort()
            readNames.sort(key=len)
            p = nuke.Panel('channel merge read nodes')
            p.addEnumerationPulldown('BeautyLayer', readNames)
            p.addEnumerationPulldown('nameMethod', 'from_folder_name from_file_name')
            p.addEnumerationPulldown('folderCount', '2 0 1 2 3 4')
            p.addSingleLineInput('splitStringFileName', '_')
            p.addEnumerationPulldown('removeFrontFileName', '6 0 1 2 3 4 5 6 7 8 9 10')
            p.addEnumerationPulldown('removeBackFileName', '2 0 1 2 3 4 5 6 7 8 9 10')
            ret = p.show()
            c = p.value('BeautyLayer')
            self.folderCount =p.value('folderCount')
            self.nameMethod =p.value('nameMethod')
            self.splitString =p.value('splitStringFileName')
            self.removeFront=p.value('removeFrontFileName')
            self.removeBack=p.value('removeBackFileName')
            result = c.split("'")[1]
            for mKey, name in self.dic.items():
                if result == name:
                    self.mainBeautyLayer = mKey
                else:
                    pass
           #except:
            
           #pass

    #Agrega los read nodes a la self.lista
    def getReadNodes(self):
            #try:
            if self.readNodes ==0:
                sNodes = nuke.selectedNodes()
                self.readNodes = sNodes
            else:
                sNodes = self.readNodes
            len(sNodes)
            if len(sNodes) >= 2:
                for node in sNodes:
                    node.autoplace()
                    if node.Class()  == "Read":
                       nodeName = node 
                       self.lista.append(nodeName)         
                    else:
                         pass#nuke.message("One of your nodes is not a read node: %s, it will be excluded." % node.self.name()) 
                self.mainBeauty()
                if self.mainBeautyLayer=='0':
                    nuke.ask('err broken.. sorry')
                else:
                    beautyIndex = self.lista.index(self.mainBeautyLayer)
                self.lista[beautyIndex], self.lista[0] = self.lista[0], self.lista[beautyIndex]                 
                self.node = self.lista[0]  
                self.node.knob("selected").setValue(False)
            else:
                nuke.message ("Please select more than 1 node__")
            #except:
            # self.isGroup = False
            


    #Define el nombre del nodo a ser usado

    def name(self,node):
        path = node["file"].value()
        filename = os.path.basename(path)
        filenamesplit = filename.split(".")
        folderCount = int(self.folderCount)
        if self.nameMethod=='from_folder_name':
                filePathSplit = path.split("/")
                self.currentlayerName= ''.join(filePathSplit[len(filePathSplit)-(folderCount+1):-folderCount])
        if self.nameMethod=='from_file_name':
            del filenamesplit[-1]
            filenamesplit = '_'.join(filenamesplit)
            filenamesplit = filenamesplit.split(self.splitString) 
            self.currentlayerName = str(self.splitString.join(filenamesplit[int(self.removeFront):len(filenamesplit)-int(self.removeBack)]))
            nuke.tprint(filenamesplit)
            nuke.tprint(self.currentlayerName)


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
            #listTemp=str.split(self.currentlayerName,'_')
            listTemp=self.currentlayerName
            #for x in range(int(float(self.removeFront)),len(listTemp)-int(float(self.removeBack)),1):
                #nameTemp= nameTemp+'_'+listTemp[x]
            nameTemp="_"+listTemp
            nuke.tprint(nameTemp)
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
            nuke.selectAll()
            nuke.invertSelection()
            for shuffleknob in self.sGroup:
                shuffleknob['selected'].setValue(True) 
            #for shuffleknob in self.readNodes:
                #shuffleknob['selected'].setValue(True) 
            node = nuke.collapseToGroup(show=False)
            node['xpos'].setValue(self.mainBeautyLayer.xpos())
            node['ypos'].setValue(self.mainBeautyLayer.ypos()+100)
            #node.autoplace()
            #gName = node.name()
            #nuke.tprint((self.mainBeautyLayer))
            #nuke.toNode(gName)["name"].setValue("Exr Merge %s" %'hello')
            #self.nIncrement += 1
            #node.lock_connections(True)
        else:
            pass


    def run(self,readNodes=0):
        self.readNodes = readNodes
        self.readNodes =0
        #nuke.message(str(self.readNodes))
        self.getReadNodes()


        if len(self.lista) >= 2 and self.isGroup == True:
            self.selector()
            self.makeGroup()
           
        else:
            print "Process Stopped"
            pass
channelMergeFromRead().run()
