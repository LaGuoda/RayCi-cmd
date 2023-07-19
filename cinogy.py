"""
<cinogy.py>

Command Line Interface For RayCi Beam Profiler Software.

Author: Guoda Laurinaviciute
Date: 2023 - 07 - 17

Description: The user can enable, set, update camera parameters from command line.
            The picture with specified parameters will be taken as a result.
"""

import xmlrpc.client
import time
import sys
import os
import argparse
import uuid
import random
import string


proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")
RayCi = proxy.RayCi

def selectCamera():
    LiveModeList = RayCi.LiveMode.list()
    for item in LiveModeList:
        if (item['sName'] != 'not connected'):
            tempCamera = RayCi.LiveMode.Camera.getIdCurrentCam(item['nIdDoc'])
            if (tempCamera['sName'] != 'Video Stream'):
                IdDocLive = item['nIdDoc']
                CameraItem = item
                OpenedLiveMode = False
                break
    if IdDocLive == None:
        CameraCount = RayCi.LiveMode.Camera.getIdCamListSize()
        if CameraCount == 0:
            raise Exception('No camera found.')
        CameraItem = RayCi.LiveMode.Camera.getIdCamListItem(-1, 0)
        IdDocLive = RayCi.LiveMode.open ( CameraItem['nIdCamHigh'], CameraItem['nIdCamLow'])
        print("Opened new live mode.")
        OpenedLiveMode = True
    print('Using camera', CameraItem['sName'])
    return (IdDocLive, OpenedLiveMode)


def generateRandom():
    """Helper function for random file names.

    Using uuid library a unique id is generated (uniqueId) and concatenated with a random 8 letter string (randomChars).

    Returns:
        str: randomly generated file name.
    """
    uniqueId = str(uuid.uuid4().hex)
    randomChars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    filename = f"{uniqueId}_{randomChars}"
    return filename

def createParser():
    """Creates a parser for command line input.

    Defines the flags for user input and specifies the help messages. Uses argparse library.

    Returns:
        argparse: parsed arguments.
    """
    parser = argparse.ArgumentParser(description = "Parser", formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument("-e","--exposure", type = str, default = "auto", help = 
            "Input exposure time value. *auto* for auto exposure. \n"
            "Float value for updating the exposure, for example 2.0 or 2. \n"
            "The value will be rounded to the closest value supported by RayCi software. \n \n")

    parser.add_argument("-g", "--gain", type = str, default = "auto", help =
            "\n"
            "Input gain value. *auto* for auto gain.\n"
            "Float value for updating the gain, for example 2.5x for 8Db gain. \n"
            "The value will be rounded to the closest value supported by RayCi software \n \n" )

    parser.add_argument("-fps", "--frames", type = str, default = "auto", help = 
            "Input frame rate value. *auto* for auto FPS. \n"
            "Measured in frames per second, range: (1.0, 14.0) \n"
            "The value will be rounded to the closest value supported by RayCi software \n \n")
        
    parser.add_argument("-c", "--clock", type = str, default = "False", help = 
            "Reduce pixel clock (true), don't reduce pixel clock (false) \n \n")

    parser.add_argument("-s", "--snapshot", type = str, default = "False", help = 
            "Input a name of the file you want to save your picture as. \n"
            "Files with the same name will be overriden. \n "
            "If you don't specify this flag, a picture won't be taken at all. \n"
            "Unless you use random name generator -r flag. \n \n")
    parser.add_argument("-d", "--directory", type = str, default = "False", help = 
            "Input a path to the directory you want to save your picture to. \n"
            "After using -s flag you don't need to enter the name of the file anymore. \n"
            "If not specified the picture will be saved to the default directory -> \n"
            "C:\CINOGY\RayCi Lite SDK\Python \n \n")
    parser.add_argument("-r", "--random", type = str, default = "False", help = 
            "If you don't want to name your pictures, set this flag to True. \n"
            "It will generate random filenames for your pictures. \n"
            "After setting this flag to True, you don't need to specify the snapshot -s flag. \n \n")
    parser.add_argument("-fh", "--fliph", type = str, default = "False", help = 
            "Set this flag to true if you want your image to be flipped horizontally. \n \n")
    parser.add_argument("-fv", "--flipv", type = str, default = "False", help = 
            "Set this flag to true if you want your image to be flipped vertically. \n \n")
    parser.add_argument("-rt", "--rotate", type = str, default = "False", help = 
            "Default value is set to False: no rotation. \n"
            "Input 'left' for left rotation. \n"
            "Input 'right' for right rotation \n \n")
    parser.add_argument("-hist", "--histogram", type = str, default = "False", help = 
            "If you want to obtain a histogram as well set this flag to 'true' :) \n \n")
    parser.add_argument("-ga", "--gaussian", type = str, default = "False", help = 
            "Set to 'true' to see the Gaussian distribution in the histogram")
    args = parser.parse_args()
    return args

def getExposure(exposureTimeArg):
    """Deals with exposure time input.

    Checks if exposure was set to auto. If not, tries to assign it a float value. If it doesn't succeed - a user is prompted with an error message.

    Args:
        exposureTimeArg (str): User input to the -e flag.

    Returns:
        bool/float: Returns False for auto exposure and a float value for manual exposure.
    """
    if exposureTimeArg == "auto":
        exposureTime = False
    else:
        try:
            exposureTime = float(exposureTimeArg)
        except ValueError:
            print("Invalid value for setting exposure time.")
            sys.exit(1)
    return exposureTime

def getGain(gainArg):
    """Deals with gain input.

    Checks if gain was set to auto. If not, tries to assign it a float value. If it doesn't succeed - a user is prompted with an error message.

    Args:
        gainArg (str): User input to the -g flag.

    Returns:
        bool/float: Returns False for auto gain and a float value for manual gain.
    """
    if gainArg == "auto":
        gain = False
    else:
        try: 
            gain = float(gainArg)
        except ValueError:
            print("Invalid value for setting the gain.")
            sys.exit(1)
    return gain

def getFPS(frameRateArg):
    """Deals with FPS input.

    Checks if frame rate was set to auto. If not, tries to assign it a float value. If it doesn't succeed - a user is prompted with an error message.

    Args:
        frameRateArg (str): User input to the -fps flag.

    Returns:
        bool/float: Returns False for auto frame rate and a float value for manual frame rate.
    """
    if frameRateArg == "auto":
        frameRate = False
    else:
        try:
            frameRate = float(frameRateArg)
        except ValueError:
            print("Invalid value for setting the frame rate.")
            sys.exit(1)
    return frameRate

def setRotate(rotate, idDoc):
    if rotate == "False":
        RayCi.LiveMode.Processing.Transform.Rotate.setMethod(idDoc, 0)
    elif rotate == "left" or rotate == "Left" or rotate == "l":
        RayCi.LiveMode.Processing.Transform.Rotate.setMethod(idDoc, 1)
    elif rotate == "right" or rotate == "Right" or rotate == "r":
         RayCi.LiveMode.Processing.Transform.Rotate.setMethod(idDoc, 2)
    else:
        print("Invalid input for rotate --rotate flag.")
        sys.exit(1)

def cleanStringInput(string):
    """Sorts out flexible user input.

    Checks user input and determine whether it should be True, False or invalid. This allows more flexibility.

    Args:
        string (str): User input.

    Returns:
        bool: True or False.
    """
    r = string
    if r == 'true' or r == 't' or r == 'True' or r == 'TRUE':
        s = True
    elif r == 'false' or r == 'f' or r == 'False' or r == "FALSE":
        s = False
    else: 
        print("Invalid value for specifying random filename flag. *true* to turn on the flag, *false* to turn it off.") 
        sys.exit(1)
    return s

def setExposure(exposureTime, idDoc):
    """Sets the exposure time.

    Sets the exposure time to auto or updates the exposure time to a value specified by the user.

    Args:
        exposureTime (float/bool): either float (a value to be updated) or bool (false for auto exposure).
        idDoc (int): the id of the current documment (camera).
    """
    if exposureTime == False:
        RayCi.LiveMode.Camera.ExposureTime.setAutomatic(idDoc, True)
    else:
        RayCi.LiveMode.Camera.ExposureTime.setAutomatic(idDoc, False)
        RayCi.LiveMode.Camera.ExposureTime.setExposureTime(idDoc, exposureTime)

def setGain(gain, idDoc):
    """Sets the gain.

    Sets the gain to auto or updates the gain to a value specified by the user.

    Args:
        gain (float/bool): either float (a value to be updated) or bool (false for auto gain).
        idDoc (int): the id of the current documment (camera).
    """
    if gain == False:
        RayCi.LiveMode.Camera.Gain.setAutomatic(idDoc, True)
    else:
        RayCi.LiveMode.Camera.Gain.setAutomatic(idDoc, False)
        RayCi.LiveMode.Camera.Gain.setGain(idDoc, gain)

def setFPS(frameRate, idDoc):
    """Sets the frame rate.

    Sets FPS to auto or updates  to a value it by the user.

    Args:
        frameRate (float/bool): either float (a value to be updated) or bool (false for auto FPS).
        idDoc (int): the id of the current documment (camera).
    """
    if frameRate ==  False:
        RayCi.LiveMode.Camera.FrameRate.setAutomatic(idDoc, True)
    else:
        RayCi.LiveMode.Camera.FrameRate.setAutomatic(idDoc, False)
        RayCi.LiveMode.Camera.FrameRate.setFrameRate(idDoc, frameRate)

def setPixelClock(pixelClockFlag, idDoc):
    """Sets reduce pixel clock flag.

    Sets the pixel clock flag to on or off (specified by the user).
    Args:
        pixelClockFlag (bool): True - reduces the pixel clock, False - doesn't reduce.
        idDoc (int): the id of the current documment (camera).
    """
    if pixelClockFlag == False:
        RayCi.LiveMode.Camera.PixelClock.setReduce(idDoc, False)
    elif pixelClockFlag == True:
        RayCi.LiveMode.Camera.PixelClock.setReduce(idDoc, True)

def setFlipHorizontally(fliph, idDoc):
    """Flips the screen horizontally if required.

    Args:
        fliph (bool): True - flips the image horizontally, False - doesn't.
        idDoc (int): the id of the current documment (camera).
    """
    RayCi.LiveMode.Processing.Transform.setHorizontalFlip(idDoc, fliph) 

def setFlipVertically(flipv, idDoc):
    """Flips the screen vertically if required.

    Args:
        flipv (bool): True - flips the image vertically, False - doesn't.
        idDoc (int): the id of the current documment (camera).
    """
    RayCi.LiveMode.Processing.Transform.setVerticalFlip(idDoc, flipv) 

def saveTheSnapshot(random, directoryArg, snapshotArg, idDoc):
    """Saves the snapshot according to directory and file name specified by the user.

    Sorts out the saving of the file. Checks if random name generation is required. Looks if the path is specified or should the file be saved to a default directory.

    Args:
        random (bool): flag for random file name generation.
        directoryArg (str): a user specified directory.
        snapshotArg (str): a user specified file name.
        idDoc (int): the id of the current documment (camera).
    """
    if directoryArg == "False":
        if random == True:
            fileName = generateRandom()
            saveTo = "C:\CINOGY\RayCi Lite SDK\Python" + "\\" + fileNames
            capture = RayCi.LiveMode.Measurement.newSnapshot(idDoc)
            RayCi.Single.saveAs(capture, saveTo, True)
            print("The picture has been successfully saved to: ", saveTo)
            return capture, saveTo
            
        elif snapshotArg == "False":
            print("No picture taken. Specify the file name (-s --snapshot) and/or the name of the directory (-d --directory)")
            sys.exit(1)
        elif snapshotArg != "False":
            saveTo = "C:\CINOGY\RayCi Lite SDK\Python" + "\\" + snapshotArg 
            capture = RayCi.LiveMode.Measurement.newSnapshot(idDoc)
            RayCi.Single.saveAs(capture, saveTo, True)
            print("The picture has been successfully saved to: ", saveTo)
            return capture, saveTo
    
    elif directoryArg != "False":
        if snapshotArg == "False":
            if random == True:
                fileName = generateRandom()
                saveTo = directoryArg + "\\" + fileName
                capture = RayCi.LiveMode.Measurement.newSnapshot(idDoc)
                RayCi.Single.saveAs(capture, saveTo, True)
                print("The picture has been successfully saved to: ", saveTo)
                return capture, saveTo
            else:
                print("No picture taken. Only specify the directory with -d/--directory flag. Use flag -s or --spanshot to set the name of the file.")
                sys.exit(1)
        elif snapshotArg != "False":
            saveTo = directoryArg + "\\" + snapshotArg
            capture = RayCi.LiveMode.Measurement.newSnapshot(idDoc)
            RayCi.Single.saveAs(capture,saveTo ,True)
            print("The picture has been successfully saved to: ", saveTo)
            return capture, saveTo

def makeHistogram(single, path, gaussian):
    path = path + "-histogram.png"
    RayCi.Single.CrossSection.Adjustment.adjust(single,0)

    if gaussian:
        RayCi.Single.Analysis.Settings.setMethod(single,3)

    RayCi.Single.CrossSection.View.exportView(single, 0, path, 1600, 1200, "CINOGY")
    print("The histogram has been successfully saved to: ", path)
    return


def main():
    """The main driver of this program.

    1. Gets all the arguments specified by the user.
    2. Initialises the camera.
    3. Sets the arguments specified by the user.
    4. Takes a picture of the laser beam with the specified parameters.
    """
    args = createParser()

    exposureTime = getExposure(args.exposure)
    gain = getGain(args.gain)
    frameRate = getFPS(args.frames)
    pixelClockFlag = cleanStringInput(args.clock)
    random = cleanStringInput(args.random)
    fliph = cleanStringInput(args.fliph)
    flipv = cleanStringInput(args.flipv)
    histogram = cleanStringInput(args.histogram)
    gaussian = cleanStringInput(args.gaussian)
  

    idDoc, liveMode = selectCamera()
 
    setExposure(exposureTime, idDoc)
    setGain(gain, idDoc)
    setFPS(frameRate, idDoc)
    setPixelClock(pixelClockFlag, idDoc)
    setFlipHorizontally(fliph, idDoc)
    setFlipVertically(flipv, idDoc)
    rotate = setRotate(args.rotate, idDoc)

    

    snapshotArg = args.snapshot
    directoryArg = args.directory
    single, filePath = saveTheSnapshot(random, directoryArg, snapshotArg, idDoc)

    if histogram:
        makeHistogram(single, filePath, gaussian)
 
    # RayCi.LiveMode.closeAll(True)
    RayCi.Single.closeAll(True)

    

if __name__ == "__main__":
    sys.exit(main())