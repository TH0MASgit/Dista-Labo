import os
import subprocess
from subprocess import PIPE
import cv2

#current_value=subprocess.run(["v4l2-ctl", "--get-ctrl=contrast"] , stdout=PIPE, stderr=PIPE)          
#current_value=str(current_value.stdout)
#current_value=fl(current_value.split(": ")[1].split("\\n'")[0])
   
setting = "brightness"
step_camera_settings = 1



dictionary =	{
  'brightness': cv2.CAP_PROP_BRIGHTNESS,
  'contrast': cv2.CAP_PROP_CONTRAST,
  'hue':cv2.CAP_PROP_HUE,
  'saturation': cv2.CAP_PROP_SATURATION,
  'sharpness': cv2.CAP_PROP_SHARPNESS,
  'gain': cv2.CAP_PROP_GAIN ,
  'whitebalance':cv2.CAP_PROP_WB_TEMPERATURE,
  'exposure' : cv2.CAP_PROP_EXPOSURE}







################################################################################
def camera_settings(key, cap):
    step_camera_settings = 1


    if key == 115:  # for 's' key
        switch_camera_settings()
    elif key == 43:  # for '+' key
#        current_value=subprocess.run(["v4l2-ctl","--get-ctrl="+setting] , stdout=PIPE, stderr=PIPE)     
#        current_value=str(current_value.stdout)
#        current_value=float(current_value.split(": ")[1].split("\\n'")[0])
#        os.system("v4l2-ctl --set-ctrl="+setting +"=" + str(current_value + step_camera_settings))
        current_value = cap.get(dictionary[setting])
        cap.set(dictionary[setting], current_value + step_camera_settings)
        print(setting + ": " + str(current_value + step_camera_settings))
  
    elif key == 45:  # for '-' key
#        current_value=subprocess.run(["v4l2-ctl", "--get-ctrl="+setting] , stdout=PIPE, stderr=PIPE)          
#        current_value=str(current_value.stdout)
#        current_value=float(current_value.split(": ")[1].split("\\n'")[0])
        current_value = cap.get(dictionary[setting])
        if current_value >= 1:
#            os.system("v4l2-ctl --set-ctrl="+setting +"=" + str(current_value - step_camera_settings))   
            cap.set(dictionary[setting], current_value - step_camera_settings)
            print(setting + ": " + str(current_value - step_camera_settings))
   
    elif key == 114:  # for 'r' key

        cap.set(dictionary['brightness'], -1)
        cap.set(dictionary['contrast'], -1)
        cap.set(dictionary['hue'], -1)
        cap.set(dictionary['saturation'], -1)
        cap.set(dictionary['gain'], -1)
        cap.set(dictionary['whitebalance'], -1)
        cap.set(dictionary['exposure'], -1)
        
#        os.system("v4l2-ctl --set-ctrl=brightness=5")
#        os.system("v4l2-ctl --set-ctrl=contrast=5")     
#        os.system("v4l2-ctl --set-ctrl=hue=0")        
#        os.system("v4l2-ctl --set-ctrl=saturation=5")        
#        os.system("v4l2-ctl --set-ctrl=gain=5")        
#        os.system("v4l2-ctl --set-ctrl=exposure=101")        
#        os.system("v4l2-ctl --set-ctrl=whitebalanc=e=4000")        
        
        
        print("Camera settings: reset")
################################################################################


    
################################################################################
def switch_camera_settings():
    global cam_settings
    global str_camera_settings
    if cam_settings == 'brightness':
        cam_settings = 'contrast'
        str_camera_settings = "contrast"
        print("Camera settings: CONTRAST")
    elif cam_settings == "contrast":
        cam_settings = "Hue"
        str_camera_settings = "Hue"
        print("Camera settings: HUE")
    elif cam_settings == "Hue":
        cam_settings = 'saturation'
        str_camera_settings = 'saturation'
        print("Camera settings: SATURATION")
    elif cam_settings == 'saturation':
        cam_settings = 'sharpness'
        str_camera_settings = "sharpness"
        print("Camera settings: Sharpness")
    elif cam_settings =='sharpness':
        cam_settings = 'gain'
        str_camera_settings = "gain"
        print("Camera settings: GAIN")
    elif cam_settings == 'gain':
        cam_settings = 'exposure'
        str_camera_settings = "exposure"
        print("Camera settings: EXPOSURE")
    elif cam_settings == 'exposure':
        cam_settings = 'whitebalance'
        str_camera_settings = "whitebalance"
        print("Camera settings: WHITEBALANCE")
    elif cam_settings == 'whitebalance':
        cam_settings = 'brightness'
        str_camera_settings = "brightness"
        print("Camera settings: BRIGHTNESS")
################################################################################
