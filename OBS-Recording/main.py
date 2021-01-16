import obsController as obs
import asyncio
import argparse
import keyboard
import os
import pathlib
import time

NEW_RECORDING_KEY = "cmd+1"
OVERRIDE_RECORDING_KEY = "cmd+3"
FILE_TYPE = ".mp4"

async def main(recordingPath, fileName):
    await obs.connect()
    await obs.setRecordingPath(recordingPath)

    createDeletionFolder(recordingPath)
    
    recordingIndex = setRecordingIndex(recordingPath, fileName)
    lastRecording = "Recording_10.mp4"

    while(not keyboard.is_pressed("esc")):
        recordingName = f"{fileName}_{recordingIndex}"
        recordingIndex, lastRecording = await checkRecordingKey(recordingName, recordingIndex, lastRecording)
        recordingIndex, lastRecording = await checkOverrideRecordingKey(recordingIndex, lastRecording)

def createDeletionFolder(path):
    folderAlreadyCreated = False
    for file in os.listdir():
        if(file.title() == "Deleted"):
            folderAlreadyCreated = True
    
    if(not folderAlreadyCreated): 
        os.mkdir(path + "/Deleted")
    
def setRecordingIndex(path, fileName):
    recordingIndex = 0
    
    for file in os.listdir(path):
       if file.startswith(fileName + "_"):
            recordingIndex += 1
            
    return recordingIndex

async def checkRecordingKey(fileName, recordingIndex, lastRecording):
    await obs.setFileName(fileName)

    if(keyboard.is_pressed(NEW_RECORDING_KEY)):
        await obs.startRecording()
        recordingIndex += 1

        while(keyboard.is_pressed(NEW_RECORDING_KEY)):
            pass

        lastRecording = fileName + FILE_TYPE
        print(f"Saved: {lastRecording}")
        await obs.stopRecording()
    
    return recordingIndex, lastRecording

async def checkOverrideRecordingKey(recordingIndex, lastRecording):
    if(keyboard.is_pressed(OVERRIDE_RECORDING_KEY)):

        for file in os.listdir():
            if(file.title().lower() == lastRecording.lower()):
                oldPath = str(pathlib.Path(file).absolute())
                newPath = oldPath.replace(lastRecording, ("Deleted/" + lastRecording.replace(FILE_TYPE, "_ " + str(time.time_ns()) + FILE_TYPE)))
                os.rename(oldPath, newPath)
                
                recordingIndex -= 1
                print(f"Found previous recording and moved it successfully")
        
        recordingName = f"{fileName}_{recordingIndex}"   
        await obs.setFileName(recordingName)     
        await obs.startRecording()
        
        while(keyboard.is_pressed(OVERRIDE_RECORDING_KEY)):
            pass
        
        lastRecording = recordingName + FILE_TYPE
        recordingIndex += 1
        
        print(f"Saved: {lastRecording}")
        await obs.stopRecording()
        
    return recordingIndex, lastRecording
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OBS recording helper")

    parser.add_argument("-f", "--filename", default="Recording")
    parser.add_argument("-p", "--path", help="Path to use", default="/Users/sebastianschuchmann/Desktop/YoutubeRecordingTools/OBS-Recording")

    args = parser.parse_args()
    path = args.path
    fileName = args.filename


    asyncio.run(main(path, fileName))
