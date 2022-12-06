##############################################################################################################
# Projet : Integration cours initiation                                                                      #
# Description Script : Effectuer la calibration d'une camera stereo                                          #
# Date : 23 septembre 2020                                                                                   #
# Auteur : Carl Beaulieu                                                                                     #
##############################################################################################################
import numpy as np
import cv2
import glob
import time

# Classe contenant les fonctions de calibration
class StereoCalibration(object):
    # Paramaètres D'initialisation
    def __init__(self):
        # Critères de terminaison
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.criteria_cal = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)

        # Déclaration des points 3D et taille du damier 7x7
        self.objp = np.zeros((9*6, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

        # Déclaration des tableau contenant les points de tout les images
        self.objpoints = []  # Points 3D dans l'espace réel
        self.imgpoints_l = []  # Points 2D dans l'image
        self.imgpoints_r = []  # Points 2D dans l'image
        
        # Paramètre du dossier contenant les images à analyser
#        filepath = "./"
#        self.cal_path = filepath
        self.read_images()

    # Fonction de lectures des images
    def read_images(self):
        images_right = glob.glob('right*.jpg')
        images_left = glob.glob('left*.jpg')
        images_left.sort()
        images_right.sort()

        # Parcours le dossier pour trouver le damier sur les images
        for i, fname in enumerate(images_right):
            img_l = cv2.imread(images_left[i])
            img_r = cv2.imread(images_right[i])

            # Transformation de l'image en nuance de gris pour analyse
            gray_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)
            gray_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)

            # On cherche les coins sur le damier
            ret_l, corners_l = cv2.findChessboardCorners(gray_l, (9, 6), None)
            ret_r, corners_r = cv2.findChessboardCorners(gray_r, (9, 6), None)

            # Si le damier dans les images gauche et droite correspondante est détecté
            if ret_l is True and ret_r is True:
                # Quand les coins sont trouver et rafiné on les ajoutes au tableau de point 3D
                self.objpoints.append(self.objp)
                
                # On ajoute les points dans le tableau 2D
                rt = cv2.cornerSubPix(gray_l, corners_l, (11, 11),(-1, -1), self.criteria)    
                self.imgpoints_l.append(corners_l)

                # On dessine et affiche les coins sur l'image
                ret_l = cv2.drawChessboardCorners(img_l, (9, 6),corners_l, ret_l)           
                cv2.imshow(images_left[i], img_l)
                cv2.imwrite("detected/" + str(images_left[i]), img_l)
                cv2.waitKey(100)
                
                # On ajoute les points dans le tableau 2D
                rt = cv2.cornerSubPix(gray_r, corners_r, (11, 11),(-1, -1), self.criteria)  
                self.imgpoints_r.append(corners_r)

                # On dessine et affiche les coins sur l'image
                ret_r = cv2.drawChessboardCorners(img_r, (9, 6),corners_r, ret_r)                
                cv2.imshow(images_right[i], img_r)
                cv2.imwrite("detected/" + str(images_right[i]), img_r)
                cv2.waitKey(100)
                
            # On récupaire la taille de l'image
            img_shape = gray_l.shape[::-1]
            
        # # Délais pour analyse d'image
        #cv2.waitKey(50000)
        
        # On calibre les lentilles indépendament et retourne les valeurs de calibration
        rt, self.M1, self.d1, self.r1, self.t1 = cv2.calibrateCamera(self.objpoints, self.imgpoints_l, img_shape, None, None)
        rt, self.M2, self.d2, self.r2, self.t2 = cv2.calibrateCamera(self.objpoints, self.imgpoints_r, img_shape, None, None)

        print("Debut du calcul de calibration...")
        cv2.waitKey(100)
        start = time.time()
        
        # On appel la fonction de calibration STEREO [ligne 98]
        self.camera_model = self.stereo_calibrate(img_shape)
        
        # Après l'execution de la fonction on affiche le temps de calcul
        print("Calcul termine!")
        end = time.time()
        print('Temps de calcul:', int(end - start))

    # Fonction de calibration STEREO
    def stereo_calibrate(self, dims):
        # Taille des carreaux sur le damier en cm
        squaresize = 3.6412
        
        # Flag pour la calibration STEREO
        flags = 0
        flags |= cv2.CALIB_FIX_INTRINSIC
        # flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
        flags |= cv2.CALIB_USE_INTRINSIC_GUESS
        flags |= cv2.CALIB_FIX_FOCAL_LENGTH
        # flags |= cv2.CALIB_FIX_ASPECT_RATIO
        flags |= cv2.CALIB_ZERO_TANGENT_DIST
        # flags |= cv2.CALIB_RATIONAL_MODEL
        # flags |= cv2.CALIB_SAME_FOCAL_LENGTH
        # flags |= cv2.CALIB_FIX_K3
        # flags |= cv2.CALIB_FIX_K4
        # flags |= cv2.CALIB_FIX_K5
        
        # Critaires de terminaison et lancement de la calibration STEREO
        stereocalib_criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
        ret, M1, d1, M2, d2, R, T, E, F = cv2.stereoCalibrate(self.objpoints, self.imgpoints_l,self.imgpoints_r, self.M1, self.d1, self.M2,self.d2, dims,criteria=stereocalib_criteria, flags=flags)

        # On extrait les valeurs qui nous intéresse dans la matrice gauche
        fx_l = M1[0][0]
        cx_l = M1[0][2]
        fy_l = M1[1][1]
        cy_l = M1[1][2]
        k1_l = d1[0][0]
        k2_l = d1[0][1]
        k3_l = d1[0][4]
        p1_l = d1[0][2]
        p2_l = d1[0][3]
        
        # On extrait les valeurs qui nous intéresse dans la matrice droite
        fx_r = M2[0][0]
        cx_r = M2[0][2]
        fy_r = M2[1][1]
        cy_r = M2[1][2]
        k1_r = d2[0][0]
        k2_r = d2[0][1]
        k3_r = d2[0][4]
        p1_r = d2[0][2]
        p2_r = d2[0][3]

        # On extrait la distance entre les deux lentilles
        baseline = T[0][0]
        baseline = baseline * squaresize * 10

        # Sauvegarde des données dans un fichier
        f = open("config.conf", "a")
        f.write("[LEFT_CAM_VGA] \n")
        f.write("fx=" + str(fx_l) + "\n")
        f.write("fy=" + str(fy_l) + "\n")
        f.write("cx=" + str(cx_l) + "\n")
        f.write("cy=" + str(cy_l) + "\n")
        f.write("k1=" + str(k1_l) + "\n")
        f.write("k2=" + str(k2_l) + "\n")
        f.write("k3=" + str(k3_l) + "\n")
        f.write("p1=" + str(p1_l) + "\n")
        f.write("p2=" + str(p2_l) + "\n")
        f.write("\n")
        f.write("[RIGHT_CAM_VGA] \n")
        f.write("fx=" + str(fx_r) + "\n")
        f.write("fy=" + str(fy_r) + "\n")
        f.write("cx=" + str(cx_r) + "\n")
        f.write("cy=" + str(cy_r) + "\n")
        f.write("k1=" + str(k1_r) + "\n")
        f.write("k2=" + str(k2_r) + "\n")
        f.write("k3=" + str(k3_r) + "\n")
        f.write("p1=" + str(p1_r) + "\n")
        f.write("p2=" + str(p2_r) + "\n")
        f.write("\n")
        f.write("[STEREO] \n")
        f.write("Baseline=" + str(baseline) + "\n")
        f.write("\n")
        f.close()
        
        # Affichage des paramètres de calibration dans le Terminal
        print('Intrinsic_mtx_1', M1)
        print('dist_1', d1)
        print('Intrinsic_mtx_2', M2)
        print('dist_2', d2)
        print('R', R)
        print('T', T)
        print('E', E)
        print('F', F)

        # #Application des paramètres à une image test
        # img = cv2.imread('distorted.jpg')
        # h,  w = img.shape[:2]
        # newcameramtx, roi=cv2.getOptimalNewCameraMatrix(M1,d1,(w,h),1,(w,h))
        
        # #Transformation de l'image
        # mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
        # dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)
        
        # # Rognage de l'image
        # x,y,w,h = roi
        # dst = dst[y:y+h, x:x+w]
        
        # # Enregistrement de l'image
        # cv2.imwrite('undistorted.png',dst)
        
        

        # for i in range(len(self.r1)):
        #     print("--- pose[", i+1, "] ---")
        #     self.ext1, _ = cv2.Rodrigues(self.r1[i])
        #     self.ext2, _ = cv2.Rodrigues(self.r2[i])
        #     print('Ext1', self.ext1)
        #     print('Ext2', self.ext2)

        print('')

        camera_model = dict([('M1', M1), ('M2', M2), ('dist1', d1),('dist2', d2), ('rvecs1', self.r1),('rvecs2', self.r2), ('R', R), ('T', T),('E', E), ('F', F)])

        # On ferme les fenêtres d'images
        cv2.destroyAllWindows()
        
        # On retourne les valeurs des paramètres de calibration
        return camera_model

if __name__ == '__main__':
    # Lancement de la procédure de calibration
    cal_data = StereoCalibration()
