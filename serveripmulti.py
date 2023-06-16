import mmap
import time
import os
import cv2
import queue
from database_tools import *
from camera_tools import *
from detection_tools import *
from Camera import *
from config import *
import numpy as np
print("Opening camera...")





def main():

    #################################################################
    # GET DEFAULT PARAMETERS
#    args = parse_args()
#    if args.catego: #TODO Renommer en 'categories'
#        args.catego = args.catego.split(',')
#    #################################################################
#    # Connect (or create) database and load camera information
#    database = connect_database(user, args)
#    serial_numbers, ip_addresses, cam_ports = load_cameras(args, database)
#    ############################################################################################
#    # INITIALIZE ALL CAMERAS
#    cap = initalize_all_cameras(serial_numbers,ip_addresses,cam_ports)
    
    
    
#    h=int(480 * 512/800)
#    w=int(1600*512/800)
    h=int(1200*0.25)
    w=int(1800*0.25)
    shape = (h, w, 3)
#    n = (w*w*3*1)
    n = (h*w*3*1)

    fd=[]
    cap=[1]
    for i in range(len(cap)):
        fd.append(os.open('/tmp/mmaptest'+str(i), os.O_CREAT | os.O_TRUNC | os.O_RDWR))
        os.truncate(fd[i], n)  # resize file


    
    try:
        mean=np.array([0.406, 0.456, 0.485],dtype=np.float32)
        std=np.array([0.225, 0.224, 0.229],dtype=np.float32)
#        mean=(0.406, 0.456, 0.485)
#        std=(0.225, 0.224, 0.229)

        while True:
            
            for i in range(len(cap)):
            
                mm = mmap.mmap(fd[i], n, mmap.MAP_SHARED, mmap.PROT_WRITE)  # it has to be only for writing

                start = time.perf_counter()

#                img = cap[i].read()
#                img=cv2.resize(img, (w, h))
                img=np.ones((h,w,3)).astype(np.uint8)
#                img=img.astype(np.float32)
#                img = (img / 255 - mean) / std
#                img=img.astype(np.uint8)
                
#                canvas = np.zeros((w, w, 3), np.float32)
          
#                canvas[:h, :w,:] = img                
                
                
                
                
                
                
                
    
        
                # write image
#                start = time.perf_counter()
                buf = img.tobytes()
                mm.seek(0)
                mm.write(buf)
                mm.flush()
                
                stop = time.perf_counter()
        
                print("Writing Duration:", (stop - start) * 1000, "ms")
    
    
    
    except KeyboardInterrupt:
        pass
    
    print("Closing resources")
    cap.release()
    mm.close()



if __name__ == "__main__":
    main()

