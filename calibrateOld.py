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
import os
import glob
import subprocess
from config import *

from lib.Calibrator import Calibrator

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
        except FileNotFoundError as ex:
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


def requestFishEye():
    fishEye = None
    while fishEye is None:
        try:
            fishEye = str(input("Les cameras ont-elle une lentille type 'Fish-Eye' (Y/n , default:n) : ") or 'n')
            if fishEye == 'Y' or fishEye == 'y':
                fishEye = True
            elif fishEye == 'N' or fishEye == 'n':
                fishEye = False
            else:
                raise ValueError("Not in list")
            print(f'\t==> Fish-Eye : {fishEye}')
        except ValueError:
            print(f'\t==> Mauvaise saisie. La valeur doit être "Y" ou "n" ')
            fishEye = None
    return fishEye


def requestSerial():
    serial = None
    while serial is None:
        try:
            serial = str(input("Indiquez un numéro de série pour cette configuration ( default:TEST) : ") or 'TEST')
            if serial == "":
                raise ValueError("Not in list")
            else:
                serial = f'SN{serial}'
            print(f'\t==> Nom du Fichier calibration : {serial}.conf')
        except ValueError:
            print(f'\t==> Mauvaise saisie. La valeur doit être non nulle ')
            serial = None
    return serial

def requestResolution():
    resolution = None
    while resolution is None:
        try:
            resolution = str(input("Indiquez la resolution de capture ( default:FHD) : ") or 'FHD')
            if resolution == "":
                raise ValueError("Not in list")

            print(f'\t==> Resolution de calibration : {resolution}')
        except ValueError:
            print(f'\t==> Mauvaise saisie. La valeur doit être 2K / FHD / HD / VGA ')
            resolution = None
    return resolution


def requestSquareSize():
    squareSize = None
    while squareSize is None:
        try:
            squareSize = str(input("Taille d\'un carreau du damier en mm (ex : 34.5) : ") or '10')
            squareSize = float(squareSize)
            print(f'\t==> Taille de carreaux : {squareSize}')
        except ValueError:
            print(f'\t==> Mauvaise saisie. La valeur doit être un nombre flotant ')
            squareSize = None
    return squareSize


def requestBoardShape():
    boardShape = None
    while boardShape is None:
        try:
            boardShape = str(
                input(
                    "Nombre de case du damier, horizontalement puis verticalement (ex : 15,10) - default : Autodetect  : ") or '')

            if len(boardShape) != 0:
                boardShape = list(map(int, boardShape.split(',')))
                if (len(boardShape) != 2):
                    raise ValueError('missing values')
                boardShape = (boardShape[0], boardShape[1])
            if (boardShape == ''):
                boardShape = None
                print(f'\t==> Nombre carreaux : AUTODETECTION')
                return boardShape
            else:
                print(f'\t==> Nombre carreaux : {boardShape}')
        except ValueError:
            print(f'\t==> Mauvaise saisie, indiquez un nombre de colonne et un nombre de ligne.')
            boardShape = None
    return boardShape


if __name__ == '__main__':
    calibrator = None
    try:
        defaultSettings = None
        try:
            with open('calibrate_settings.json') as json_file:
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
            defaultSettings['serial'] = requestSerial()
            defaultSettings['resolution'] = requestResolution()
            defaultSettings['fishEye'] = requestFishEye()
            defaultSettings['squareSize'] = requestSquareSize()
            defaultSettings['boardShape'] = requestBoardShape()
            defaultSettings['isCsiCam'] = args.csi or False

        clearPreviousPicture = False
        filePath = 'calibration/' + defaultSettings['serial']
        if os.path.exists(filePath):
            files = glob.glob(f'{filePath}/**/*.jpg', recursive=True)
            if len(files) > 0:
                print(f'{len(files)} image(s) ont été detectée(s) dans le repertoire {filePath} ')
                choice = str(input("Voulez-vous supprimer ces images ? (Y/n , default:n) : ") or 'n')
                if choice != 'n':
                    clearPreviousPicture = True
            else:
                clearPreviousPicture = True

        defaultSettings['clearPreviousPicture'] = clearPreviousPicture

        calibrator = Calibrator(settings=defaultSettings)
        calibrator.run()
    finally:
        if calibrator is not None:
            calibrator.release()
