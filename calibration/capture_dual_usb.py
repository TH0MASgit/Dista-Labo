##############################################################################################################
# Projet : Integration cours initiation                                                                      #
# Description Script : Effectuer une capture synchrone de deux camera                                        #
# Date : 29 aout 2020                                                                                        #
# Auteur : Carl Beaulieu                                                                                     #
##############################################################################################################
import sys
import os
import cv2

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from lib.NetCam import NetCam

text_title="Assistant de calibration"
text_progress=""

# Nombres de captures prises
capture_taken=0
# Nombres de captures à prendre
capture_qty=40

# Déclaration du périphérique de capture
cap_left = NetCam(source=0,capture='HD')
cap_left.invertVertical()
# cap_left = cv2.VideoCapture(4)
# cap_left.set(cv2.CAP_PROP_FPS, 30)
# cap_right = cv2.VideoCapture(2)
cap_right = NetCam(source=1,capture='HD')
cap_right.invertHorizontal()

# cap_right.set(cv2.CAP_PROP_FPS, 30)

# # #Paramètres d'image pour la lnetille gauche
# cap_left.set(cv2.CAP_PROP_BRIGHTNESS,0);
# cap_left.set(cv2.CAP_PROP_CONTRAST, 0);
# cap_left.set(cv2.CAP_PROP_SATURATION, 0);
# cap_left.set(cv2.CAP_PROP_GAIN, 0);

# # #Paramètres d'image pour la lnetille droite
# cap_right.set(cv2.CAP_PROP_BRIGHTNESS,0);
# cap_right.set(cv2.CAP_PROP_CONTRAST, 0);
# cap_right.set(cv2.CAP_PROP_SATURATION, 0);
# cap_right.set(cv2.CAP_PROP_GAIN, 0);

# Attribution de la resolution au frame
# cap_left.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap_left.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# cap_right.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap_right.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
while(True):
    
    if not cap_left.isRunning():
        continue
    if not cap_right.isRunning():
        continue
    
    if capture_taken==0:
        text_progress="Appuyez sur 'C' pour capturer les images"
    elif capture_taken==capture_qty:
        text_progress="Termine, maintenir 'Esc' pour quitter."
    else: 
        text_progress="Il reste " + str(capture_qty-capture_taken)+ " image(s) a prendre."
        
    # Acquisition du flux video
    frame_color_left = cap_left.read()
    # if not ret:
    #     continue
    
    frame_color_right = cap_right.read()
    # if not ret:
    #     continue
    
    # frame_color_left=cv2.flip(frame_color_left, 1)
    # frame_color_left=cv2.flip(frame_color_left, 0)


#    frame_color_left=cv2.rotate(frame_color_left, cv2.ROTATE_90_COUNTERCLOCKWISE)
#    frame_color_right=cv2.rotate(frame_color_right, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    #Transformation de l'image en nuances de gris
    frame_left = cv2.cvtColor(frame_color_left, cv2.COLOR_BGR2GRAY)
    frame_right = cv2.cvtColor(frame_color_right, cv2.COLOR_BGR2GRAY)



    
    # Enregistrement des deux fcd cdrames sans écritures
    if cv2.waitKey(1) == ord('c'):
        if capture_taken<capture_qty:
            capture_taken = capture_taken + 1
            if capture_taken < 10:
                zf = "00"
            if capture_taken > 9:
                zf = "0"
            if capture_taken >99:
                zf= ""

            text_progress=""
            filename_l="left" + str(zf) + str(capture_taken) + ".jpg"
            filename_r="right" + str(zf) + str(capture_taken) + ".jpg"
            cv2.imwrite(filename_l, frame_left)
            cv2.imwrite(filename_r, frame_right)

    # Flip images
#    frame_color_left_flip=cv2.flip(frame_color_left, 0)
#    frame_color_right_flip=cv2.flip(frame_color_right, 0)
    
    frame_color_left_flip=frame_color_left
    frame_color_right_flip=frame_color_right    
            
    # Affichage du contenu
    k=0.75
    left_view = cv2.resize(frame_color_left_flip,(int(1280*k),int(720*k)))
    right_view = cv2.resize(frame_color_right_flip,(int(1280*k),int(720*k)))
    
    
    cv2.putText(left_view, text_progress, (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(right_view, text_progress, (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.imshow(text_title + ' Camera Gauche',left_view)
    cv2.imshow(text_title + ' Camera Droite',right_view)
        
    if cv2.waitKey(1) == 27:
        break
    
# On ferme les fenêtres
cv2.destroyAllWindows()