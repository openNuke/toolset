#ExrMerge v1.0
#Desarrollado por Jose A. Enriquez (Zabander) 21-11-2014.

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

#Permite seleccionar al passe beauty

def mainBeauty():
    try:
        for nodes in lista:
            dic[nodes] = os.path.split(nodes.knob('file').value())[1]
        
        p = nuke.Panel('ExrMerge by Zabander')
        p.addEnumerationPulldown('BeautyLayer', dic.values())
        
        ret = p.show()
        c = p.value('BeautyLayer')
        #print c
        result = c.split("'")[1]
        #print result
        #print dic.values()[1]
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
            beautyIndex = lista.index(mainBeautyLayer)
            lista[beautyIndex], lista[0] = lista[0], lista[beautyIndex]   
            node = lista[0]  
            node.knob("selected").setValue(False)
        else:
            nuke.message ("Please select more than 1 node")
    except:
        isGroup = False
        
#print lista


#Define el nombre del nodo a ser usado

def name(nodo):
    global currentlayerName
    path = nodo["file"].value()
    pathsplited =  path.split("/") 
    extentionsplited = pathsplited[-1].split(".")
    extentionsplited2 = extentionsplited[0].split("%")
    nameLayer = extentionsplited2[0]
    currentlayerName = str(nameLayer)
    #print currentlayerName

#Generar Shuffle y transferir atributos

def exrCompile (x, y):
    global node, sGroup
    s1 = nuke.nodes.ShuffleCopy()
    sGroup.append(s1)
    s1.autoplace()
    if  s1.canSetInput(0, node) and s1.canSetInput(1,node2):        
        s1.setInput( 0, node)
        s1.setInput( 1, node2)
        chan =  s1["in2"].value()
        #print s1
        s1["red"].setValue('red')
        s1["green"].setValue('green')
        s1["blue"].setValue('blue')
        s1["alpha"].setValue('alpha')
        name(node2)
        currentlayerNameRed = str(currentlayerName) + ".red"
        currentlayerNameGreen = str(currentlayerName) + ".green"
        currentlayerNameBlue = str(currentlayerName) + ".blue"
        currentlayerNameAlpha = str(currentlayerName) + ".alpha"
         
        nuke.Layer(currentlayerName,[currentlayerNameRed, currentlayerNameGreen,currentlayerNameBlue, currentlayerNameAlpha])
        s1["out"].setValue(currentlayerName)              
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
        node2 = lista[add]
        #print node.name()
        #print node2.name()

        exrCompile(node, node2)
        if add < len(lista):
            add =+ add + 1        
        else:
            add =+ add + 0
            pass
        
        item.knob("selected").setValue(False) 
    
   


#Crea un path para guardar el render automatico
def renderPath():
    global newdir
    totalPath = os.path.split(lista[0].knob("file").value())[0]
    totalName =  os.path.split(lista[0].knob("file").value())[1]
    splitExt = totalName.split(".")
    splitNum = splitExt[0].split("%")
    nameFile = splitNum[0] + "_%04d.exr"
   
    path = totalPath + "/" + "nukeCompiledExrFiles"  + "/" 
    newdir = os.path.join(path, nameFile)
    #print newdir
    if not os.path.exists(path): 
        os.makedirs(path)
    else:
        pass
    
#Crear nodo write con especificaciones
def renderOut():
    if len(lista) >= 2:
        a = nuke.createNode("Write")      
        a.connectInput(0, node)
        nuke.connectViewer(0, node)
        a["channels"].setValue("all")
        a["file_type"].setValue("exr")
        a.autoplace()
        renderPath()
        a["file"].setValue(newdir)
    else:
        pass



def makeGroup(): 
    if len(lista) >= 2:
        global node, nIncrement
        for shuffleknob in sGroup:
            shuffleknob['selected'].setValue(True) 
        node = nuke.collapseToGroup(show=False)
        node.autoplace()
        gName = node.name()
        #print gName
        nuke.toNode(gName)["name"].setValue("Exr Merge %s" %nIncrement)
        nIncrement += 1
        #node.lock_connections(True)
        #print node
    else:
        pass


def executeScript():
    readNodes()
    #print nIncrement
    global lista, add, node, node2, currentlayerName, newdir, dic, mainBeautyLayer, sGroup, isGroup
    print isGroup
    if len(lista) >= 2 and isGroup == True:
        selector()
        makeGroup()
        renderOut()
        print "Done"
       
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
    
    
    

executeScript()
