#// Open the camera

import pyzed.sl as sl
import cv2
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='projetdista')
    parser.add_argument('--resolution', type=str, default='VGA', help='camera resolution : VGA, HD, FHD, 2K')
    parser.add_argument('--port', type=int, default=30000, help='camera port number')
    parser.add_argument('--serial', type=int, default=27645295, help='camera serial number')
    parser.add_argument('--linux_id', type=int, default=2, help='camera linux_id')
    parser.add_argument('--bitrate', type=int, default=7000, help='camera bitrate')

    
    args = parser.parse_args()
    return args



def main():
    args = parse_args()
    resolution_str=args.resolution
    port=args.port
    serial=args.serial
    linux_id=args.linux_id
    bitrate=args.bitrate
    
    
    
    print(sl.Camera.get_device_list())
    zed = sl.Camera()

    init_params1 = sl.InitParameters()  
    init_params1.set_from_camera_id(linux_id)
#    init_params1.set_from_serial_number(serial)         
    
    if resolution_str== 'VGA' :
        init_params1.camera_resolution = sl.RESOLUTION.VGA 
    if resolution_str== 'HD' :
        init_params1.camera_resolution = sl.RESOLUTION.HD720         
    if resolution_str== 'FHD' :
        init_params1.camera_resolution = sl.RESOLUTION.HD1080
    if resolution_str== '2K' :
        init_params1.camera_resolution = sl.RESOLUTION.HD2K  

    err = zed.open(init_params1)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)
    
    
    # Set the streaming parameters
    stream = sl.StreamingParameters()
    stream.codec = sl.STREAMING_CODEC.H264 # Can be H264 or H265
    stream.bitrate = bitrate
    stream.port = port # Port used for sending the stream
    # Enable streaming with the streaming parameters
    err = zed.enable_streaming(stream)
    
    
    while True :
        zed.grab()
        
        k = cv2.waitKey(1)
        if k == 27:
            break
    
    
    # Disable streaming
    zed.disable_streaming()

if __name__ == "__main__":
    main()



