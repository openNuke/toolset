#!/usr/bin/python

"""
rmk 3/9/15 
Todo:
1) all file path requests should be a util functions in nxPipeline class? i.e. copyIt
2) separate out items in CAPITALS to JSON loaded as per project. (SLACKAUTH & CREDENTIAL_PATH & GOOGLEGROUP)
"""

################################## general
import nuke
import time
import datetime
import os
import os.path
import glob

################################## copyIt()
import nxPipeline
import nxProject
from nxPipeline import get_project
import shutil

################################## slack()
from slacker import Slacker # slack dependency: requests.py

################################## Google Drive
import pickle 
import httplib2 
import apiclient.discovery 
import apiclient.http 

######################################################################################################

class sumbit():
    def __init__(self):
        #SLACK VARS
        self.SLACKAUTH = 'xoxp-11630268487-11627592660-13686392289-747aa67a5f' #made https://api.slack.com/web ################### need to use OAuth2 as this only lasts a month with multiple users
        self.assetFilePath=""
        self.asSlackUser='true'
        self.slackUser=''
        self.slackMessage=""
        self.slackChannel=""
        # Google Drive VARS
        self.GOOGLEGROUP = ""
        self.CREDENTIAL_PATH = "//jupiter/Studio/23158_TBWA_LA_Slack_SF/COMP/00_nuke/00_pipeline/data/gDriveCredentials.plk" #generated from gDriveSetUp.py ###################
        self.credentials = ""
        self.uploadfile = ""
        self.mimetype = ""
        self.title = ""
        self.description = ""
        self.gDriveLink = ""
        
        
    def writeSlack(self):
        #https://api.slack.com/methods/chat.postMessage
        slack = Slacker(self.SLACKAUTH)
        channelList=slack.channels.list().__dict__['body']['channels']
        self.slackChannels=[]
        for x in channelList:
         self.slackChannels.append(x['name'])
        if not self.slackChannel in self.slackChannels:
           slack.channels.create(self.slackChannel)
        slack.chat.post_message('#'+self.slackChannel, self.slackMessage, username=self.slackUser, as_user=self.asSlackUser) 
        
##############################################################################################      only used for copyit()
    def getPreviewPath(self): ### COPIED FROM nxWrite
        path = self.assetFilePath #edited by rmk 3/9/15
        return path
        
    def copyIt(self,movPath):### COPIED FROM nxWrite
            nx_artist = nuke.root()['nx_artist'].getValue()                #edited by rmk 3/9/15
            if nx_artist.find(' ')>0:                                     #edited by rmk 3/9/15
                artistShort = nx_artist.replace(' ','_')
                artistShort = artistShort[0:artistShort.index('_')+4]         #edited by rmk 3/9/15
            else: #edited by rmk 3/9/15
                artistShort = nx_artist #edited by rmk 3/9/15
            todaysdate = datetime.date.today().strftime('%y%m%d')
            #WIPPath = nxPipeline.nxStudioRootDir() + get_project() + '/' + 'WIP' + '/' + todaysdate
            WIPPath = os.path.join(nxPipeline.nxStudioRootDir(), get_project(), 'WIP', todaysdate,artistShort).replace('\\', '/') #edited by rmk 3/9/15
            i = True

            if os.path.exists(str(WIPPath + '/' + movPath.rsplit('/')[-1])): #edited by rmk 3/9/15
                i = nuke.ask('WARNING.\n\nWIP Folder contains this version already.\n\nDo you want to overwrite it?')

            if i:
                self.createWIPDir(WIPPath)
            movPath=movPath.replace('/','\\')
            try:
                shutil.copy2(movPath, WIPPath) #edited by rmk 3/9/15
            except:
                nuke.message('Push failed! Sorry...')
            else:
                if nuke.ask('Success!\n\nDo you want to open the WIP Folder?'):
                    nxProject.openProjectFolders('wip')

    def getWriteNode(self): ### COPIED FROM nxWrite
        return nuke.thisGroup().node('Write1')

    def createWIPDir(self,dir): ### COPIED FROM nxWrite
        osdir = nuke.callbacks.filenameFilter( dir ) 
        try: 
            os.makedirs( osdir ) 
            return 
        except: 
            return
##############################################################################################      only used for copyit()  
    def nkMenuRun(self):
        
        thisN = nuke.selectedNodes()    
        if not len(thisN) == 1 or thisN[0].knob('nxWrite')== None:
            nuke.message('err.. please select a single nxWrite node.')
        else:
            thisN = thisN[0]
            thisN.begin()
            self.assetFilePath = nuke.toNode('Write1')['file'].getValue()
            nuke.root().begin()
            if  glob.glob(self.assetFilePath.replace('%04d','*')) ==[]:
                nuke.message('err.. nothing is rendered') # this should really check all frames are rendered
            else:
                dumbWriteName='Write'+str(int(time.time()))
                ################# this should be a util class #################
                nx_sequence = nuke.root()['nx_sequence'].getValue() 
                nx_sequenceEdit = nuke.root()['nx_sequence'].getValue().replace("_", "") # i do not like this!! pipeline weakness.
                nx_shot = nuke.root()['nx_shot'].getValue()
                nx_suffix = nuke.root()['nx_suffix'].getValue()
                nx_major_version = nuke.root()['nx_major_version'].getValue()
                nx_job = "LaSlack" ################### warning this is hardcoded for this project only (i dont know where this environment var is) ###################
                nx_artist = os.getenv('nexusid')
                ################# this should be a util class #################
                
                if nuke.ask(os.path.basename(self.assetFilePath)+'\nPublish to Nuke Studio?'):
                    # make write node for studio to link to #
                    dumbWrite = nuke.createNode('Write')
                    dumbWrite['name'].setValue(dumbWriteName)
                    dumbWrite['file'].setValue(self.assetFilePath)
                    # make knob for studio to link to write node #
                    try:
                        if nuke.root()['timeline_write_node']:
                            nuke.root()['timeline_write_node'].setValue(dumbWriteName)
                    except:
                        nuke.root().addKnob(nuke.String_Knob('timeline_write_node', 'Timeline_write_node(studio)', dumbWriteName))

                    # save the script for studio to use (without minor version) #
                    splitPath =  str.split(nuke.root().knob('name').value(),'_')
                    saveP='_'.join(splitPath[0:-1])+'_Studio.nk'
                    #thisN['disable'].setValue('1.0')
                    nuke.scriptSave(saveP)
                    #thisN['disable'].setValue('0.0')
                    nuke.delete(dumbWrite)

            
                # make slack strings
                self.slackChannel= nx_sequence + "_" + nx_shot
                notes=""
                self.slackUser = nx_artist
                self.asSlackUser = "'false'"
                if nuke.ask(os.path.basename(self.assetFilePath)+'\nPublish to Slack with notes?'):
                    p = nuke.Panel('artist release notes: new & todo')
                    p.addNotepad('notes', 'Done: ') 
                    ret = p.show()
                    notes=  p.value('notes')
                    self.assetFilePath.replace('.%04d.exr','.1001.exr') #this is so copy and paste into pdPlayer works. Todo: use a real found first frame
                    self.slackMessage = "*NUKE - "+nx_suffix+": "+os.path.split(self.assetFilePath)[1]+"*\nby: "+ nx_artist +"\n```<file:"+self.assetFilePath+"> (right click, copy) ```"+"\n"+notes
                    self.writeSlack()
                
                # Quicktime upload to google drive and/or WIP folder
                movPath = os.path.split(self.assetFilePath)[0]+"/"+nx_job+"_"+nx_sequenceEdit+ "_" + nx_shot+"_"+nx_suffix+"_"+"v"+nx_major_version+".mov"
                if os.path.isfile(movPath):                     
                    if nuke.ask(os.path.basename(movPath)+'\n Upload to Slack as web-movie?'):
                        self.uploadfile = movPath
                        self.mimetype = 'video/quicktime'
                        self.title = "COMP: "+os.path.split(movPath)[1]
                        self.description = nx_artist +" "+notes
                        self.writeGDrive()
                        self.slackMessage = self.gDriveLink
                        self.writeSlack()
                    if nuke.ask(os.path.basename(movPath)+' Copy to todays WIP folder?'): ################# this should be a util class
                        self.copyIt(movPath)
                        
                nuke.message('Released') 
            
        
    def getGDriveCred(self):
            fileObject = open(self.CREDENTIAL_PATH,'r')
            self.credentials = pickle.load(fileObject)  #generated from gDriveSetUp.py
            fileObject.close()
        
    def writeGDrive(self):

        self.getGDriveCred()
        # Create an authorized Drive API client.
        http = httplib2.Http()
        self.credentials.authorize(http)
        drive_service = apiclient.discovery.build('drive', 'v2', http=http)

        # Insert a file. Files are comprised of contents and metadata.
        # MediaFileUpload abstracts uploading file contents from a file on disk.
        media_body = apiclient.http.MediaFileUpload(
            self.uploadfile,
            mimetype=self.mimetype,
            resumable=True
        )
        # The body contains the metadata for the file.
        body = {
          'title': self.title,
          'description': self.description,
        }

        # Perform the request and print the result.
        new_file = drive_service.files().insert(body=body, media_body=media_body).execute()
        self.gDriveLink =  new_file['alternateLink']
         
