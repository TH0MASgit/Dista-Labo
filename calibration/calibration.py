##############################################################################################################
# Projet : Integration cours initiation                                                                      #
# Description Script : Effectuer la calibration de deux lentilles                                            #
# Date : 29 aout 2020                                                                                        #
# Auteur : Carl Beaulieu                                                                                     #
##############################################################################################################

import numpy as np
import cv2
import glob

# Critères de terminaison
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Préparation des object points, comme (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

objp = objp

# Tableau pour storer les object points et les image points de tout les images.
objpoints = [] # Points 3d dans l'espace réel
imgpoints = [] # Points 2d dans le plan de l'image

# Tout les images terminant gauche et droite dans le dossier du script
images_left = glob.glob('left*.jpg')
images_right = glob.glob('right*.jpg')

##############################################################################################################
#                                          Calibration lentille gauche                                       #
##############################################################################################################
print("Image(s) retenue(s) pour la calibration de la lentille gauche:")

for fname in images_left:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # On trouve les coins sur le damier
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)

    # Si trouvé, on ajoute les object points et les image points après les avoir affinés
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # On dessine et affiche les coins
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)
        cv2.imshow(fname,img)
        
        # Afficher le nom des images retenu pour la calibration dans la console
        print(fname)
        cv2.waitKey(500)

cv2.destroyAllWindows()

#Acquisition des résultats de calibration
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Transformation de la matrice et des coefficients de distortion en nombres
camera_mtx = np.array(mtx)
dist_coeff = np.asarray(dist)
print(tvecs)
fx = camera_mtx[0][0]
cx = camera_mtx[0][2]
fy = camera_mtx[1][1]
cy = camera_mtx[1][2]
k1 = dist_coeff[0][0]
k2 = dist_coeff[0][1]
k3 = dist_coeff[0][4]
p1 = dist_coeff[0][2]
p2 = dist_coeff[0][3]

# Sauvegarde des données dans un fichier
f = open("config.conf", "a")
f.write("[LEFT_CAM_HD] \n")
f.write("fx=" + str(fx) + "\n")
f.write("fy=" + str(fy) + "\n")
f.write("cx=" + str(cx) + "\n")
f.write("cy=" + str(cy) + "\n")
f.write("k1=" + str(k1) + "\n")
f.write("k2=" + str(k2) + "\n")
f.write("k3=" + str(k3) + "\n")
f.write("p1=" + str(p1) + "\n")
f.write("p2=" + str(p2) + "\n")
f.write("\n")
f.close()

##############################################################################################################
#                           Affichage d'une image test de la lentille gauche                                 #
##############################################################################################################
#Application des paramètres à une image test
img = cv2.imread('left001.jpg')
h,  w = img.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

#Transformation de l'image
mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)

# Rognage de l'image
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]

# Enregistrement de l'image
cv2.imwrite('calibresult_left1.png',dst)

##############################################################################################################
#                                          Calibration lentille droite                                       #
##############################################################################################################
print("Image(s) retenue(s) pour la calibration de la lentille droite:")
objpoints = []
imgpoints = []
for fname in images_right:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # On trouve les coins sur le damier
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)

    # Si trouvé, on ajoute les object points et les image points après les avoir affinés
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # On dessine et affiche les coins
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)
        cv2.imshow(fname,img)
        
        # Afficher le nom des images retenu pour la calibration dans la console
        print(fname)
        cv2.waitKey(500)

cv2.destroyAllWindows()

#Acquisition des résultats de calibration
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Transformation de la matrice et des coefficients de distortion en nombres
camera_mtx = np.array(mtx)
dist_coeff = np.asarray(dist)
print(tvecs)
fx = camera_mtx[0][0]
cx = camera_mtx[0][2]
fy = camera_mtx[1][1]
cy = camera_mtx[1][2]
k1 = dist_coeff[0][0]
k2 = dist_coeff[0][1]
k3 = dist_coeff[0][4]
p1 = dist_coeff[0][2]
p2 = dist_coeff[0][3]

# Sauvegarde des données dans un fichier
f = open("config.conf", "a")
f.write("[RIGHT_CAM_HD] \n")
f.write("fx=" + str(fx) + "\n")
f.write("fy=" + str(fy) + "\n")
f.write("cx=" + str(cx) + "\n")
f.write("cy=" + str(cy) + "\n")
f.write("k1=" + str(k1) + "\n")
f.write("k2=" + str(k2) + "\n")
f.write("k3=" + str(k3) + "\n")
f.write("p1=" + str(p1) + "\n")
f.write("p2=" + str(p2) + "\n")
f.write("\n")
f.close()

##############################################################################################################
#                           Affichage d'une image test de la lentille droite                                 #
##############################################################################################################
# Application des paramètres à une image test
img = cv2.imread('right001.jpg')
h,  w = img.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

# Transformation de l'image
mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)

# Rognage de l'image
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]

# Enregistrement de l'image
cv2.imwrite('calibresult_right1.png',dst)

#Calibration Terminé
print("Calibration terminé!")