################################################################################
##          Classe CalibrationStereoProcessor
##      Calcul les paramètres stereo des caméras
##  Author : J. Coupez
##  Date : 18/10/2020
##  Copyright Dista
##  Version : 1.0
################################################################################
import cv2
import glob
import numpy as np
import json
import math
import time

from lib.CalibrationAbstractProcessor import CalibrationAbstractProcessor
from lib.Calibration import Calibration

from lib.ChessboardImage import ChessboardImage


class CalibrationStereoProcessor(CalibrationAbstractProcessor):

    def __init__(self, captureType, filePath, resolution, getChessBoardForFrame,
                 leftCalibrationProcessor: CalibrationAbstractProcessor,
                 rightCalibrationProcessor: CalibrationAbstractProcessor,
                 onComputeProgress=None):
        CalibrationAbstractProcessor.__init__(self, captureType, filePath, resolution, getChessBoardForFrame,
                                              onComputeProgress)
        self.leftCalibrationProcessor = leftCalibrationProcessor
        self.rightCalibrationProcessor = rightCalibrationProcessor

        # self.leftImagePath = f'{filePath}/stereo/*left.jpg'
        # self.rightImagePath = f'{filePath}/stereo/*right.jpg'

        # Used for calibration progress
        # self.imagePath = self.leftImagePath
        # self.leftDistortedCornersList = []
        # self.rightDistortedCornersList = []

        min_disp = 0
        numDisparities = 32
        blockSize = 5  # for SGBM in HD 5 is god # for BM 15 seems "ok" not concluding
        lambd = 10000  # 8000
        sigma = 5  # 1.5
        vis_mult = 1.0
        disp12MaxDiff = 200
        self.stereoSGBM = cv2.StereoSGBM_create(minDisparity=min_disp,
                                                numDisparities=numDisparities,  # 256
                                                blockSize=blockSize,
                                                P1=8 * 3 * blockSize * blockSize,
                                                P2=32 * 3 * blockSize * blockSize,  # 96
                                                # disp12MaxDiff=disp12MaxDiff,
                                                preFilterCap=63,  # 63
                                                #                                   uniquenessRatio=5,  #5
                                                # speckleWindowSize=50,
                                                # speckleRange=1,
                                                mode=cv2.STEREO_SGBM_MODE_HH)  # STEREO_SGBM_MODE_SGBM_3WAY  STEREO_SGBM_MODE_HH
        # self.stereoSGBM = cv2.StereoSGBM_create(minDisparity=-64,
        #                                         numDisparities=128,  # 256
        #                                         blockSize=11,
        #                                         P1=100,
        #                                         P2=1000,  # 96
        #                                         disp12MaxDiff=132,
        #                                         preFilterCap=0,  # 63
        #                                         uniquenessRatio=15,  # 5
        #                                         speckleWindowSize=1000,
        #                                         speckleRange=16,
        #                                         mode=cv2.STEREO_SGBM_MODE_HH)  # STEREO_SGBM_MODE_SGBM_3WAY  STEREO_SGBM_MODE_HH

        self.right_matcher = cv2.ximgproc.createRightMatcher(self.stereoSGBM)
        self.wls_filter = cv2.ximgproc.createDisparityWLSFilter(self.stereoSGBM)
        self.wls_filter.setLambda(lambd)
        self.wls_filter.setSigmaColor(sigma)

        self.map11 = None
        self.map12 = None
        self.map21 = None
        self.map22 = None
        self.Q = None

    def reloadChessboardImageList(self):
        pathLeft = f'{self.imagePath}/*_left.jpg'
        pathRight = f'{self.imagePath}/*_right.jpg'

        leftFileNameList = np.sort(glob.glob(pathLeft))
        rightFileNameList = np.sort(glob.glob(pathRight))
        fullChessboardImageList = []
        for i in range(len(leftFileNameList)):
            calibTuple = (ChessboardImage(leftFileNameList[i]), ChessboardImage(rightFileNameList[i]))
            fullChessboardImageList.append(calibTuple)
        return fullChessboardImageList


    def compute(self, chessBoardGrid=None, fishEye=False, batchChessboardImageList=[]):
        batchChessboardImageList = self.getBatchChessboardImageList()

        super().compute(chessBoardGrid, fishEye, batchChessboardImageList)
        # Calibrate stereo
        calibration = self.calibrateStereo(batchChessboardImageList, fishEye)
        self.addCalibrationToList(calibration)
        self.isComputing = False

        return self.calibrationStep

    def isImageDisabled(self, imageIndex):
        if imageIndex >= 0 and imageIndex < len(self.chessboardImageList):
            calibrationLeftImage, _ = self.chessboardImageList[imageIndex]
            return not calibrationLeftImage.getIsEnabled()
        return False

    def savePicture(self, imageLeft, imageRight):
        currentImageIndex = self.imageIndex + 1
        numbering = self.generateNumbering(currentImageIndex)
        pathLeft = f'{self.imagePath}/{numbering}_left.jpg'
        pathRight = f'{self.imagePath}/{numbering}_right.jpg'
        cv2.imwrite(pathLeft, imageLeft)
        cv2.imwrite(pathRight, imageRight)
        self.setImageIndex(currentImageIndex)
        self.chessboardImageList.append((ChessboardImage(pathLeft), ChessboardImage(pathRight)))
        print(f'\tSaving picture {pathLeft}.')
        print(f'\tSaving picture {pathRight}.')

    def addCalibrationToList(self, calibration):
        super().addCalibrationToList(calibration)
        results = []
        for calibrationResult in self.cameraCoeficientList:
            results.append(calibrationResult.toJSON())
        with open(f'{self.imagePath}/calibrationresult.json', 'w') as outfile:
            json.dump({'results': results}, outfile, indent=4)

    def getImage(self, imageIndex, side=None):
        calibrationLeftImage, calibrationRightImage = self.getChessboardImage(imageIndex)
        if calibrationLeftImage is not None and calibrationRightImage is not None:
            if side == 'left':
                return calibrationLeftImage.getImage()
            elif side == 'right':
                return calibrationRightImage.getImage()
            else:
                return np.concatenate((calibrationLeftImage.getImage(), calibrationRightImage.getImage()), axis=1)
        return None

    def isStereo(self):
        return True

    def calibrateStereo(self, batchChessboardImageList, isFishEye=False):
        # If both camera left & right have been computed, we can compute the stereo with the right coefficients.

        flags = cv2.CALIB_FIX_INTRINSIC | \
                cv2.CALIB_USE_INTRINSIC_GUESS | \
                cv2.CALIB_FIX_FOCAL_LENGTH | \
                cv2.CALIB_ZERO_TANGENT_DIST
        if isFishEye:
            flags += cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K6

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)

        # Compute stereo calibration
        leftCoef = self.leftCalibrationProcessor.getCoefficient() or None
        rightCoef = self.rightCalibrationProcessor.getCoefficient() or None

        if leftCoef is None or rightCoef is None:
            return

        cameraMatrixLeft = leftCoef.getCameraMatrixLeft()
        distCoefLeft = leftCoef.getDistCoefLeft()
        cameraMatrixRight = rightCoef.getCameraMatrixRight()
        distCoefRight = rightCoef.getDistCoefRight()

        enabledChessboardImageList = []
        realCornersList = []
        leftDistortedCornersList = []
        rightDistortedCornersList = []
        self.imageSize = (0, 0)

        # Only take enable image
        for chessboardImage in batchChessboardImageList:
            calibrationLeftImage, _ = chessboardImage
            if calibrationLeftImage.getIsEnabled():
                enabledChessboardImageList.append(chessboardImage)
                calibrationLeftImage, calibrationRightImage = chessboardImage
                realCornersList.append(calibrationLeftImage.getRealCorners())
                leftDistortedCornersList.append(calibrationLeftImage.getDistortedCorners())
                rightDistortedCornersList.append(calibrationRightImage.getDistortedCorners())
                self.imageSize = calibrationLeftImage.getImageSize()
            if self.onComputeProgress is not None:
                self.onComputeProgress()
            time.sleep(0.01)

        # Build the real & distorted list from the enabled image
        # for chessboardImage in enabledChessboardImageList:
        #     calibrationLeftImage, calibrationRightImage = chessboardImage
        #     realCornersList.append(calibrationLeftImage.getRealCorners())
        #     leftDistortedCornersList.append(calibrationLeftImage.getDistortedCorners())
        #     rightDistortedCornersList.append(calibrationRightImage.getDistortedCorners())
        #     self.imageSize = calibrationLeftImage.getImageSize()

        if len(realCornersList) == 0:
            return None  # No corner to detect

        R, T = None, None
        rms, M1, d1, M2, d2, R, T, E, F, perViewErrors = cv2.stereoCalibrateExtended(
            realCornersList,
            leftDistortedCornersList,
            rightDistortedCornersList,
            cameraMatrixLeft,
            distCoefLeft,
            cameraMatrixRight,
            distCoefRight,
            self.imageSize,
            R, T,
            criteria=criteria, flags=flags)

        # Save each Per View error in each used calibration image
        for i in range(len(perViewErrors)):
            perViewError = perViewErrors[i]
            calibrationLeftImage, calibrationRightImage = enabledChessboardImageList[i]
            calibrationLeftImage.setRmsError(perViewError[0])
            calibrationRightImage.setRmsError(perViewError[0])

        # On extrait la distance entre les deux lentilles
        baseline = T[0][0]
        baseline = baseline * 1000

        calibration = Calibration()
        calibration.setRms(rms)
        calibration.setPerViewErrors(perViewErrors)
        calibration.setBaseline(baseline)
        calibration.setImageSize(self.imageSize)
        calibration.setResolution(self.resolution)
        calibration.setCameraMatrixLeft(cameraMatrixLeft)
        calibration.setDistCoefLeft(distCoefLeft)
        calibration.setCameraMatrixRight(cameraMatrixRight)
        calibration.setDistCoefRight(distCoefRight)
        calibration.setT(T)
        calibration.setR(R)

        # self.coefficient.generateCoefficientString("LEFT_CAM", self.resolution, M1, d1)
        # self.coefficient.generateCoefficientString("RIGHT_CAM", self.resolution, M2, d2)

        self.isComputed = True
        return calibration

    def getDisparityMaps(self):

        if self.map11 is None:
            leftCoef = self.leftCalibrationProcessor.getCoefficient()
            rightCoef = self.leftCalibrationProcessor.getCoefficient()
            stereoCoef = self.getCoefficient()
            if not leftCoef or not rightCoef or not stereoCoef:
                return None

            cameraMatrix_left = leftCoef.getCameraMatrixLeft()
            distCoeffs_left = leftCoef.getDistCoefLeft()
            cameraMatrix_right = rightCoef.getCameraMatrixRight()
            distCoeffs_right = rightCoef.getDistCoefRight()
            R = stereoCoef.getR()
            T = stereoCoef.getT()
            width, height = self.imageSize
            self.R1, self.R2, self.P1, self.P2, self.Q = cv2.stereoRectify(cameraMatrix1=cameraMatrix_left,
                                                                           distCoeffs1=distCoeffs_left,
                                                                           cameraMatrix2=cameraMatrix_right,
                                                                           distCoeffs2=distCoeffs_right,
                                                                           R=R, T=T,
                                                                           alpha=0,
                                                                           imageSize=(width, height),
                                                                           newImageSize=(width, height))[0:5]
            self.map11, self.map12 = cv2.initUndistortRectifyMap(cameraMatrix_left, distCoeffs_left, self.R1, self.P1,
                                                                 (width, height), cv2.CV_32FC1)
            self.map21, self.map22 = cv2.initUndistortRectifyMap(cameraMatrix_right, distCoeffs_right, self.R2, self.P2,
                                                                 (width, height), cv2.CV_32FC1)

        return self.map11, self.map12, self.map21, self.map22

    def computeDisparityMap(self, imageLeft, imageRight, isActif=False):
        finalPicture = None

        downscale = 1

        map11, map12, map21, map22 = self.getDisparityMaps()
        if map11 is None:
            return None

        left_frame_rect = cv2.remap(imageLeft, map11, map12, interpolation=cv2.INTER_LINEAR)
        right_frame_rect = cv2.remap(imageRight, map21, map22, interpolation=cv2.INTER_LINEAR)

        # if isActif:
        #     left_frame_rect = cv2.cvtColor(left_frame_rect, cv2.COLOR_BGR2GRAY)  #
        #     right_frame_rect = cv2.cvtColor(right_frame_rect, cv2.COLOR_BGR2GRAY)

        # n_width = int(left_frame_rect.shape[1] * 1 / downscale)
        # n_height = int(left_frame_rect.shape[0] * 1 / downscale)
        # left_frame_rect_down = cv2.resize(left_frame_rect, (n_width, n_height))
        # right_frame_rect_down = cv2.resize(right_frame_rect, (n_width, n_height))

        # if isActif:
        #     left_frame_rect = cv2.medianBlur(left_frame_rect, 3)  # 3
        #     right_frame_rect = cv2.medianBlur(right_frame_rect, 3)

        left_frame_rect_down = left_frame_rect
        right_frame_rect_down = right_frame_rect
        left_disp = self.stereoSGBM.compute(cv2.UMat(left_frame_rect_down), cv2.UMat(right_frame_rect_down))
        right_disp = self.right_matcher.compute(cv2.UMat(right_frame_rect_down), cv2.UMat(left_frame_rect_down))

        left_disp = np.int16(cv2.UMat.get(left_disp))
        right_disp = np.int16(cv2.UMat.get(right_disp))

        filtered_disp = self.wls_filter.filter(left_disp, left_frame_rect, None, right_disp)

        # disparityMap = cv2.normalize(filtered_disp, filtered_disp, 0, 256,
        #                             cv2.NORM_MINMAX, cv2.CV_8UC3)
        # return disparityMap

        # minDisp = np.min(filtered_disp)
        # maxDisp = np.max(filtered_disp)

        # image3D = cv2.reprojectImageTo3D(filtered_disp,self.Q)

        if isActif:
            disparityMap = cv2.normalize(filtered_disp, filtered_disp, 0, 256,
                                         cv2.NORM_MINMAX, cv2.CV_8UC3)
            disparityMap = cv2.applyColorMap(disparityMap, cv2.COLORMAP_JET)
            return disparityMap

        # filtered_disp = filtered_disp.astype(np.float32) / 16.0

        minDisp = np.min(filtered_disp)
        maxDisp = np.max(filtered_disp)

        disparity_to_display = ((filtered_disp - minDisp) / (maxDisp - minDisp) * 255.).astype(np.uint8)

        return disparity_to_display, filtered_disp, left_disp

    def get3DPoint(self, disparityCursorPosition, finalPicture, filteredDisparity, left_disp):
        point3DList = []
        if self.Q is not None:
            x = disparityCursorPosition[0]
            y = disparityCursorPosition[1]
            d = left_disp[y][x]
            d2 = filteredDisparity[y][x]
            d3 = finalPicture[y][x]
            print(f'distance {d} == {d2} == {d3}')
            # TODO : Trouver comment calculer la bonne distance avec perspectiveTrans. Sinon passer sur reprojectImageTo3D
            pointToFind = np.array([[x, y, d2]], dtype="float32")
            point3DList = cv2.perspectiveTransform(np.array([pointToFind]), self.Q)
        return point3DList
        # if len(distancePixelList) > 0:
        #     self.getDisparityMaps()
        #
        #     if self.Q is not None:
        #
        #         distancePixelList = np.array(distancePixelList, dtype="float32")
        #         # a = np.array([[1, 2], [4, 5], [7, 8]], dtype='float32')
        #         # a = np.array([a])
        #
        #         distancePixelList = np.array([distancePixelList])
        #         # pts_src = np.float32([52, 376, 240, 528, 413, 291, 217, 266]).reshape(4, -1)
        #         # pts_dst = np.float32([56, 478, 387, 497, 376, 124, 148, 218]).reshape(4, -1)
        #         # h = cv2.findHomography(pts_src, pts_dst)
        #         # point3DList = cv2.perspectiveTransform(pts_src, h)
        #
        #         point3DList = cv2.perspectiveTransform(distancePixelList, self.Q)
        # return point3DList
