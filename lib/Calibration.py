################################################################################
##          Classe Calibration
##      Stock les coefficient d'une camera (stereo ou non)
##  Author : J. Coupez
##  Date : 10/10/2020
##  Copyright Dista
##  Version : 1.0
################################################################################


class Calibration():

    def __init__(self, settings={}):

        self.imageSize = settings.get('imageSize') or None
        self.cameraMatrixLeft = settings.get('cameraMatrixLeft') or None
        self.cameraMatrixRight = settings.get('cameraMatrixRight') or None
        self.distCoefLeft = settings.get('distCoefLeft') or None
        self.distCoefRight = settings.get('distCoefRight') or None
        self.T = settings.get('T') or None
        self.R = settings.get('R') or None

    def getRms(self):
        return self.rms

    def setRms(self, rms):
        self.rms = rms

    def setImageSize(self, imageSize):
        self.imageSize = imageSize

    def getImageSize(self):
        return self.imageSize

    def setCameraMatrixLeft(self, cameraMatrixLeft):
        self.cameraMatrixLeft = cameraMatrixLeft

    def getCameraMatrixLeft(self, ):
        return self.cameraMatrixLeft

    def setCameraMatrixRight(self, cameraMatrixRight):
        self.cameraMatrixRight = cameraMatrixRight

    def getCameraMatrixRight(self):
        return self.cameraMatrixRight

    def setDistCoefLeft(self, distCoeffsLeft):
        self.distCoefLeft = distCoeffsLeft

    def getDistCoefLeft(self):
        return self.distCoefLeft

    def setDistCoefRight(self, distCoefsRight):
        self.distCoefRight = distCoefsRight

    def getDistCoefRight(self):
        return self.distCoefRight

    def setT(self, T):
        self.T = T

    def getT(self):
        return self.T

    def setR(self, R):
        self.R = R

    def getR(self):
        return self.R

    def getPerViewErrors(self):
        return self.perViewErrors

    def setPerViewErrors(self, perViewErrors):
        self.perViewErrors = perViewErrors

    def setBaseline(self, baseline):
        self.baseline = baseline

    def getBaseline(self):
        return self.baseline

    def setResolution(self, resolution):
        self.resolution = resolution

    def getResolution(self):
        return self.resolution

    def toJSON(self):
        result = {
            "rms": self.rms,
            "resolution": self.resolution,
            "imageSize": self.imageSize,
            "baseline": self.baseline,
        }
        if self.cameraMatrixLeft is not None:
            result["cameraMatrixLeft"] = self.cameraMatrixLeft.tolist()
        if self.cameraMatrixRight is not None:
            result["cameraMatrixRight"] = self.cameraMatrixRight.tolist()
        if self.distCoefLeft is not None:
            result["distCoefLeft"] = self.distCoefLeft.tolist()
        if self.distCoefRight is not None:
            result["distCoefRight"] = self.distCoefRight.tolist()
        if self.R is not None:
            result["R"] = self.R.tolist()
        if self.T is not None:
            result["T"] = self.T.tolist()
        # if self.E is not None:
        #     result["E"] = self.E.tolist()
        # if self.F is not None:
        #     result["F"] = self.F.tolist()
        return result

    def toTxt(self):
        result = f"""
{self.generateCoefficientString("LEFT_CAM", self.resolution, self.getCameraMatrixLeft(), self.getDistCoefLeft())}
{self.generateCoefficientString("RIGHT_CAM", self.resolution, self.getCameraMatrixRight(), self.getDistCoefRight())}
[STEREO]
Baseline={self.baseline}
TY={self.T[1][0]}
TZ={self.T[2][0]}
RY={self.R[0][1]}
RX={self.R[2][1]}
RZ={self.R[1][0]}
"""
        return result

    def generateCoefficientString(self, configName, resolution, M, d):
        fx = M[0][0]
        fy = M[1][1]
        cx = M[0][2]
        cy = M[1][2]
        k1 = d[0][0]
        k2 = d[0][1]
        k3 = d[0][4]
        p1 = d[0][2]
        p2 = d[0][3]

        return f"""[{configName}_{resolution}]
 fx={fx}
 fy={fy}
 cx={cx}
 cy={cy}
 k1={k1}
 k2={k2}
 k3={k3}
 p1={p1}
 p2={p2}\n\n"""
