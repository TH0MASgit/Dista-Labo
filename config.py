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
    mindist = 0
    max_number_objects=10000
    minheight=0.0
    minwidth=0.0
    mindepth=0.0
    maxdepth=100.0
    resolution='VGA'
    depth_mode='ULTRA'
    hold_for=1
    detection_threshold=0.1
    nonmax_threshold=0.3
    min_z=0.2
    max_z=40
    window_width=800
    window_height=480
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
    displim=48
    sidebyside=False
    justcloud=False
    nodetec =False
    justdetec =False
    nocuda=False
    thread=False
    mirror=False
    vmirror=False
    showdisplim =False

    csi=False
    nerian=False
    netsize=0
    mmcam=False
    socketcam = False
    ipcam = False
    tracking=False    
    display=None
    show=False
    sendimg=False
    camPerLine = 1
    threadnet=False
    threadstereo = False
    stereo = False
    netsizes= [512, 640, 768, 896, 1024, 1280, 1280, 1536,1920]
    camid=[]
    vidin=[]
    vidout=[]
    angleports = []
    camposi = [0,0,0]
    core = []
    serverip = '192.168.1.22'
    pid = 0
    cloudstep=1
    rectifydown = 1
    cloudports = []
    netimgports = []
    sn='12345678'
    udp=False
    recv=False
    compression=80
    pwd='m0P04b*PYMG'
    imsplit = 1
    yolo4 = False
    yolo5 = False
    yolo7 = False
    posenet = False
    overlap = 50
    zsign = False
    displayposition = False
    computeposition = False
    segment = False
    feet = False
    head = False
    bottom= False

    separatedisplay = False
    scatter = False
    inout = False
    dispinout = False
    dispcount = False
    scatterselect = False
    hist2d = False
    globalmap=False
    inoutdirection= []
    camidinout=[]
    accumulatecounts=5
    inoutreceive=False
    inoutsend=False
    inoutcamid=[]
    dataset=False
    datatrain=False
    datavalid = False
    thisset='0'
    rectify = False
    netrectify = False
    use16 = False
    bm=False
    dispdown=2
    bmcuda=False
    euler=[]
    bright=5
    smiley=False
    smileypng=False
    arrowsdist = False
    handarrows=False
    timeavg=1
    keepclosest=1


    distaparser = argparse.ArgumentParser(description='Projet Dista')
    
    # Selecting database
    # If this is omitted, an in-memory database will be used
    distaparser.add_argument('--db', '--database', help="Database connection string")
    #TODO Support a real db connection string:
    # https://docs.sqlalchemy.org/en/13/core/engines.html
    
    # Selecting cameras and machines
    # If these are omitted, they will be loaded from the database
    distaparser.add_argument('-c', '--camera', dest='cameras', action='append', default=[],
                        help="Camera url(s)")
    #TODO Replace these with zed|opencv://username:password@host:port/serial
    # See https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse
    
    # Deprecated (this is the same as a --camera without an ip address)
    distaparser.add_argument('--sn', '--serial', dest='cameras', action='append',
                        help="[Deprecated: use -c instead] Camera serial number(s)")
    distaparser.add_argument('--ip', '--ip_address', action='append', default=[], help="Streamer ip address(es)")

    # Other parameters
    distaparser.add_argument('--usb', action='store_true', default=usb,help='connection type')    
    distaparser.add_argument('--opencv', action='store_true', default=opencv,help='Library type')
    distaparser.add_argument('--fullscreen', action='store_true', default=fullscreen,help='Full screen display') 
    distaparser.add_argument('--display_title', action='store_true', default=display_title,help='Display title ')    
    distaparser.add_argument('--resolution', type=str, default=resolution,help='Resolution : VGA, HD, FHD ,2K')
    distaparser.add_argument('--display', type=str, default=display,help='Display Resolution : VGA, HD, FHD ,2K')
    distaparser.add_argument('--hold_for', type=int, default=hold_for,help='Number of frames held with same distance')
    distaparser.add_argument('--view_3dbox', action='store_true', default=view_3dbox,help='Display 3D box : NOT FOR PUBLIC USE')
    distaparser.add_argument('--view_2dbox', action='store_true', default=view_2dbox,help='Display 2D box : NOT FOR PUBLIC USE')
    distaparser.add_argument('--displaydistance', action='store_true', default=displaydistance,help='Display distance on objects')
    distaparser.add_argument('--red_box_arrow_yellow_box', action='store_true', default=red_box_arrow_yellow_box,help='Display distances with boxes instead of arrows')
    distaparser.add_argument('--lineupmode', action='store_true', default=lineupmode,help='For lineups')
    distaparser.add_argument('--record', action='store_true', default=record,help='Record video : CAREFUL DO NOT RECORD TOO LONG IN FHD')
    distaparser.add_argument('--wait', type=int, default=wait,help='Frame step for recording: ONE or more')    
    distaparser.add_argument('--vidid', type=str, default=vidid,help='Time of recording')      
    distaparser.add_argument('--side_panel', action='store_true', default=side_panel,help='Display side panel : NOT FOR PUBLIC USE')
    distaparser.add_argument('--lineupdepth', type=float, default=lineupdepth,help='Maximum depth of lineup')
    distaparser.add_argument('--nb_neighbors', type=int, default=nb_neighbors,help='Maximum number of arrows coming out of one person : OVERRIDEN BY LINEUP MODE')
    distaparser.add_argument('--maxdist', type=float, default=maxdist,help='Maximum distance between persons')
    distaparser.add_argument('--mindist', type=float, default=mindist,help='Minimum distance between persons')

    distaparser.add_argument('--max_number_objects', type=int, default=max_number_objects,help='Maximum number of persons detected')
    distaparser.add_argument('--minheight', type=float, default=minheight,help='Minimum height of objects')
    distaparser.add_argument('--minwidth', type=float, default=minwidth,help='Minimum width of objects')
    distaparser.add_argument('--mindepth', type=float, default=mindepth,help='Minimum depth of objects')
    distaparser.add_argument('--maxdepth', type=float, default=maxdepth,help='Maximum depth of objects')
    distaparser.add_argument('--depth_mode', type=str, default=depth_mode,help='Resolution : ULTRA, QUALITY, MEDIUM, PERFORMANCE')
    distaparser.add_argument('--detection_threshold', type=float, default=detection_threshold,help='Detection confidence, Max = 100') 
    distaparser.add_argument('--nonmax_threshold', type=float, default=nonmax_threshold,help='Non max supression') 
    distaparser.add_argument('--min_z', type=float, default=min_z,help='Minimum depth : KEEP at 1')
    distaparser.add_argument('--max_z', type=float, default=max_z,help='Maximum depth: Keep at 40')
    distaparser.add_argument('--window_width', type=int, default=window_width,help='Truck display width')
    distaparser.add_argument('--window_height', type=int, default=window_height,help='truck display height')
    distaparser.add_argument('--window_hori_position', type=int, default=window_hori_position,help='Truck side window horizontal position')    
    distaparser.add_argument('--window_verti_position', type=int, default=window_verti_position,help='Truck side window vertical position')    
    distaparser.add_argument('--nbframes_per_cam', type=int, default=nbframes_per_cam,help='nbframes_per_cam')    
    distaparser.add_argument('--linuxid', type=str, default=linuxid,help='List of camera USB port id : 0,1,2,3,4...')
    distaparser.add_argument('--arrows', action='store_true', default=arrows,help='display arrows between persons')    
    distaparser.add_argument('--adjust', action='store_true', default=adjust,help='Adjust image quality')    
    distaparser.add_argument('--showcloud', action='store_true', default=showcloud,help='Show disparity/cloud')    
    distaparser.add_argument('--cloudtrackbar', action='store_true', default=cloudtrackbar,help='Show trackbar for disparity')    
    distaparser.add_argument('--threadframes', action='store_true', default=threadframes,help='thread frames')    
    distaparser.add_argument('--nanocam', action='store_true', default=nanocam,help='camera open with nanocamera library')    
    distaparser.add_argument('--zed', action='store_true', default=zed,help='zed open with zed library')    
    distaparser.add_argument('--opencv_cloud', action='store_true', default=opencv_cloud,help='compute cloud with opencv')    
    distaparser.add_argument('--displayloop', action='store_true', default=displayloop,help='activate display loop option : no detection')    
    distaparser.add_argument('--ports_in', type=str, default=ports_in,help='List of camera USB streaming port : 5555,5556 etc...')
    distaparser.add_argument('--ports_out', type=str, default=ports_out,help='List of camera USB streaming port : 5555,5556 etc...')
    distaparser.add_argument('--vflip', type=str, default=vflip,help='Display image upside down. For 2 cam, use x,y')
    distaparser.add_argument('--hflip', type=str, default=hflip,help='Display image as a mirror')
    distaparser.add_argument('--catego', type=str, default=catego,help='List of categories to detect person, vehicule, bottle, etc...')
    distaparser.add_argument('--displim', type=int, default=displim,help=' disparity limit')
    distaparser.add_argument('--sidebyside', action='store_true',default=sidebyside,help='Display image sidebyside')
    distaparser.add_argument('--nodetec', action='store_true',default=nodetec,help='Dont detec')
    distaparser.add_argument('--justdetec', action='store_true',default=justdetec,help='Just detect')
    distaparser.add_argument('--nocuda', action='store_true',default=False,help='Disable CUDA')
    distaparser.add_argument('--thread', action='store_true',default=False,help='Display is separated from computations')
    distaparser.add_argument('--mirror', action='store_true',default=mirror,help='Display as mirror')
    distaparser.add_argument('--vmirror', action='store_true',default=vmirror,help='mirror vertical flip')

    distaparser.add_argument('--csi', action='store_true',default=False,help='set to True if camera is connected through CSI')
    distaparser.add_argument('--nerian', action='store_true',default=nerian,help='set to True if camera is nerian')
    distaparser.add_argument('--netsize', type=int, default=netsize,help='efficientdet net size')
    distaparser.add_argument('--ipcam', action='store_true',default=ipcam,help='set to True if camera is ipcam')
    distaparser.add_argument('--mmcam', action='store_true',default=mmcam,help='set to True if camera is mmcam')
    distaparser.add_argument('--socketcam', action='store_true',default=socketcam,help='set to True if camera is socketcam')
    distaparser.add_argument('--tracking', action='store_true',default=nerian,help='set to True if camera is tracking')
    distaparser.add_argument('--show', action='store_true',default=show,help='set to True if display in main code')
    distaparser.add_argument('--sendimg', action='store_true',default=show,help='set to True if send image to antother computer')
    distaparser.add_argument('--camPerLine', type=int, default=camPerLine,help='number of cam per line for display')
    distaparser.add_argument('--threadnet', action='store_true',default=threadnet,help='set to True thread net')
    distaparser.add_argument('--threadstereo', action='store_true',default=threadstereo,help='set to True thread stereo')
    distaparser.add_argument('--stereo', action='store_true',default=stereo,help='set to True frame is for stereo')
    distaparser.add_argument('--netsizes', type=int, default=netsizes,help='netsizes')
    distaparser.add_argument('--vidout', type=str, default=vidout,help='List of vigear ports')
    distaparser.add_argument('--vidin', type=str, default=vidin,help='List of vigear ports')
    distaparser.add_argument('--angleports', type=str, default=angleports,help='List of ports to receive angles')
    distaparser.add_argument('--camid', type=str, default=camid,help='cam to read')
    distaparser.add_argument('--camposi', type=str, default=camposi,help='cam world position')
    distaparser.add_argument('--core', type=str, default=core,help='set cpu core')
    distaparser.add_argument('--serverip', type=str, default=serverip,help='server address to send angles')
    distaparser.add_argument('--pid', type=int, default=pid,help='process id')
    distaparser.add_argument('--cloudstep', type=int, default=cloudstep,help='cloud downsampling')
    distaparser.add_argument('--rectifydown', type=float, default=rectifydown,help='rectification downsampling')
    distaparser.add_argument('--cloudports', type=str, default=cloudports,help='List of ports to receive clouds')
    distaparser.add_argument('--netimgports', type=str, default=netimgports,help='List of ports to receive net images')
    distaparser.add_argument('--recv', action='store_true',default=recv,help='set to True udp cam receive')
    distaparser.add_argument('--udp', action='store_true', default=udp,help='Library type')
    distaparser.add_argument('--compression', type=int, default=compression,help='jpg compression')
    distaparser.add_argument('--pwd', type=str, default=pwd,help='rstp cam pwd')
    distaparser.add_argument('--imsplit', type=int, default=imsplit,help='split image in quadrants')
    distaparser.add_argument('--yolo4', action='store_true', default=yolo4,help='detect with yolo 4')
    distaparser.add_argument('--yolo5', action='store_true', default=yolo5,help='detect with yolo 5')
    distaparser.add_argument('--yolo7', action='store_true', default=yolo7,help='detect with yolo 7')

    distaparser.add_argument('--overlap', type=int, default=overlap,help='overlap for quadrant image split')
    distaparser.add_argument('--zsign', action='store_true', default=zsign,help='do not switch z sign')
    distaparser.add_argument('--displayposition', action='store_true', default=displayposition,help='display box position in metric coordinates')
    distaparser.add_argument('--computeposition', action='store_true', default=computeposition,help='compute box position in metric coordinates')

    distaparser.add_argument('--segment', action='store_true', default=segment,help='segment image into polygons')
    distaparser.add_argument('--feet', action='store_true', default=feet,help='position feet')
    distaparser.add_argument('--head', action='store_true', default=head,help='position head')

    distaparser.add_argument('--separatedisplay', action='store_true', default=separatedisplay,help='show cam individualy')
    distaparser.add_argument('--scatter', action='store_true', default=scatter,help='show point scatter plot')
    distaparser.add_argument('--inout', action='store_true', default=inout,help='in and out counting')
    distaparser.add_argument('--dispcount', action='store_true', default=dispcount,help='display count')
    distaparser.add_argument('--dispinout', action='store_true', default=dispinout,help='display in and out counting')
    distaparser.add_argument('--scatterselect', action='store_true', default=scatterselect,help='select region scatter plot')
    distaparser.add_argument('--hist2d', action='store_true', default=hist2d,help='2d histogramm of scatter points')
    distaparser.add_argument('--globalmap', action='store_true', default=globalmap,help='globalmap')
    distaparser.add_argument('--inoutdirection', type=str, default=inoutdirection,help='in and out directions')
    distaparser.add_argument('--camidinout', type=str, default=camidinout,help=' in and out cams')
    distaparser.add_argument('--accumulatecounts', type=int, default=accumulatecounts,help='lenght of list to average counts')
    distaparser.add_argument('--inoutsend', action='store_true', default=inoutsend,help='send in out')
    distaparser.add_argument('--inoutreceive', action='store_true', default=inoutreceive,help='send in out')
    distaparser.add_argument('--inoutcamid', type=str, default=inoutcamid,help='in out cams')
    distaparser.add_argument('--dataset', action='store_true', default=dataset,help='write dataset')
    distaparser.add_argument('--datatrain', action='store_true', default=datatrain,help='write dataset')
    distaparser.add_argument('--datavalid', action='store_true', default=datavalid,help='write dataset')
    distaparser.add_argument('--thisset', type=str, default=thisset,help='just to number image taking a diffrent time of the day')
    distaparser.add_argument('--rectify', action='store_true', default=rectify,help='rectify images')
    distaparser.add_argument('--netrectify', action='store_true', default=netrectify, help='rectify net images')

    distaparser.add_argument('--use16', action='store_true', default=use16,help='use 16bits floats for net')
    distaparser.add_argument('--bm', action='store_true', default=bm,help='use simple block matching for stereo')
    distaparser.add_argument('--dispdown', type=int, default=dispdown,help='stereo downscale')
    distaparser.add_argument('--bmcuda', action='store_true', default=bmcuda,help='use cuda for stereo BM')
    distaparser.add_argument('--bottom', action='store_true', default=bottom,help='only show bottom of 3d box')
    distaparser.add_argument('--euler', type=str, default=euler,help='cam angles')
    distaparser.add_argument('--bright', type=int, default=bright,help='opencv brightness')
    distaparser.add_argument('--smiley', action='store_true', default=smiley,help='display smiley')
    distaparser.add_argument('--smileypng', action='store_true', default=smileypng,help='display smiley')
    distaparser.add_argument('--arrowsdist', action='store_true', default=arrowsdist,help='display distance on arrows')
    distaparser.add_argument('--handarrows', action='store_true', default=handarrows,help='display arrows between hands')
    distaparser.add_argument('--posenet', action='store_true', default=posenet,help='compute pose net')
    distaparser.add_argument('--timeavg', type=int, default=timeavg,help='number of frame to average stereo')
    distaparser.add_argument('--keepclosest', type=int, default=keepclosest,help='number of detection closest to camera to keep')
    distaparser.add_argument('--showdisplim', action='store_true', default=showdisplim,help='display disparity limit')

    return distaparser.parse_known_args()[0]

