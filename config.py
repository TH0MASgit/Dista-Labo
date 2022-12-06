from datetime import datetime
import pytz

import argparse

# Function to define and load all default parameters
def parse_args():    
        
    now = datetime.now(pytz.timezone('America/Montreal')).strftime('YYYY-MM-DDTHH_MM_SS')
    
    # LOAD DEFAULT PARAMETERS
    usb=False
    opencv=False
    fullscreen=False
    display_title=False
    lineupmode=False
    hflip=[]
    record=False
    wait=1
    vidid=now
    side_panel=False
    lineupdepth=2
    nb_neighbors=2
    maxdist=3.5
    max_number_objects=100
    minheight=0.0
    minwidth=0.0
    mindepth=0.0
    resolution='VGA'
    depth_mode='ULTRA'
    hold_for=2
    detection_threshold=0.4
    nonmax_threshold=0.2
    min_z=0.2
    max_z=40
    window_width=672
    window_height=376
    window_hori_position=50
    window_verti_position=20
    view_3dbox=False
    view_2dbox=False
    displaydistance=False
    red_box_arrow_yellow_box=False
    nbframes_per_cam=2
    linuxid=[]
    arrows=False
    adjust=False
    showcloud=False
    cloudtrackbar=False
    threadframes=False
    nanocam=False
    zed=False
    opencv_cloud=False
    displayloop=False    
    ports_in='5555'
    ports_out='5556'
    vflip=[]
    catego='person'
    displim=None
    sidebyside=False
    justcloud=False
    nodetec =False
    justdetec =False
    nocuda=False
    thread=False
    mirror=False
    csi=False
    nerian=False
    netsize=0
    mmcam=False
    socketcam = False
    ipcam = False
    tracking=False    
    display=None
    show=False
    camPerLine = 1
    threadnet=False
    threadstereo = False
    stereo = False
    netsizes= [512, 640, 768, 896, 1024, 1280, 1280, 1536]
    camid=[]
    vidin=[]
    vidout=[]
    angleports = []
    camposi = [0,0,0]
    core = []
    serverip = '192.168.1.22'
    pid = 0
    cloudstep=4
    rectifydown = 1
    cloudports = []
    netimgports = []
    sn='12345678'
    udp=False
    recv=False
    compression=80
    pwd='m0P04b*PYMG'

    parser = argparse.ArgumentParser(description='Projet Dista')
    
    # Selecting database
    # If this is omitted, an in-memory database will be used
    parser.add_argument('--db', '--database', help="Database connection string")
    #TODO Support a real db connection string:
    # https://docs.sqlalchemy.org/en/13/core/engines.html
    
    # Selecting cameras and machines
    # If these are omitted, they will be loaded from the database
    parser.add_argument('-c', '--camera', dest='cameras', action='append', default=[],
                        help="Camera url(s)")
    #TODO Replace these with zed|opencv://username:password@host:port/serial
    # See https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse
    
    # Deprecated (this is the same as a --camera without an ip address)
    #parser.add_argument('--sn', '--serial', dest='cameras', action='append',
    #                    help="[Deprecated: use -c instead] Camera serial number(s)")

    parser.add_argument('--sn', type=str, default=sn,help='serial number')


    parser.add_argument('--ip', '--ip_address', action='append', default=[], help="Streamer ip address(es)")

    # Other parameters
    parser.add_argument('--usb', action='store_true', default=usb,help='connection type')    
    parser.add_argument('--opencv', action='store_true', default=opencv,help='Library type')
    parser.add_argument('--fullscreen', action='store_true', default=fullscreen,help='Full screen display') 
    parser.add_argument('--display_title', action='store_true', default=display_title,help='Display title ')    
    parser.add_argument('--resolution', type=str, default=resolution,help='Resolution : VGA, HD, FHD ,2K')
    parser.add_argument('--display', type=str, default=display,help='Display Resolution : VGA, HD, FHD ,2K')
    parser.add_argument('--hold_for', type=int, default=hold_for,help='Number of frames held with same distance')
    parser.add_argument('--view_3dbox', action='store_true', default=view_3dbox,help='Display 3D box : NOT FOR PUBLIC USE')
    parser.add_argument('--view_2dbox', action='store_true', default=view_2dbox,help='Display 2D box : NOT FOR PUBLIC USE')
    parser.add_argument('--displaydistance', action='store_true', default=displaydistance,help='Display distance on objects')
    parser.add_argument('--red_box_arrow_yellow_box', action='store_true', default=red_box_arrow_yellow_box,help='Display distances with boxes instead of arrows')
    parser.add_argument('--lineupmode', action='store_true', default=lineupmode,help='For lineups')
    parser.add_argument('--record', action='store_true', default=record,help='Record video : CAREFUL DO NOT RECORD TOO LONG IN FHD')
    parser.add_argument('--wait', type=int, default=wait,help='Frame step for recording: ONE or more')    
    parser.add_argument('--vidid', type=str, default=vidid,help='Time of recording')      
    parser.add_argument('--side_panel', action='store_true', default=side_panel,help='Display side panel : NOT FOR PUBLIC USE')
    parser.add_argument('--lineupdepth', type=float, default=lineupdepth,help='Maximum depth of lineup')
    parser.add_argument('--nb_neighbors', type=int, default=nb_neighbors,help='Maximum number of arrows coming out of one person : OVERRIDEN BY LINEUP MODE')
    parser.add_argument('--maxdist', type=float, default=maxdist,help='Maximum distance between persons')   
    parser.add_argument('--max_number_objects', type=int, default=max_number_objects,help='Maximum number of persons detected')
    parser.add_argument('--minheight', type=float, default=minheight,help='Minimum height of objects')
    parser.add_argument('--minwidth', type=float, default=minwidth,help='Minimum width of objects')
    parser.add_argument('--mindepth', type=float, default=mindepth,help='Minimum depth of objects')
    parser.add_argument('--depth_mode', type=str, default=depth_mode,help='Resolution : ULTRA, QUALITY, MEDIUM, PERFORMANCE')
    parser.add_argument('--detection_threshold', type=float, default=detection_threshold,help='Detection confidence, Max = 100') 
    parser.add_argument('--nonmax_threshold', type=float, default=nonmax_threshold,help='Non max supression') 
    parser.add_argument('--min_z', type=float, default=min_z,help='Minimum depth : KEEP at 1')
    parser.add_argument('--max_z', type=float, default=max_z,help='Maximum depth: Keep at 40')
    parser.add_argument('--window_width', type=int, default=window_width,help='Truck display width')
    parser.add_argument('--window_height', type=int, default=window_height,help='truck display height')
    parser.add_argument('--window_hori_position', type=int, default=window_hori_position,help='Truck side window horizontal position')    
    parser.add_argument('--window_verti_position', type=int, default=window_verti_position,help='Truck side window vertical position')    
    parser.add_argument('--nbframes_per_cam', type=int, default=nbframes_per_cam,help='nbframes_per_cam')    
    parser.add_argument('--linuxid', type=str, default=linuxid,help='List of camera USB port id : 0,1,2,3,4...')
    parser.add_argument('--arrows', action='store_true', default=arrows,help='display arrows between persons')    
    parser.add_argument('--adjust', action='store_true', default=adjust,help='Adjust image quality')    
    parser.add_argument('--showcloud', action='store_true', default=showcloud,help='Show disparity/cloud')    
    parser.add_argument('--cloudtrackbar', action='store_true', default=cloudtrackbar,help='Show trackbar for disparity')    
    parser.add_argument('--threadframes', action='store_true', default=threadframes,help='thread frames')    
    parser.add_argument('--nanocam', action='store_true', default=nanocam,help='camera open with nanocamera library')    
    parser.add_argument('--zed', action='store_true', default=zed,help='zed open with zed library')    
    parser.add_argument('--opencv_cloud', action='store_true', default=opencv_cloud,help='compute cloud with opencv')    
    parser.add_argument('--displayloop', action='store_true', default=displayloop,help='activate display loop option : no detection')    
    parser.add_argument('--ports_in', type=str, default=ports_in,help='List of camera USB streaming port : 5555,5556 etc...')
    parser.add_argument('--ports_out', type=str, default=ports_out,help='List of camera USB streaming port : 5555,5556 etc...')
    parser.add_argument('--vflip', type=str, default=vflip,help='Display image upside down. For 2 cam, use x,y')
    parser.add_argument('--hflip', type=str, default=hflip,help='Display image as a mirror')
    parser.add_argument('--catego', type=str, default=catego,help='List of categories to detect person, vehicule, bottle, etc...')
    parser.add_argument('--displim', type=int, default=displim,help='Show disparity limit')
    parser.add_argument('--sidebyside', action='store_true',default=sidebyside,help='Display image sidebyside')
    parser.add_argument('--nodetec', action='store_true',default=nodetec,help='Dont detec')
    parser.add_argument('--justdetec', action='store_true',default=justdetec,help='Just detect')
    parser.add_argument('--nocuda', action='store_true',default=False,help='Disable CUDA')
    parser.add_argument('--thread', action='store_true',default=False,help='Display is separated from computations')
    parser.add_argument('--mirror', action='store_true',default=False,help='Display as mirror')
    parser.add_argument('--csi', action='store_true',default=False,help='set to True if camera is connected through CSI')
    parser.add_argument('--nerian', action='store_true',default=nerian,help='set to True if camera is nerian')
    parser.add_argument('--netsize', type=int, default=netsize,help='efficientdet net size')
    parser.add_argument('--ipcam', action='store_true',default=ipcam,help='set to True if camera is ipcam')
    parser.add_argument('--mmcam', action='store_true',default=mmcam,help='set to True if camera is mmcam')
    parser.add_argument('--socketcam', action='store_true',default=socketcam,help='set to True if camera is socketcam')
    parser.add_argument('--tracking', action='store_true',default=nerian,help='set to True if camera is tracking')
    parser.add_argument('--show', action='store_true',default=show,help='set to True if display in main code')
    parser.add_argument('--camPerLine', type=int, default=camPerLine,help='number of cam per line for display')
    parser.add_argument('--threadnet', action='store_true',default=threadnet,help='set to True thread net')
    parser.add_argument('--threadstereo', action='store_true',default=threadstereo,help='set to True thread stereo')
    parser.add_argument('--stereo', action='store_true',default=stereo,help='set to True frame is for stereo')
    parser.add_argument('--netsizes', type=int, default=netsizes,help='netsizes')
    parser.add_argument('--vidout', type=str, default=vidout,help='List of vigear ports')
    parser.add_argument('--vidin', type=str, default=vidin,help='List of vigear ports')
    parser.add_argument('--angleports', type=str, default=angleports,help='List of ports to receive angles')
    parser.add_argument('--camid', type=str, default=camid,help='cam to read')
    parser.add_argument('--camposi', type=str, default=camposi,help='cam world position')
    parser.add_argument('--core', type=str, default=core,help='set cpu core')
    parser.add_argument('--serverip', type=str, default=serverip,help='server address to send angles')
    parser.add_argument('--pid', type=int, default=pid,help='process id')
    parser.add_argument('--cloudstep', type=int, default=cloudstep,help='cloud downsampling')
    parser.add_argument('--rectifydown', type=float, default=rectifydown,help='rectification downsampling')
    parser.add_argument('--cloudports', type=str, default=cloudports,help='List of ports to receive clouds')
    parser.add_argument('--netimgports', type=str, default=netimgports,help='List of ports to receive net images')
    parser.add_argument('--recv', action='store_true',default=recv,help='set to True udp cam receive')
    parser.add_argument('--udp', action='store_true', default=udp,help='Library type')
    parser.add_argument('--compression', type=int, default=compression,help='jpg compression')
    parser.add_argument('--pwd', type=str, default=pwd,help='rstp cam pwd')

    
    return parser.parse_args()
    

