################################################################################
##          Classe RectifiedCamera
##      Fournit une abstration de camera pour donner une image corrigee
##  Author : J. Coupez
##  Date : 17/02/2021
##  Copyright Dista
##  Version : 1.0
################################################################################
import cv2



class RectifiedCamera:

    def __init__(self, cameraMatrix, distCoeffs, rectificationMatix, projectionMatrix, map_x, map_y, Q):
        self.K=cameraMatrix
        self.D=distCoeffs
        self.R=rectificationMatix
        self.P=projectionMatrix
        self.map_x=map_x
        self.map_y=map_y
        self.Q=Q

    def rectifyImage(self,image):
        return cv2.remap(image, self.map_x, self.map_y, interpolation=cv2.INTER_LINEAR)

