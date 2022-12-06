import os, sys
user = os.environ.get('HOME') or os.environ.get('HOMEPATH')
sys.path.append('efficientdetection')
os.chdir('efficientdetection')

########################################################################
import cv2
import numpy as np
import time
import traceback
import threading
import queue
from database_tools import *
from display_tools import *
from camera_tools import *
from detection_tools import *
from Camera import *
from config import *
import globalvar
import mmap
from scipy.spatial import distance_matrix


def main():

    #################################################################
    # GET DEFAULT PARAMETERS
    args = parse_args()
    if args.catego: #TODO Renommer en 'categories'
        args.catego = args.catego.split(',')
    if len(args.core) != 0:
        core = set(map(int, args.core.split(',')))
    # assign core to process
    #os.sched_setaffinity(os.getpid(), core)
    #################################################################
    # Connect (or create) database and load camera information
    database = connect_database(user, args)
    serial_numbers, ip_addresses, cam_ports = load_cameras(args, database)
    ##########################################################################

    ############################################################################################
    # INITIALIZE ALL CAMERAS
    cap = initalize_all_cameras(serial_numbers,ip_addresses,cam_ports)
#    print(cap[0].width)
    ##############################################################
    # LOAD EFFICIENTDET NETWORK
    neural_net=Neural_Net(args)
    ##########################################################################
    #   DEFINE WINDOWS SIZES DANS POSITIONS ON SCREEN
    # for i in range(len(serial_numbers)):
    #     set_windows(args,cap[i],i)
    set_windows(args)
    #################################################################################
#    # Initialize disparity trackbar
    if args.cloudtrackbar:
        for i in range(len(serial_numbers)):
            cap[i].initalize_stereo_trackbar()
    ############################################################################################
    # MAIN LOOP
    try :
        
        # VIDEO ONLY
        if args.displayloop:
            displayloop(args,cap)
       ####################################################################
       # DETECTION
        detectionloop(args,cap,neural_net,database)

    
    except KeyboardInterrupt as ex:
        if args.thread:
            globalvar.stopthread_images=True
            globalvar.stopthread_stereo=True
            globalvar.stopthread_net=True

        print("Received Ctrl-C")
    except Exception as ex:
        traceback.print_exc()
        
    finally :
        if args.thread:
            globalvar.stopthread_stereo=True
            globalvar.stopthread_images=True
            globalvar.stopthread_net=True

        # Close cameras
        for i in range(len(serial_numbers)):
            cap[i].release()
        cv2.destroyAllWindows()
        database.close()
        print("Exited cleanly")

if __name__ == "__main__":
    main()
    
