#http://www.nukepedia.com/python/import/export/localisethreaded
import errno
import filecmp
import nuke
import os
import re
import threading
import time
import shutil
from subprocess import call

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


if nuke.env['WIN32']:
    # IMPORT WINDLL FOR FAST COPY UNDER WINDOWS (if available)
    windllAvailable = False
    try:
        from ctypes import windll
        windllAvailable = True
    except:
        pass

    # IMPORT SHUTIL IF WINDLL IS NOT AVAILABLE
    if not windllAvailable:
        import shutil



class LocaliseThreaded(object):
    '''
    Mimic nuke.localiseFile but make it threaded so it can run in the background

    To install put this into your menu.py:
    import LocaliseThreaded
    LocaliseThreaded.register()
    '''

    def __init__(self, fileDict, maxThreads=1):
        '''
        Threaded interface for copying files
        fileDict  -  dictionary where key is the name of the sequence (used for progress bar) and value is a list of files to be copied
        '''
        self.fileDict = fileDict
        self.cachePath = nuke.value('preferences.localCachePath')
        self.taskCount = len(self.fileDict)
        self.totalFileCount = sum([len(v) for v in self.fileDict.values()])
        self.progress = 0.0
        self.cachePath = nuke.value('preferences.localCachePath')
        self.finishedThreads = 0
        self.threadLimit = maxThreads
        self.threadLimiter = threading.BoundedSemaphore(self.threadLimit)


    def start(self):
        '''start copying files'''
        logger.debug('thread limit is: %s' % self.threadLimit)
        self.start = time.time()
        self.mainTask = nuke.ProgressTask('LOCALISING %s files' % self.totalFileCount)
        self.__updateMainTaskMessage()
        for seqName, fileList in self.fileDict.iteritems():
            thread = threading.Thread(name=seqName, target=self.copyFiles, args=(seqName, fileList))
            thread.start()

    def copyFiles(self, taskName, fileList):
        '''Copy all files'''
        self.threadLimiter.acquire()
        task = nuke.ProgressTask('%s (%s files)' % (taskName, len(fileList)))
        for i, filePath in enumerate(fileList):
            if task.isCancelled() or self.mainTask.isCancelled():
                break
            # COPY FILE
            self.copyFile(filePath, self.getTargetDir(filePath))
            # UPDATE LOCAL TASK
            task.setMessage('localising %s' % filePath)
            task.setProgress(int(float(i) / len(fileList) * 100))
            # UPDATE GLOBAL TASK
            self.progress += 1
            self.mainTask.setProgress(int(self.progress / self.totalFileCount * 100))
        self.reportFinishedThread()
        self.threadLimiter.release()


    def reportFinishedThread(self):
        '''Used to update the main task message and invoke the indicator on all nodes after localisation finsishes'''

        self.finishedThreads += 1
        self.__updateMainTaskMessage()
        if self.finishedThreads == self.taskCount:
            self.__forceUpdate()
            self.end = time.time()
            logger.debug('localising took %s seconds' % (self.end - self.start))


    def __updateMainTaskMessage(self):
        self.mainTask.setMessage('%s/%s tasks' % (self.finishedThreads, self.taskCount))

    def __forceUpdate(self):
        '''Silly workaround to update the node indicators. node.update() doesn't do the trick'''
        n = nuke.nodes.NoOp()
        nuke.delete(n)

    def copyFile(self, filePath, destPath):
        '''
        Copy filePath to destPath. destPath will be created if it doesn't exist.
        filePath will not be copied if the file already exists in destPath unless the local copy has an older time stamp
        '''
        # CREATE TARGET DIR IF NEED BE
        logger.debug('copying %s to %s' % (filePath, destPath))
        try:
            if not os.path.isdir(destPath):
                os.makedirs(destPath)
        except WindowsError:
            # NOT SURE WHY WINDOWS SOMETIMES SPEWS HERE
            pass
        # SKIP MISSING FRAMES
        if not os.path.isfile(filePath):
            logger.info('skipping missing frame %s' % filePath)
            return

        maxTries = 5 # NUMBER OF COPY ATTEMPTS IF STALE NFS HANDLE IS ENCOUNTERED
        localFile = os.path.join(destPath, os.path.basename(filePath))

        if os.path.isfile(localFile) and filecmp.cmp(filePath, localFile):
            # LOCAL FILE IS UP-TO-DATE - NOTHING TO DO
            pass
        else:
            # FILE DOES NOT EXISTS LOCALLY OR
            # LOCAL COPY SEEMS OUT OF SYNC - COPY IT AGAIN
            tryCount = 0
            while True:           
                try:
                    # TRY TO COPY FILE
                    #self.fastCopy(filePath, destPath)
                    self.fastCopy(filePath, localFile)
                    break
                except (OSError, IOError) as e:
                    if e.errno == errno.ESTALE:
                        # IF STALE NFS HANDLE IS ENCOUNTERED WAIT AND TRY AGAIN
                        if tryCount >= maxTries:
                            # TOO MANY UNSUCCESSFUL TRIES - GIVING UP
                            raise
                        time.sleep(.5)
                        tryCount += 1
                    else:
                        # SOME UNKNOWN ERROR OCCURRED
                        raise


    def fastCopy(self, srcPath, destPath):
        '''use a fast copy function based on OS'''
        
        ## COPY WITH INCREASED BUFFER SIZE
        with open(srcPath, 'rb') as srcFile:
            with open(destPath, 'wb') as destFile:
                shutil.copyfileobj(srcFile, destFile, 10 * 1024 * 1024)

    def getTargetDir(self, filePath):
        '''Get the target directory for filePath based on Nuke's cache preferences and localisation rules'''
        logger.debug('getting target directory')
        parts = filePath.split('/') # NUKE ALREADY CONVERTS BACK SLASHES TO FORWARD SLASHES ON WINDOWS
        logger.debug(filePath)
        logger.debug(parts)
        if not filePath.startswith('/'):
            logger.debug('localising with drive letter')
            # DRIVE LETTER
            driveLetter = parts[0]
            parts = parts [1:] # REMOVE DRIVE LETTER FROM PARTS BECAUSE WE ARE STORING IT IN PREFIX
            prefix =  driveLetter.replace(':', '_')
        else:
            # REPLACE EACH LEADING SLASH WITH UNDERSCORE
            logger.debug('localising without drive letter')
            # GET LEADING SLASHES
            slashCountRE = re.match('/+', filePath)
            slashCount = slashCountRE.span()[1]
            #slashCount = len([i for i in parts if not i])
            root = [p for p in parts if p][0]
            parts = parts[slashCount + 1:] # REMOVE SLASHES AND ROOT FROM PARTS BECAUSE WE ARE STORING THOSE IN PREFIX
            prefix = '_' * slashCount + root
        # RE-ASSEMBLE TO LOCALISED PATH
        parts.insert(0, prefix)
        parts = self.cachePath.split('/') + parts
        return '/'.join(parts[:-1]) # RETURN LOCAL DIRECTORY USING FORWARD SLASHES TO BE CONSISTENT WITH NUKE




def getFrameList(fileKnob, existingFilePaths):
    '''
    Return a list of frames that are part of the sequence that fileKnob is pointing to.
    If the file path is already in existingFilePaths it will not be included.
    '''
    node = fileKnob.node()
    originalCacheMode = node['cacheLocal'].value()
    node['cacheLocal'].setValue('never')

    #frameRange = nuke.FrameRange(node.firstFrame(), node.lastFrame(), 1)
    frameRange = nuke.FrameRange(node['first'].value(), node['last'].value(), 1)
    print 'frame range: {0}-{1}'.format(frameRange.first(), frameRange.last())
    outputContext = nuke.OutputContext()

    frameList = []
    # Cycle over views
    for viewNumber in xrange(outputContext.viewcount()):
        viewName = outputContext.viewname(viewNumber)
        # Skip "default" view
        if viewName not in nuke.views():
            continue

        # Set context to viewNumber
        outputContext.setView(viewNumber)

        # Cycle over frame range
        for frameNumber in frameRange:
            outputContext.setFrame(frameNumber)
            filePath = fileKnob.getEvaluatedValue(outputContext)
            if filePath not in existingFilePaths:
                frameList.append(filePath)

    node['cacheLocal'].setValue(originalCacheMode)
    return frameList

def localiseFileThreaded(readKnobList):
    '''Wrapper to duck punch default method'''

    sequenceCount = len(readKnobList)
    if sequenceCount > 1:
        p = nuke.Panel('Localiser (threaded)')
        knobName = 'concurrent copy tasks'
        p.addEnumerationPulldown(knobName, ' '.join([str(i+1) for i in xrange(min(nuke.THREADS, sequenceCount, 4))]))
        if p.show():
            maxThreads = int(p.value(knobName))
        else:
            return
    else:
        maxThreads = 1

    fileDict = {}
    allFilesPaths = []
    for knob in readKnobList:
        filePathList = getFrameList(knob, allFilesPaths)
        fileDict[knob.node().name()] = filePathList
        allFilesPaths.extend(filePathList)
    logger.debug('max threads from panel: %s' % maxThreads)
    localiseThread = LocaliseThreaded(fileDict, maxThreads)
    localiseThread.start()


def register():
    nuke.localiseFilesHOLD = nuke.localiseFiles #BACKUP ORIGINAL
    nuke.localiseFiles = localiseFileThreaded
