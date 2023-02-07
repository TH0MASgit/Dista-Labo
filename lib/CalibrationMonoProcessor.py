################################################################################
##          Classe CalibrationMonoProcessor
##      Calcule les paramètres de caméra pour une camera Mono
##  Author : J. Coupez
##  Date : 18/10/2020
##  Copyright Dista
##  Version : 1.0
################################################################################
import cv2
import numpy as np
import time

from lib.CalibrationAbstractProcessor import CalibrationAbstractProcessor, CALIBRATION_STEP, CALIBRATION_FLAG
from lib.Calibration import Calibration


class CalibrationMonoProcessor(CalibrationAbstractProcessor):

    def __init__(self, captureType, filePath, resolution, getChessBoardForFrame, onComputeProgress= None):
        CalibrationAbstractProcessor.__init__(self, captureType, filePath, resolution, getChessBoardForFrame, onComputeProgress)
        self.lastCameraMatrix = None
        self.lastDistCoeffs = None


    def compute(self, chessBoardGrid=None, fishEye=False, batchChessboardImageList=[]):
        batchChessboardImageList = self.getBatchChessboardImageList()

        super().compute(chessBoardGrid, fishEye, batchChessboardImageList)
        calibration = self.calibrateMono(batchChessboardImageList, fishEye)
        self.addCalibrationToList(calibration)
        self.isComputing = False
        return self.calibrationStep

    def isStereo(self):
        return False

    def calibrateMono(self, batchChessboardImageList, isFishEye=False):
        flags = CALIBRATION_FLAG.getFlag(self.calibrationStep)
        # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # flags = cv2.CALIB_FIX_K3 | cv2.CALIB_ZERO_TANGENT_DIST
        if isFishEye:
            # With fish eye camera, we should apply these params
            flags += cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K6
            # flags += cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K6 | cv2.CALIB_ZERO_TANGENT_DIST

        enabledChessboardImageList = []
        realCornersList = []
        distortedCornersList = []

        # Only take enable image
        for chessboardImage in batchChessboardImageList:
            if chessboardImage.getIsEnabled():
                enabledChessboardImageList.append(chessboardImage)
                realCornersList.append(chessboardImage.getRealCorners())
                distortedCornersList.append(chessboardImage.getDistortedCorners())
                self.imageSize = chessboardImage.getImageSize()
            if self.onComputeProgress is not None:
                self.onComputeProgress()
            time.sleep(0.01)


        # Build the real & distorted list from the enabled image
        # for chessboardImage in enabledChessboardImageList:
        #     realCornersList.append(chessboardImage.getRealCorners())
        #     distortedCornersList.append(chessboardImage.getDistortedCorners())
        #     self.imageSize = chessboardImage.getImageSize()


        if len(realCornersList) == 0:
            return None  # No corner to detect

        # Compute camera calibration
        rms, cameraMatrix, distCoeffs, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, perViewErrors = cv2.calibrateCameraExtended(
            realCornersList,
            distortedCornersList,
            self.imageSize,
            self.lastCameraMatrix,
            self.lastDistCoeffs,
            flags=flags)

        if not self.isComputing:
            # The computing was aborded somehow : discard the result
            return None

        self.lastCameraMatrix = np.copy(cameraMatrix)
        self.lastDistCoeffs = np.copy(distCoeffs)

        # print(
        #     f'step : {self.calibrationStep} - image : {len(enabledChessboardImageList)} - nbr error per view : {len(perViewErrors)}')

        # Save each Per View error in each used calibration image
        for i in range(len(perViewErrors)):
            perViewError = perViewErrors[i]
            chessboardImage = enabledChessboardImageList[i]
            chessboardImage.setRmsError(perViewError[0])

        coefficient = Calibration()
        coefficient.setRms(rms)
        coefficient.setPerViewErrors(perViewErrors)
        if self.captureType == 'left':
            coefficient.setCameraMatrixLeft(cameraMatrix)
            coefficient.setDistCoefLeft(distCoeffs)
        else:
            coefficient.setCameraMatrixRight(cameraMatrix)
            coefficient.setDistCoefRight(distCoeffs)

        self.isComputed = True
        return coefficient
