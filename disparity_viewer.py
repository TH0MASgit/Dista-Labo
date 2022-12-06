################################################################################
##          Calibration de camera
##      Fichier principal pour lancer une calibration de caméra avec stereo (ou sans)
##  Cet utilitaire recupere la liste des caméras disponibles et propose des options au travers d'un menu
##  Author : J. Coupez
##  Date : 10/12/2020
##  Version : 1.0
################################################################################

import cv2
import json
import re
import glob
import numpy as np
import subprocess
from config import *

from lib.DisparityProcessor import DisparityProcessor
from lib.DisparityDisplay import DisparityDisplay

args = parse_args()

def retrieveCameras():
    """
    Test the ports and returns a tuple with the available ports and resolution that are working.
    """
    is_working = True
    dev_port = 0
    working_ports = []
    error = 0
    while is_working:
        isFound = False
        try:
            process = subprocess.Popen(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            lineList = out.splitlines()
            i = 0
            pattern = "b'(.*?)'"

            while i < len(lineList):
                cameraName = lineList[i].decode("utf-8").replace(":", '')
                i += 1
                cameraPort = lineList[i].decode("utf-8").replace("\t", '')
                working_ports.append((cameraName, cameraPort))
                i += 1
                while i < len(lineList):
                    value = lineList[i].decode("utf-8")
                    i += 1
                    if len(value) == 0:
                        break
            is_working = False
        except RuntimeError as ex:
            is_working = True
        if is_working:
            #  v4l2 didn't worked, try the brute force
            try:
                camera = cv2.VideoCapture(dev_port)
                if camera is None or not camera.isOpened():
                    is_working = False
                else:
                    is_reading, img = camera.read()
                    w = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
                    h = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    if is_reading:
                        working_ports.append((f'Camera ({w}x{h})', dev_port))
                        print(f'..', end='')
                    camera.release()
            except RuntimeError as ex:
                error += 1
            finally:
                dev_port += 1

    if args.nerian:
        import PySpin
        # FLIR camera detection
        # Retrieve singleton reference to system object
        system = PySpin.System.GetInstance()
        # Retrieve list of cameras from the system
        cam_list = system.GetCameras()
        cam = None
        try:
            for i, cam in enumerate(cam_list):
                # Retrieve TL device nodemap and print device information
                nodemap = cam.GetTLDeviceNodeMap()
                # node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))
                cameraName = None
                node_device_name = PySpin.CStringPtr(nodemap.GetNode('DeviceModelName'))
                node_device_serial = PySpin.CStringPtr(nodemap.GetNode('DeviceSerialNumber'))
                if PySpin.IsAvailable(node_device_name) and PySpin.IsReadable(node_device_name):
                    cameraName = node_device_name.GetValue()
                if PySpin.IsAvailable(node_device_serial) and PySpin.IsReadable(node_device_serial):
                    cameraName = f'{cameraName} Serial : {node_device_serial.GetValue()}'
                dev_port = f'flir://{i}'
                if cameraName is not None:
                    working_ports.append((f'FLIR {cameraName}', dev_port))

        except RuntimeError as ex:
            print('Error while detecting FLIR camera',ex)
        finally:
            del cam
            # Clear camera list before releasing system
            cam_list.Clear()
            # Release system instance
            system.ReleaseInstance()

    return working_ports


def requestCamera():
    print(f'Détection des caméras..', end='')
    cameraList = retrieveCameras()
    print(f'Détection réussie !')
    print(f'Choisissez la/les caméras à utiliser :')
    for num, (name, port) in enumerate(cameraList):
        print(f'\t{num} : {port} ({name}) ')
    print(f'\tr : Relancer la detection')
    print(f'\tq : Quitter')
    cameraIndexes = []
    while len(cameraIndexes) == 0:
        try:
            print(f'\t=================')
            print(
                f'\tIndiquez le numéro de la caméra à calibrer.')
            print(f'\tCalibration Stéréo : séparez les numéro par une virgule, caméra gauche en premier.')
            print(f'\tPar exemple : 0,1')
            pickedValues = str(input(
                f'Numéro de caméra(s) (default:0) : ') or '0')
            if (pickedValues == 'r'):
                return requestCamera()
            if (pickedValues == 'q'):
                return 'q'
            if len(pickedValues) != 0:
                pickedValues = list(map(int, pickedValues.split(',')))
                for index in pickedValues:
                    cameraInfo = cameraList[index]
                    name, port = cameraInfo
                    cameraIndexes.append(port)
            print(f'\t==> Caméra utilisée : {cameraIndexes}')
        except ValueError:
            print(f'\t==> Mauvaise saisie, indiquez le chiffre de la caméra. Ex : 1')
            cameraIndexes = []
    return cameraIndexes



def requestConfigFile():
    configFile = None
    while configFile is None:
        fileNameList = np.sort(glob.glob(f'calibration/*.json'))
        print(f'\t==> Choisissez un fichier de configuration :')
        nbrFile = len(fileNameList)
        try:
            i = 0
            for i in range(nbrFile):
                print(f'\t\t {i} : {fileNameList[i]}')
            i = i + 1
            print(f'\t\t {i} : Autre...')
            index = str(input("Indiquez le numero du fichier de configuration : ") or f'{i}')

            index = int(index)
            if index == i:
                configFile = str(input(
                    "Indiquez le nom du fichier de configuration ( ex : calibration/SN123.json ) : ") or 'calibration/SNCARL.json')
            else:
                if index >= 0 and index < nbrFile:
                    configFile = fileNameList[index]
                else:
                    raise ValueError("Not in range")

            print(f'\t==> Fichier utilise : {configFile}')
        except ValueError:
            print(f'\t==> Mauvaise saisie. La valeur doit être un numero entre 0 et {nbrFile}')
            configFile = None
    return configFile


def requestResolution():
    resolution = None
    while resolution is None:
        try:
            resolution = str(input("Indiquez la resolution ( default:FHD) : ") or 'FHD')
            if resolution == "":
                raise ValueError("Not in list")

            print(f'\t==> Resolution de calibration : {resolution}')
        except ValueError:
            print(f'\t==> Mauvaise saisie. La valeur doit être 2K / FHD / HD / VGA ')
            resolution = None
    return resolution


if __name__ == '__main__':
    disparityProcessor = None
    disparityDisplay = None
    try:
        defaultSettings = None
        try:
            with open('disparity_settings.json') as json_file:
                defaultSettings = json.load(json_file)
        except IOError:
            defaultSettings = None

        useDefaultSetting = 'n'
        if defaultSettings is not None:
            print(f'Une configuration précédente a été detectée : {defaultSettings} ')
            useDefaultSetting = str(input("Voulez-vous utiliser cette configuration ? (Y/n , default:Y) : ") or 'Y')

        if useDefaultSetting != 'Y' and useDefaultSetting != 'y':
            # Asking for configuration
            defaultSettings = {}
            cameraIndexes = requestCamera()
            if cameraIndexes == 'q':
                exit()
            defaultSettings['cameraIndexes'] = cameraIndexes
            defaultSettings['configFileName'] = requestConfigFile()
            defaultSettings['resolution'] = requestResolution()
            defaultSettings['isCsiCam'] = args.csi or False

        disparityProcessor = DisparityProcessor(settings=defaultSettings)
        disparityDisplay = DisparityDisplay(disparityProcessor, settings=defaultSettings)
        disparityDisplay.saveConfiguration()

        disparityDisplay.run()

    finally:
        if disparityDisplay is not None:
            disparityDisplay.release()
        if disparityProcessor is not None:
            disparityProcessor.release()
