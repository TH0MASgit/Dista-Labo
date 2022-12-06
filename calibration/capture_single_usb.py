##############################################################################################################
# Projet : Integration cours initiation                                                                      #
# Description Script : Effectuer une capture synchrone de deux camera                                        #
# Date : 29 aout 2020                                                                                        #
# Auteur : Carl Beaulieu                                                                                     #
##############################################################################################################
import numpy as np
import cv2
import sys
import os
import glob

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from lib.NetCam import NetCam

# Variables textuel
text_title="Assistant de calibration"
text_progress=""

# Nombres de captures prises
capture_taken=0
# Nombres de captures à prendre
capture_qty=20

# Déclaration du périphérique de capture

cap = NetCam(source=0,capture='VGA',isStereoCam=True)
# cap_left.invertVertical()

# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FPS, 30)

#cap.set(cv2.CAP_PROP_BRIGHTNESS,Brightness);
#cap.set(cv2.CAP_PROP_CONTRAST, Contrast);
#cap.set(cv2.CAP_PROP_SATURATION, Saturation);
#cap.set(cv2.CAP_PROP_GAIN, Gain);

# Attribution de la resolution au frame
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# Old picture cleanup
if not os.path.exists('capture'):
    os.makedirs('capture')
else:
    # Flush the content of the directory
    files = glob.glob('capture/*.jpg')
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))


while(True):
    if capture_taken==0:
        text_progress="Appuyez sur 'C' pour capturer les images"
    elif capture_taken==capture_qty:
        text_progress="Termine, maintenir 'Esc' pour quitter."
    else: 
        text_progress="Il reste " + str(capture_qty-capture_taken)+ " image(s) a prendre."
    
    # Acquisition du flux video
    frame = cap.read()

    # Split images
    frames = np.split(frame, 2, axis=1)
    left_frame_color=frames[0]
    right_frame_color=frames[1]
    
    # Flip images
    left_frame_color=cv2.flip(left_frame_color, 0)
    right_frame_color=cv2.flip(right_frame_color, 0)

    #Transformation de l'image en nuances de gris
    left_frame = cv2.cvtColor(left_frame_color, cv2.COLOR_BGR2GRAY)
    right_frame = cv2.cvtColor(right_frame_color, cv2.COLOR_BGR2GRAY)
    
    # Enregistrement des deux frames sans écritures
    keypressed = cv2.waitKey(1)
    if keypressed == ord('c'):
        if capture_taken<capture_qty:
            capture_taken = capture_taken + 1
            if capture_taken < 10:
                zf = "00"
            if capture_taken > 9:
                zf = "0"
            if capture_taken >99:
                zf= ""
            
            text_progress=""
            filename_l=f'capture/{zf}{capture_taken}_left.jpg'
            filename_r=f'capture/{zf}{capture_taken}_right.jpg'
            cv2.imwrite(filename_l, left_frame)
            cv2.imwrite(filename_r, right_frame)
    elif keypressed == 27:
        # Exit capture
        break

    # Affichage du contenu
    # left_view = left_frame_color #cv2.resize(left_frame_color,(640,480))
    left_view = cv2.resize(left_frame_color,(640,480))
    # right_view = right_frame_color #cv2.resize(right_frame_color,(640,480))
    right_view = cv2.resize(right_frame_color,(640,480))
    height, width, _ = left_view.shape

    cv2.putText(left_view, "Gauche", (int(width/2) - 50, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 1)

    cv2.putText(right_view, "Droite", (int(width/2) - 40, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 1)

    finalPicture = np.concatenate((left_view, right_view), axis=1)
    cv2.putText(finalPicture, text_progress, (int(width) - 250, int(height) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    cv2.imshow(text_title ,finalPicture)

# On ferme les fenêtres
cap.release()