import asyncio
import argparse
import recorder as obsRecorder

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OBS recording helper")

    parser.add_argument("-f", "--filename", default="Recording")
    parser.add_argument("-p", "--path", help="Path to use", default="/Users/sebastianschuchmann/Desktop/YoutubeRecordingTools/OBS-Recording")

    args = parser.parse_args()
    path = args.path
    fileName = args.filename

    recorder = obsRecorder.Recorder(path, fileName)
    asyncio.run(recorder.main())