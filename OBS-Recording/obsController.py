#region imports
import asyncio
import logging
import sys
import pickle
import os
import time

from obswsrc import OBSWS
from obswsrc.requests import StartRecordingRequest, StopRecordingRequest, SetRecordingFolderRequest, SetFilenameFormattingRequest
from obswsrc.logs import logger
import obswsrc.events
from obswsrc.events import RecordingStoppedEvent

logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
#endregion

VIDEO_FORMAT = ".mp4"

async def connect():
    print("Connecting to OBS-Server ...")

    while 1:
        try:
            async with OBSWS('localhost', 4444, "password") as obsws:
                print("Success ✔")
                return True
        except:
                print(".", end = '')
            
async def setRecordingPath(path):
    async with OBSWS('localhost', 4444, "password") as obsws:
        print("Recording Path set to " + path)
        response = await obsws.require(SetRecordingFolderRequest({'rec-folder': path }))

async def setFileName(filename):
    async with OBSWS('localhost', 4444, "password") as obsws:
        response = await obsws.require(SetFilenameFormattingRequest({'filename-formatting': filename }))

async def startRecording():
    async with OBSWS('localhost', 4444, "password") as obsws:
        print("Started recording")
        response = await obsws.require(StartRecordingRequest())

async def stopRecording():
    async with OBSWS('localhost', 4444, "password") as obsws:
        response = await obsws.require(StopRecordingRequest())
        print("Stopped Recording, waiting for finalization")
        while 1:
            try:
                event = await asyncio.wait_for(obsws.event(), 6)
                if event['update-type'] == 'RecordingStopped':
                    print('Recording finished')
                    break
            except asyncio.TimeoutError:
                print("Timeout - Recording, finished")
                break
                
async def saveListAsFile(itemlist):
    with open('RecordingsList', 'wb') as fp:
        pickle.dump(itemlist, fp)

async def resetList():
    itemlist = ["Recording-0"]
    with open('RecordingsList', 'wb') as fp:
        pickle.dump(itemlist, fp)

async def decreaseIndex():
    itemlist = await readList()
    itemlist.pop()
    await saveListAsFile(itemlist)

async def readList():
    if os.path.getsize('RecordingsList') > 0:
        with open ('RecordingsList', 'rb') as fp:
            return pickle.load(fp)
    else:
        return []

async def prepareRecordingAndStart(path="Recordings/"):
    #Generate Filename
    recordingList = await readList()
    currentIndex = len(recordingList)
    filename = f"Recording-{len(recordingList)}"
    recordingList.append(filename)
    await saveListAsFile(recordingList)

    await setFileName(filename)
    await setRecordingPath(os.path.abspath(path))
    await startRecording()
    print(f"Started {filename}")
    return path + filename + VIDEO_FORMAT, currentIndex


if __name__ == "__main__":
    import argparse

    #PARSING
    parser = argparse.ArgumentParser(description="Start and Stop OBS")
    parser.add_argument("StartStop", help="Start or Stop the recording", default="start")
    parser.add_argument("-p", "--path", help="Path to use", default="./Recordings/")

    args = parser.parse_args()
    path = args.path
    
    if args.StartStop.casefold() == "start":
        asyncio.run(prepareRecordingAndStart(path))
    else:
        asyncio.run(stopRecording())
