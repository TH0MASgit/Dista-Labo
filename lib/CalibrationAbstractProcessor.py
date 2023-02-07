################################################################################
##          Classe CalibrationProcessor
##      Calcule les paramètres de caméra
##  Author : J. Coupez
##  Date : 18/10/2020
##  Copyright Dista
##  Version : 1.0
################################################################################
import cv2
import glob
import numpy as np
import time


from lib.ChessboardImage import ChessboardImage

class CALIBRATION_STEP:
    STEP_1 = 0
    STEP_2 = 1
    STEP_3 = 2
    STEP_4 = 3
    ALL = 4


#  Chaque step de calibration va fixer deux parametres des equations
# La derniere etape prend tout les parametres calculé pour se rapprocher des bonne valeurs
class CALIBRATION_FLAG:
    @staticmethod
    def getFlag(step: CALIBRATION_STEP):
        return 0
        # switcher = {
        #     CALIBRATION_STEP.STEP_1: 0,
        #     CALIBRATION_STEP.STEP_2: cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_FIX_K1 + cv2.CALIB_FIX_K2 + cv2.CALIB_FIX_K3,
        #     CALIBRATION_STEP.STEP_3: cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_FIX_PRINCIPAL_POINT,
        #     CALIBRATION_STEP.STEP_3: cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_FIX_FOCAL_LENGTH,
        #     CALIBRATION_STEP.ALL: cv2.CALIB_USE_INTRINSIC_GUESS
        # }
        # return switcher.get(step, cv2.CALIB_USE_INTRINSIC_GUESS)


class CalibrationAbstractProcessor:
    BATCH_SIZE = 3

    def __init__(self, captureType, filePath,resolution, getChessBoardForFrame, onComputeProgress = None):

        self.captureType = captureType
        self.resolution = resolution
        self.getChessBoardForFrame = getChessBoardForFrame

        self.isComputing = False
        self.isComputed = False
        self.imageIndex = 0
        self.lastCalibrationBatch = 0

        # Used for calibration progress
        self.imagePath = f'{filePath}/{self.captureType}'
        self.chessboardImageList = []
        self.onComputeProgress = onComputeProgress

        # self.disabledImageIndexList = {}

        self.imageSize = (0, 0)

        # Final Coeficients
        self.calibrationStep = CALIBRATION_STEP.STEP_1
        self.cameraCoeficientList = []

    def resetImageIndex(self):
        self.chessboardImageList = self.reloadChessboardImageList()
        self.imageIndex = len(self.chessboardImageList)
        print(f'image index for {self.imagePath} : {self.imageIndex}')
        self.cameraCoeficientList = []
        # self.disabledImageIndexList = {}
        self.calibrationStep = int(self.imageIndex / CalibrationAbstractProcessor.BATCH_SIZE) - 1

        self.lastCalibrationBatch = 0

    def reloadChessboardImageList(self):
        fileNameList = np.sort(glob.glob(f'{self.imagePath}/*.jpg'))
        fullChessboardImageList = []
        for i in range(len(fileNameList)):
            fullChessboardImageList.append(ChessboardImage(fileNameList[i]))
        return fullChessboardImageList

    def getActivePictureList(self):
        imageList = []
        for chessboardImage in self.chessboardImageList:
            if chessboardImage.getIsEnabled():
                imageList.append(chessboardImage)
        return imageList

    def getBatchChessboardImageList(self):
        # On retourne toujours l'ensemble des images
        pictureNeeded = self.getPictureNeeded()
        imageList = self.chessboardImageList[0: pictureNeeded]

        return imageList

    def isReadyToCompute(self):
        if not self.isComputing:
            # We need a full batch to start processing
            pictureNeeded = self.getPictureNeeded()
            batchPictureList = self.getBatchChessboardImageList()
            if len(batchPictureList) >= pictureNeeded:
                # No more picture needed, we can launch the batch
                return True
        return False

    def getPictureNeeded(self):
        pictureNeeded = (self.calibrationStep + 1) * CalibrationAbstractProcessor.BATCH_SIZE
        if pictureNeeded < 3:
            return 3
        return pictureNeeded

    def generateNumbering(self, index):
        if index < 10:
            return f'00{index}'
        if index > 9:
            return f'0{index}'
        if index > 99:
            return f'{index}'

    def getImage(self, imageIndex):
        chessboardImage = self.getChessboardImage(imageIndex)
        if chessboardImage is not None:
            return chessboardImage.getImage()
        return None

    def getChessboardImage(self, imageIndex):
        if imageIndex >= 0 and imageIndex < len(self.chessboardImageList):
            chessboardImage = self.chessboardImageList[imageIndex]
            return chessboardImage
        return None

    def getImageIndex(self):
        return self.imageIndex

    def setImageIndex(self, imageIndex):
        self.imageIndex = imageIndex

    def disableImage(self, imageIndex):
        """
        Remove an image from the calibration ( image is not deleted, just flagged)
        :param imageIndex:
        """
        if imageIndex >= 0 and imageIndex < len(self.chessboardImageList):
            chessboardImage = self.chessboardImageList[imageIndex]
            if self.isStereo():
                chessboardImage[0].toggleEnabled()
                chessboardImage[1].toggleEnabled()
            else:
                chessboardImage.toggleEnabled()
        self.cameraCoeficientList = []
        self.calibrationStep = int(len(self.chessboardImageList) / CalibrationAbstractProcessor.BATCH_SIZE) - 1
        self.lastCalibrationBatch = 0
        self.isComputing = False

    def isImageDisabled(self, imageIndex):
        if imageIndex >= 0 and imageIndex < len(self.chessboardImageList):
            chessboardImage = self.chessboardImageList[imageIndex]
            return not chessboardImage.getIsEnabled()
        return False

    def savePicture(self, image):
        currentImageIndex = self.imageIndex + 1
        numbering = self.generateNumbering(currentImageIndex)
        path = f'{self.imagePath}/{numbering}_{self.captureType}.jpg'
        print(f'\tSaving picture {path}.')
        cv2.imwrite(path, image)
        self.setImageIndex(currentImageIndex)
        self.chessboardImageList.append(ChessboardImage(path))
        # # Remove the currentchessboard (when exist)
        # image = self.removeCurrentChessBoard(image.copy())
        # isAllCorners, corners, _ = self.getChessBoardForFrame(image, useFast=True)
        # if isAllCorners:
        #     # There is another chessboard
        #     self.savePicture(image)

    def removeCurrentChessBoard(self, image):
        # Look if there is more chessboard
        isAllCorners, corners, _ = self.getChessBoardForFrame(image, useFast=True)
        if isAllCorners:
            # Mask the current chessboard
            topLeftCorner = corners[0][0]
            topLeftCorner = (int(topLeftCorner[0]) - 10, int(topLeftCorner[1]) - 10)
            bottomRightCorner = corners[-1][0]
            bottomRightCorner = (int(bottomRightCorner[0]) + 10, int(bottomRightCorner[1]) + 10)
            # cv2.rectangle(overlay, pt1, pt2, (255, 255, 255), -1)
            try:
                color = np.random.randint(0, 255, size=(3,))
                color = (int(color[0]), int(color[1]), int(color[2]))
                image = cv2.rectangle(image, topLeftCorner, bottomRightCorner, tuple(color), -1)
            except Exception as e:
                print(e)

        return image

    def getCalibrationIndex(self):
        if len(self.cameraCoeficientList) == 0:
            return None

        return len(self.cameraCoeficientList) - 1

    def getProgressTotal(self):
        batchChessboardImageList = self.getBatchChessboardImageList()
        return len(batchChessboardImageList) * 2.1


    def compute(self, chessBoardGrid=None, fishEye=False, batchChessboardImageList=[]):
        self.isComputing = True
        self.isComputed = False
        if chessBoardGrid is not None:
            print( f'Calibration STEP {self.calibrationStep} : {len(batchChessboardImageList)} images, flags : {self.calibrationFlagToString()}.')
            self.computeCornerListForBatch(batchChessboardImageList, chessBoardGrid)

    def calibrationFlagToString(self):
        flags = CALIBRATION_FLAG.getFlag(self.calibrationStep)
        flagString = ""
        if flags & cv2.CALIB_USE_INTRINSIC_GUESS:
            flagString += " USE_INTRINSIC_GUESS"
        if flags & cv2.CALIB_FIX_PRINCIPAL_POINT:
            flagString += " FIX_PRINCIPAL_POINT"
        if flags & cv2.CALIB_FIX_FOCAL_LENGTH:
            flagString += " FIX_FOCAL_LENGTH"
        if flags & cv2.CALIB_FIX_K1:
            flagString += " FIX_K1"
        if flags & cv2.CALIB_FIX_K2:
            flagString += " FIX_K2"
        if flags & cv2.CALIB_FIX_K3:
            flagString += " FIX_K3"
        if flags & cv2.CALIB_ZERO_TANGENT_DIST:
            flagString += " ZERO_TANGENT_DIST"
        else:
            flagString += " NO FLAG"

        return flagString

    def addCalibrationToList(self, calibration):
        if calibration is None:
            return

        self.cameraCoeficientList.append(calibration)
        # Increase the batch count
        self.lastCalibrationBatch += 1
        self.calibrationStep += 1


    def getCoefficient(self, calibrationStep=None):
        if len(self.cameraCoeficientList) == 0:
            return None
        if calibrationStep is None or calibrationStep >= len(self.cameraCoeficientList):
            calibrationStep = len(self.cameraCoeficientList) - 1
        return self.cameraCoeficientList[calibrationStep]

    def isStereo(self):
        return False

    def computeCornerListForBatch(self, batchChessboardImageList, chessBoardGrid):

        for chessboardImage in batchChessboardImageList:
            if self.isStereo():
                calibrationLeftImage, calibrationRightImage = chessboardImage
                isComputed = self.computeCornerListForChessboardImage(calibrationLeftImage, chessBoardGrid)
                if isComputed:
                    isComputed = self.computeCornerListForChessboardImage(calibrationRightImage, chessBoardGrid)
                    if not isComputed:
                        calibrationLeftImage.disable()  # Both picture need to be computed
                else:
                    # We compute right picture if the left picture is properly computed
                    calibrationRightImage.disable()
            else:
                self.computeCornerListForChessboardImage(chessboardImage, chessBoardGrid)
            time.sleep(0.01)
            if self.onComputeProgress is not None:
                self.onComputeProgress()

    def computeCornerListForChessboardImage(self, chessboardImage, chessBoardGrid):
        if not chessboardImage.getIsEnabled():
            chessboardImage.resetCalibration()
            return False

        subPixCriteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # We get the corners
        frame = chessboardImage.getImage()
        isAllCorners, corners, grayScale = self.getChessBoardForFrame(frame, useFast=False)
        chessboardImage.setIsAllCorners(isAllCorners)
        if isAllCorners:
            # realCornersList.append(chessBoardGrid)
            # We have now all corners, we try to find subpixels
            # firstCorner = corners[0]
            # lastCorner = corners[-1]
            # (Ax,Ay) = (firstCorner[0],firstCorner[1])
            # (Bx,By) = (lastCorner[0],lastCorner[1])
            winSize = (10, 10)
            zeroZone = (2, 2)
            corners = cv2.cornerSubPix(grayScale, corners, winSize, zeroZone, subPixCriteria)
            chessboardImage.setRealCorners(chessBoardGrid)
            chessboardImage.setDistortedCorners(corners)
            chessboardImage.setRmsError(None)
            return True
        else:
            # Not all corners have been found, disable the picture
            chessboardImage.disable()
            return False

    def undistort(self, image, calibrationIndex=None):
        height, width = image.shape[:2]
        finalPicture = np.zeros(shape=(height, width, 3), dtype=np.uint8)
        calibration = self.getCoefficient(calibrationIndex)
        if calibration is not None:
            cameraMatrix = None
            distCoeffs = None
            if self.captureType == "left":
                cameraMatrix = calibration.getCameraMatrixLeft()
                distCoeffs = calibration.getDistCoefLeft()
            elif self.captureType == "right":
                cameraMatrix = calibration.getCameraMatrixRight()
                distCoeffs = calibration.getDistCoefRight()
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, distCoeffs, (width, height), 0,
                                                              (width, height))
            finalPicture = cv2.undistort(image, cameraMatrix, distCoeffs, None, newcameramtx)
            x, y, w, h = roi
            finalPicture = cv2.resize(finalPicture[y:y + h, x:x + w], (width, height), interpolation=cv2.INTER_CUBIC)
        return finalPicture
