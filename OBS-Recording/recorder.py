import obsController as obs
import keyboard
import os
import pathlib
import time
import macNotifications

NEW_RECORDING_KEY = "cmd+1"
OVERRIDE_RECORDING_KEY = "cmd+3"
FILE_TYPE = ".mp4"
TIME_DELAY = 0.2

class Recorder:
    def __init__(self, recordingPath, fileName):
        self.notifier = macNotifications.Notificator()
        self.recordingPath = recordingPath
        self.fileName = fileName
        self.recordingIndex = 0
        
        self.setRecordingIndex()
        self.lastRecording = f"{self.fileName}_{self.recordingIndex}{FILE_TYPE}"
        self.createDeletionFolder()
    
    async def main(self):
        await obs.connect()
        await obs.setRecordingPath(self.recordingPath)

        while(not keyboard.is_pressed("esc")):
            await self.checkRecordingKey()
            await self.checkOverrideRecordingKey()
            time.sleep(TIME_DELAY)
                
    async def checkRecordingKey(self):
        if(keyboard.is_pressed(NEW_RECORDING_KEY)):
            await self.record(NEW_RECORDING_KEY)

    async def checkOverrideRecordingKey(self):
        if(keyboard.is_pressed(OVERRIDE_RECORDING_KEY)):
            self.RemoveLastRecording()
            await self.record(OVERRIDE_RECORDING_KEY, "Override")

    def RemoveLastRecording(self):
        for file in os.listdir():
            if(file.title().lower() == self.lastRecording.lower()):
                oldPath = str(pathlib.Path(file).absolute())
                newPath = oldPath.replace(self.lastRecording, ("Deleted/" + self.lastRecording.replace(FILE_TYPE, "_ " + str(time.time_ns()) + FILE_TYPE)))
                os.rename(oldPath, newPath)
                self.recordingIndex -= 1
                print(f"Found previous recording and moved it successfully")
        
    async def record(self, key, extraMessage = ""):
        recordingName = f"{self.fileName}_{self.recordingIndex}"  
        await obs.setFileName(recordingName)     
        await obs.startRecording()
        
        while(keyboard.is_pressed(key)):
            time.sleep(TIME_DELAY)
        
        self.lastRecording = recordingName + FILE_TYPE
        self.recordingIndex += 1
        
        print(f"Saved: {self.lastRecording}")
        self.notifier.notify("Recording finished!", f"{self.lastRecording} {extraMessage}")
        await obs.stopRecording() 
        
    def createDeletionFolder(self):
        folderAlreadyCreated = False
        for file in os.listdir():
            if(file.title() == "Deleted"):
                folderAlreadyCreated = True
        
        if(not folderAlreadyCreated): 
            os.mkdir(self.recordingPath + "/Deleted")
        
    def setRecordingIndex(self):
        self.recordingIndex = 0
        
        for file in os.listdir(self.recordingPath):
            if file.startswith(self.fileName + "_"):
                self.recordingIndex += 1
        
        print(f"Found {self.recordingIndex} existing recordings")
    

