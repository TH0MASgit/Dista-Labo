################################################################################
##          Classe DisparityDisplay
##      Classe ui permet d'afficher une carte de disparite en temps reel
##  Author : J. Coupez
##  Date : 25/02/2021
##  Copyright Dista
##  Version : 1.0
################################################################################

import json
import cv2
import time

from lib.NetCam import NetCam
from lib.FpsCatcher import FpsCatcher
from lib.DisparityProcessor import DisparityProcessor


class DISPARITY_DISPLAYMODE:
    GRAY = 0
    COLOR = 1
    IMAGE = 2


class DisparityDisplay:
    DEFAULT_WINDOW_NAME = 'Disparity Display'
    PANEL_FONTFACE = cv2.FONT_HERSHEY_DUPLEX
    PANEL_FONTSCALE = 1.5
    PANEL_FONTTHICKNESS = 2
    PANEL_TEXT_COLOR = (255, 255, 255)

    def __init__(self, disparityProcessor: DisparityProcessor, settings={}):
        self.cameraIndexes = settings.get('cameraIndexes') or []
        self.configFileName = settings.get('configFileName') or 1
        self.resolution = settings.get('resolution') or 'FHD'
        self.isCsiCam = settings.get('isCsiCam') or False

        # Camera Rectification
        self.disparityProcessor = disparityProcessor
        self.depthMap = None

        # Display Params
        self.cameraLeft = None
        self.cameraLeftSetting = settings.get('leftCamera') or {}
        self.cameraRight = None
        self.cameraRightSetting = settings.get('rightCamera') or {}
        self.displayScaleFactor = 0.5
        self.mousePosition = None
        self.clickedPointList = []
        self.isDisplayDisparity = True
        self.displayMode = DISPARITY_DISPLAYMODE.COLOR
        self.cameraCurrentlyDisplayed = 'left'
        self.displayFps = None
        self.isKeyboardEnabled = False

        # Create rectified Camera
        if not self.disparityProcessor:
            self.isDisplayDisparity = False

    def saveConfiguration(self):
        # Save the calibration for the next run
        with open('disparity_settings.json', 'w') as outfile:
            json.dump({'cameraIndexes': self.cameraIndexes,
                       'configFileName': self.configFileName,
                       'resolution': self.resolution,
                       'isCsiCam': self.isCsiCam,
                       'leftCamera': {
                           'vFlip': self.cameraLeftSetting.get('vFlip') or False,
                           'hFlip': self.cameraLeftSetting.get('hFlip') or False,
                       },
                       'rightCamera': {
                           'vFlip': self.cameraRightSetting.get('vFlip') or False,
                           'hFlip': self.cameraRightSetting.get('hFlip') or False,
                       },
                       }, outfile, indent=4)

    ################ RENDERING METHODS ###############

    def run(self):
        self.displayFps = FpsCatcher()
        self.isKeyboardEnabled = True

        # Init camera Left
        if len(self.cameraIndexes) > 0:
            self.cameraLeft = self.initCamera(0, self.cameraLeftSetting)

        # If there is a right camera, same thing
        if len(self.cameraIndexes) > 1:
            self.cameraRight = self.initCamera(1, self.cameraRightSetting)
        else:
            self.cameraRight = self.cameraLeft

        while self.cameraLeft is not None and self.cameraLeft.isRunning():
            self.displayFps.compute()
            imageLeft = self.cameraLeft.readLeft()
            imageRight = self.cameraRight.readRight()
            finalPicture = self.renderDisparityMap(imageLeft, imageRight, self.displayMode)
            self.renderWindow(finalPicture)

            # Grab user input if needed
            self.listenKeyboard()

    def renderDisparityMap(self, imageLeft, imageRight, displayMode=DISPARITY_DISPLAYMODE.GRAY):
        finalPicture = None
        disparityMap = None
        cloud = None
        if self.disparityProcessor:
            rectifiedImageLeft, rectifiedImageRight = self.disparityProcessor.rectifyLeftRight(imageLeft, imageRight)
            cloud, disparityMap, self.depthMap = self.disparityProcessor.computeDisparityMap(rectifiedImageLeft,
                                                                                             rectifiedImageRight)

        if displayMode == DISPARITY_DISPLAYMODE.IMAGE or disparityMap is None:
            if self.cameraCurrentlyDisplayed == 'left':
                finalPicture = imageLeft
            else:
                finalPicture = imageRight
        elif displayMode == DISPARITY_DISPLAYMODE.GRAY:
            finalPicture = self.disparityProcessor.convertDisparityToGray(disparityMap)
        elif displayMode == DISPARITY_DISPLAYMODE.COLOR:
            finalPicture = self.disparityProcessor.convertDisparityToColor(disparityMap)

        return finalPicture

    ########## RENDERING METHODS ###########
    def renderWindow(self, finalPicture):

        # Display the final output
        shape = finalPicture.shape
        height = shape[0]
        width = shape[1]
        lastY = 10
        if self.displayFps is not None:
            #  Draw FPS
            lastY = self.drawText(finalPicture, f'{self.displayFps.fps:.2f} fps', y=lastY, alignH='left')
        #  Draw downscale
        lastY = self.drawText(finalPicture, f'Downscale : {self.disparityProcessor.disparityDownScale}', y=lastY,
                              alignH='left')
        if self.isKeyboardEnabled:
            #  Draw Controls
            lastY = self.drawText(finalPicture, f'C : Change rendering', y=10, alignH='right')
            if self.displayMode == DISPARITY_DISPLAYMODE.IMAGE:
                lastY = self.drawText(finalPicture, f's : select camera', y=lastY, alignH='right')
                lastY = self.drawText(finalPicture, f'{self.cameraCurrentlyDisplayed} camera', y=lastY + 30,
                                      alignH='right')
                lastY = self.drawText(finalPicture, f'h : invert Horizontal', y=lastY, alignH='right')
                lastY = self.drawText(finalPicture, f'v : invert Vertical', y=lastY, alignH='right')
                lastY = self.drawText(finalPicture, f'i : swap left <> right', y=lastY, alignH='right')

        if self.mousePosition is not None:
            self.renderPoint(finalPicture, self.mousePosition)
        if len(self.clickedPointList) > 0:
            for clickedPoint in self.clickedPointList:
                self.renderPoint(finalPicture, clickedPoint)

        width = int(width * self.displayScaleFactor)
        height = int(height * self.displayScaleFactor)
        finalPicture = cv2.resize(finalPicture, (width, height), interpolation=cv2.INTER_LINEAR)

        cv2.imshow(DisparityDisplay.DEFAULT_WINDOW_NAME + self.resolution, finalPicture)
        cv2.setMouseCallback(DisparityDisplay.DEFAULT_WINDOW_NAME + self.resolution, self.clickAndPoint)

    def renderPoint(self, finalPicture, point, fullCross=False):
        if self.disparityProcessor is None:
            return
        if self.depthMap is None:
            return
        if point is None:
            return

        x, y = point
        x = int(x)
        y = int(y)
        depth = round(self.disparityProcessor.getPointDepth(self.depthMap, point), 2)
        if fullCross:
            shape = finalPicture.shape
            height = shape[0]
            width = shape[1]
            # Horizontal line
            cv2.line(finalPicture, (0, y), (width, y), DisparityDisplay.PANEL_TEXT_COLOR, thickness=1, lineType=8)
            # Vertical line
            cv2.line(finalPicture, (x, 0), (x, height), DisparityDisplay.PANEL_TEXT_COLOR, thickness=1,
                     lineType=8)
        else:
            # Horizontal line
            cv2.line(finalPicture, (x - 10, y), (x + 10, y), DisparityDisplay.PANEL_TEXT_COLOR, thickness=1,
                     lineType=8)
            # Vertical line
            cv2.line(finalPicture, (x, y - 10), (x, y + 10), DisparityDisplay.PANEL_TEXT_COLOR, thickness=1,
                     lineType=8)

        self.drawText(finalPicture, f'{depth:.2f}m.', x=x, y=y + 30)
        return finalPicture

    def drawText(self, src, text, x=0, y=0, width=0, height=0, alignH=None, alignV=None, fontScale=None, color=None):
        fontScale = DisparityDisplay.PANEL_FONTSCALE if fontScale is None else fontScale
        color = DisparityDisplay.PANEL_TEXT_COLOR if color is None else color
        textSize = cv2.getTextSize(text,
                                   fontFace=DisparityDisplay.PANEL_FONTFACE,
                                   fontScale=fontScale,
                                   thickness=DisparityDisplay.PANEL_FONTTHICKNESS)
        (label_width, label_height), baseline = textSize
        shape = src.shape
        if width == 0:
            width = shape[1]
        if height == 0:
            height = shape[0]

        if alignH == 'center':
            x = int(x + (width - label_width) / 2)
        elif alignH == 'right':

            x = int(width - label_width)

        if alignV == 'center':
            y = int(y + (height + label_height) / 2)
        elif alignV == 'bottom':
            y = int(height - label_height / 2)
        else:
            y += label_height

        cv2.putText(src,
                    text,
                    (x, y),
                    fontFace=DisparityDisplay.PANEL_FONTFACE,
                    fontScale=fontScale,
                    thickness=DisparityDisplay.PANEL_FONTTHICKNESS,
                    color=color)
        return y + 15

    ################ INPUT METHODS ###############
    def clickAndPoint(self, event, x, y, flags, param):

        scaledX = x / self.displayScaleFactor
        scaledY = y / self.displayScaleFactor
        self.mousePosition = (scaledX, scaledY)
        if event == cv2.EVENT_LBUTTONUP:
            lastPoint = (scaledX, scaledY)
            self.clickedPointList.append(lastPoint)

    def listenKeyboard(self):
        key = cv2.waitKeyEx(100)
        if key != -1:
            if key == ord('q') or key == 27:  # q or ESC to quit
                self.release()
            elif key == 43 or key == 61:  # Numpad Plus key
                self.increaseResolution()
            elif key == 45:  # Numpad Minus key
                self.decreaseResolution()
            elif key == ord('c'):  # c key : color ON / OFF / image

                self.displayMode = (self.displayMode + 1) % 3
            elif key == ord('k'):  # k key : lower disparityDownScale
                if self.disparityProcessor.disparityDownScale > 1:
                    self.disparityProcessor.disparityDownScale -= 1
            elif key == ord('l'):  # l key : lower disparityDownScale
                self.disparityProcessor.disparityDownScale += 1
            elif key == ord('s'):  # s key : swap between image
                if self.cameraCurrentlyDisplayed == 'left':
                    self.cameraCurrentlyDisplayed = 'right'
                else:
                    self.cameraCurrentlyDisplayed = 'left'
            elif key == ord('i'):  # v key : Invert Camera
                if self.cameraLeft is not None and self.cameraRight is not None:
                    temp = self.cameraRight
                    # Swap cameras
                    self.cameraRight = self.cameraLeft
                    self.cameraLeft = temp
                    self.cameraIndexes = [self.cameraIndexes[1], self.cameraIndexes[0]]
                    # Swap settings
                    temp = self.cameraRightSetting
                    self.cameraRightSetting = self.cameraLeftSetting
                    self.cameraLeftSetting = temp
                    self.saveConfiguration()
            elif key == ord('h'):  # h key : horizontal flip of left camera
                if self.cameraCurrentlyDisplayed == 'left':
                    if self.cameraLeft is not None:
                        self.cameraLeft.invertHorizontal()
                        self.cameraLeftSetting['hFlip'] = self.cameraLeft.flipHorizontal
                        self.saveConfiguration()
                else:
                    if self.cameraRight is not None:
                        self.cameraRight.invertHorizontal()
                        self.cameraRightSetting['hFlip'] = self.cameraRight.flipHorizontal
                        self.saveConfiguration()
            elif key == ord('v'):  # v key : vertical flip of left camera
                if self.cameraCurrentlyDisplayed == 'left':
                    if self.cameraLeftSetting is not None:
                        self.cameraLeft.invertVertical()
                        self.cameraLeftSetting['vFlip'] = self.cameraLeft.flipVertical
                        self.saveConfiguration()
                else:
                    if self.cameraRightSetting is not None:
                        self.cameraRight.invertVertical()
                        self.cameraRightSetting['vFlip'] = self.cameraRight.flipVertical
                        self.saveConfiguration()

    def increaseResolution(self):
        self.displayScaleFactor += 0.1

    def decreaseResolution(self):
        self.displayScaleFactor -= 0.1
        if self.displayScaleFactor < 0.1:
            self.displayScaleFactor = 0.1

    ######### INIT & CLEANUP METHODS #################
    def initCamera(self, cameraIndex, cameraSetting):
        source = self.cameraIndexes[cameraIndex]
        isStereoCam = True
        if len(self.cameraIndexes) > 1:
            isStereoCam = False
        camera = NetCam(source=source, capture=self.resolution, isStereoCam=isStereoCam, isCsiCam=self.isCsiCam)
        if cameraSetting.get('vFlip'):
            camera.invertVertical()
        if cameraSetting.get('hFlip'):
            camera.invertHorizontal()
        return camera

    def release(self):
        if len(self.cameraIndexes) > 0:
            if self.cameraLeft:
                self.cameraLeft.release()
            if self.cameraRight:
                self.cameraRight.release()
        cv2.destroyWindow(DisparityDisplay.DEFAULT_WINDOW_NAME + self.resolution)

        self.cameraLeft = None
        self.cameraRight = None
