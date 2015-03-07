#ExrMerge v1.0
#Desarrollado por Jose A. Enriquez (Zabander) 21-11-2014.
#hacked by Rafal 1)removed the write node 2)added stringSplit to tidy the name to remove version, show, shot
#todo change into class, do noBeauty, make gui, new group name

import os
import nuke
lista = []
add = 1
node = 0
node2 = 0
currentlayerName = ""
newdir = ""
dic = {}
mainBeautyLayer = 0
sGroup = []
isGroup = True
nIncrement = 1
splitString =''
removeFront=''
removeBack=''

#Permite seleccionar al passe beauty

def mainBeauty():
    global  removeFront,removeBack,splitString,mainBeautyLayer
    try:
        for nodes in lista:
            dic[nodes] = os.path.split(nodes.knob('file').value())[1]
        
        p = nuke.Panel('ExrMerge by Zabander')
        p.addEnumerationPulldown('BeautyLayer', dic.values()+['noBeauty'])
        p.addSingleLineInput('splitString', '_')
        p.addEnumerationPulldown('removeFront', '4 0 1 2 3 4 5 6 7')
        p.addEnumerationPulldown('removeBack', '2 0 1 2 3 4 5 6 7')
        ret = p.show()
        c = p.value('BeautyLayer')
        splitString =p.value('splitString')
        removeFront=p.value('removeFront')
        removeBack=p.value('removeBack')
        result = c.split("'")[1]
        for mKey, name in dic.items():
            if result == name:
                global mainBeautyLayer
                mainBeautyLayer = mKey
            else:
                pass
    except:
        
        pass

#Agrega los read nodes a la lista
def readNodes():
    try:
        a = nuke.selectedNodes()
        global isGroup
        if len(a) >= 2:
            global node
            for node in a:
                node.autoplace()
                if node.Class()  == "Read":
                   nodeName = node 
                   global lista
                   lista.append(nodeName)         
                else:
                     nuke.message("One of your nodes is not a read node: %s, it will be excluded." % node.name())
        
            mainBeauty()
            if mainBeautyLayer=='0':
                nuke.ask('err broken.. sorry')
            else:
                beautyIndex = lista.index(mainBeautyLayer)
            lista[beautyIndex], lista[0] = lista[0], lista[beautyIndex]   
            node = lista[0]  
            node.knob("selected").setValue(False)
        else:
            nuke.message ("Please select more than 1 node")
    except:
        isGroup = False
        


#Define el nombre del nodo a ser usado

def name(nodo):
    global currentlayerName
    path = nodo["file"].value()
    pathsplited =  path.split("/") 
    extentionsplited = pathsplited[-1].split(".")
    extentionsplited2 = extentionsplited[0].split("%")
    nameLayer = extentionsplited2[0]
    currentlayerName = str(nameLayer)


#Generar Shuffle y transferir atributos

def exrCompile (x, y):
    global node, sGroup,removeFront,removeBack,splitString

    s1 = nuke.nodes.ShuffleCopy()
    sGroup.append(s1)
    s1.autoplace()
    if  s1.canSetInput(0, node) and s1.canSetInput(1,node2):        
        s1.setInput( 0, node)
        s1.setInput( 1, node2)
        chan =  s1["in2"].value()
        s1["red"].setValue('red')
        s1["green"].setValue('green')
        s1["blue"].setValue('blue')
        s1["alpha"].setValue('alpha')
        name(node2)
        nameTemp=''
        listTemp=[]
        listTemp=str.split(currentlayerName,'_')
        for x in range(int(float(removeFront)),len(listTemp)-int(float(removeBack)),1):
            nameTemp= nameTemp+'_'+listTemp[x]
        currentlayerNameRed = str(nameTemp) + ".red"
        currentlayerNameGreen = str(nameTemp) + ".green"
        currentlayerNameBlue = str(nameTemp) + ".blue"
        currentlayerNameAlpha = str(nameTemp) + ".alpha"
         
        nuke.Layer(nameTemp,[currentlayerNameRed, currentlayerNameGreen,currentlayerNameBlue, currentlayerNameAlpha])
        s1["out"].setValue(nameTemp)              
        node = s1
        node.knob("selected").setValue(False)
        node2.knob("selected").setValue(False)  

    else:
        pass
    
#Evalua cada uno de los nodos de la lista y ejecuta exrCompile

def selector():
    for item in lista[1:]:
        global add
        global node2
        global mainBeautyLayer
        node2 = lista[add]


        exrCompile(node, node2)
        if add < len(lista):
            add =+ add + 1        
        else:
            add =+ add + 0
            pass
        if mainBeautyLayer=='0':
            pass
        item.knob("selected").setValue(False) 
    
def makeGroup(): 
    if len(lista) >= 2:
        global node, nIncrement
        for shuffleknob in sGroup:
            shuffleknob['selected'].setValue(True) 
        node = nuke.collapseToGroup(show=False)
        node.autoplace()
        gName = node.name()
        nuke.toNode(gName)["name"].setValue("Exr Merge %s" %nIncrement)
        nIncrement += 1
        #node.lock_connections(True)
    else:
        pass


def executeScript():
    readNodes()
    global lista, add, node, node2, currentlayerName, newdir, dic, mainBeautyLayer, sGroup, isGroup
    global splitString, removeFront,removeBack
    if len(lista) >= 2 and isGroup == True:
        selector()
        makeGroup()
       
    else:
        print "Process Stopped"
        pass
    
    #print nIncrement
    lista = []
    add = 1
    node = 0
    node2 = 0
    currentlayerName = ""
    newdir = ""
    dic = {}
    mainBeautyLayer = 0
    sGroup = []
    isGroup = True
