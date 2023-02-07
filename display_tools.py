import os

user = os.environ['HOME']
import numpy as np
import cv2
from config import *
from scipy.spatial import distance_matrix
import mmap
import time
import errno
import numpy as np
from camera_tools import *
from matplotlib.path import Path
import random
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

args = parse_args()

if args.show :
    from vidgear.gears import NetGear
    from vidgear.gears.helper import reducer

################################################################################
def get_fonts_and_padding_from_resolution(resolution_str):
    fontscale = 1
    if resolution_str == 'VGA':
        fontscale = 0.6
    elif resolution_str == 'HD':
        fontscale = 1
    elif resolution_str == 'FHD':
        fontscale = 1.3
    elif resolution_str == '2K':
        fontscale = 1.5

    return fontscale


################################################################################


################################################################################
def set_windows(args):
    window_verti_position = args.window_verti_position
    window_hori_position = args.window_hori_position
    windowName = 'Camera Live Feed'
    if args.fullscreen:
        cv2.namedWindow(windowName, cv2.WINDOW_GUI_NORMAL)  # cv2.WINDOW_NORMAL
        cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        w = args.window_width
        h = args.window_height
        cv2.namedWindow(windowName, cv2.WINDOW_GUI_NORMAL)  # cv2.WINDOW_NORMAL
        cv2.resizeWindow(windowName, w, h)
        cv2.moveWindow(windowName, window_hori_position, window_verti_position)


def TO_DELETE_set_windows(args, cap, i):
    window_verti_position = args.window_verti_position
    window_hori_position = args.window_hori_position
    w = cap.width
    h = cap.height
    cloud_name = cap.cloud_name
    cam_name = cap.cam_name

    camgrid = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [2, 0], [2, 1], [2, 2],
               [2, 3], [2, 4]]

    if args.fullscreen:

        cv2.namedWindow(cam_name, cv2.WINDOW_GUI_NORMAL)  # cv2.WINDOW_NORMAL
        cv2.namedWindow(cam_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(cam_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    else:

        #        window_width=w
        #        window_height=h
        #        print(w)
        #        print(h)
        w = args.window_width
        h = args.window_height

        cv2.namedWindow(cam_name, cv2.WINDOW_GUI_NORMAL)  # cv2.WINDOW_NORMAL

        if args.showcloud:
            cv2.namedWindow(cloud_name, cv2.WINDOW_GUI_NORMAL)  # cv2.WINDOW_NORMAL

        cv2.resizeWindow(cam_name, w, h)
        if args.showcloud:
            cv2.resizeWindow(cloud_name, w, h)

        cv2.moveWindow(cam_name, 0 + window_hori_position + camgrid[i][0] * w,
                       window_verti_position + camgrid[i][1] * h)

    ################################################################################


def display_image_with_stereo_options(args, cap, cloud):
    cam_name = cap.cam_name
    image_data = cap.image_data
    right_image_data = cap.right_image_data
    w = cap.width
    h = cap.height

    if args.sidebyside:
        image = np.concatenate((image_data, right_image_data), axis=1)
        cv2.resizeWindow(cam_name, w, h)

    else:
        image = np.copy(image_data)

    image[-20:-1, -20:-1, :] = 0

    cv2.imshow(cam_name, image)


################################################################################


################################################################################
def display_image(args, i, cap):
    if args.mirror == True:
        cap.image_data = np.copy(cv2.flip(cap.image_data, 1))

    cv2.imshow(cap.cam_name, cap.image_data)


################################################################################


################################################################################
def draw_2d_box(cap, bounding_box_2d, obj_list, fontscale, k,headspng):
    # if cap.detectionconfidence[k] >= 0.1:
    #     color = (255, 255, 0)
    # else:
    #     color = (0, 0, 255)
    ok = True
    if len(cap.distmat)>1:
        dist=cap.distmat[k]
        dist=np.delete(dist,k)
        #dist=dist[np.nonzero(dist)]
        if min(dist) < args.mindist :
            text_str = ' ' if args.nerian else obj_list[cap.label[k]] #'Prudence !'  #
            color = (0, 0, 255)
            ok = False
        else :
            color = (50, 255,255)
            text_str = ' ' if args.nerian else obj_list[cap.label[k]]# 'Super !'  # obj_list[cap.label[k]]

    else:
        color = (50, 255, 255)
        text_str=' ' if args.nerian else obj_list[cap.label[k]]  #obj_list[cap.label[k]]



    if args.smiley :
        radius =int(abs(cap.object_2d_boxes[k][2, 0] - cap.object_2d_boxes[k][0, 0])/3)
        center = cap.object_2d_boxes[k][0,:].astype(int)
        center = cap.object_2d_centers[k].astype(int)

        #center[0]+= int(abs(cap.object_2d_boxes[k][2, 0] - cap.object_2d_boxes[k][0, 0]) / 2)
        center[1]-=int(abs(cap.object_2d_boxes[k][2, 1] - cap.object_2d_boxes[k][0, 1]) / 2.5)
        colors = [(50,255,255),(255,255,255)]
        colorid = random.randrange(0,len(colors))
        cv2.circle(cap.image_to_display, tuple(center),radius , color, cv2.FILLED)
        eyeleft = center + [-radius/3,-radius/3]
        eyeright = center + [radius/3,-radius/3]
        cv2.circle(cap.image_to_display, tuple(eyeleft.astype(int)),int(radius/4) , (0,0, 0), cv2.FILLED)
        cv2.circle(cap.image_to_display, tuple(eyeright.astype(int)),int(radius/4) , (0,0, 0), cv2.FILLED)
        axes = (int(radius/2), int(radius/2))
        angle = 0
        if ok :
            startAngle = 0
            endAngle = 180
            smile = center + np.array([0, radius / 8])

        else:
            startAngle = 180
            endAngle = 360
            smile = center + np.array([0, radius / 2])
        cv2.ellipse(cap.image_to_display, tuple(smile.astype(int)), axes, angle, startAngle, endAngle, (0,0,0),4)

    elif args.smileypng:

        #
        #overlayid = cap.objid[k] % 5
        overlayid = 0 #if ok else 1
        sc = 0.5
        witdth = int(abs(cap.object_2d_boxes[k][2, 0] - cap.object_2d_boxes[k][0, 0]) * sc)
        if overlayid == 0 or overlayid ==4:
            height = int(1 * witdth)
        else:
            height = int(abs(cap.object_2d_boxes[k][3, 1] - cap.object_2d_boxes[k][0, 1])*sc)
        if witdth == 0: witdth = 30
        if height == 0: height = 30


        # overlay = cv2.resize(np.copy(headspng[overlayid]), (witdth, height))

        y = int(bounding_box_2d[0, 1])#-10
        x = int(bounding_box_2d[0, 0])
        [a, b, c] = cap.image_to_display.shape
        wH = min(height, a - y)
        wW = min(witdth, b - x)
        # y=int(max(0,y-(sc-1)/2*(height/sc)))
        # x=int(max(0,x-(sc-1)/2*(witdth/sc)))
        #if overlayid == 5:
        #    y = int(max(0, y - (1) / 4 * (height / sc)))
        print(headspng[overlayid])
        overlay = cv2.resize(np.copy(headspng[overlayid]), (wW, wH))

        cap.image_to_display = cv2.cvtColor(cap.image_to_display, cv2.COLOR_RGB2RGBA)
        if cap.image_to_display[y:y + wH, x:x + wW].shape == overlay.shape:
            # print(cap.image_to_display[y:y + wH, x:x + wW].shape,overlay[:wH,:wW].shape,overlay.shape,wW,wH,x,y)
            bkg = overlay[:, :, 3] == 0
            front = overlay[:, :, 3] != 0
            patch = cap.image_to_display[y:y + wH, x:x + wW]
            patch[front] = overlay[front]
            cap.image_to_display[y:y + wH, x:x + wW] = patch
            # cap.image_to_display[y:y + wH, x:x + wW] = cv2.addWeighted(cap.image_to_display[y:y + wH, x:x + wW], 1,overlay[:wH, :wW], 0.8, 0)

        cap.image_to_display = cv2.cvtColor(cap.image_to_display, cv2.COLOR_RGBA2RGB)
    else:
        cv2.rectangle(cap.image_to_display, (int(bounding_box_2d[0, 0]), int(bounding_box_2d[0, 1])),
                      (int(bounding_box_2d[2, 0]), int(bounding_box_2d[2, 1])),
                      color, 2)  # 3

    font_face = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 1 * fontscale
    font_thickness = 1  # 1
    #if args.tracking:
    #    text_str = 'ID :' + str(cap.trackingids[k])
    #else:
    #    text_str = obj_list[cap.label[k]]

    text_w, text_h = cv2.getTextSize(text_str, font_face, font_scale, font_thickness)[0]
    text_pt = (int(bounding_box_2d[0, 0]), int(bounding_box_2d[0, 1]) - text_h)
    #cv2.putText(cap.image_to_display, text_str, text_pt, font_face, font_scale, (0, 0, 255), font_thickness,
    #            cv2.LINE_AA)
    ################################################################################


################################################################################
def display_distances_on_image(image_data, bounding_box_2d, position, fontscale):
    font_face = cv2.FONT_HERSHEY_DUPLEX
    font_scale = fontscale * 3
    font_thickness = 2
    #                     coins N-O et S-E de la fenêtre 2D
    upperleftcorner = (int(bounding_box_2d[0, 0]), int(bounding_box_2d[0, 1]))
    lowerrightcorner = (int(bounding_box_2d[2, 0]), int(bounding_box_2d[2, 1]))
    lowerleftcorner = (int(bounding_box_2d[3, 0]), int(bounding_box_2d[3, 1]))
    # milieu de la fenètre 2D
    middle_row = int(np.round((upperleftcorner[0] + lowerrightcorner[0]) / 2))
    middle_col = int(np.round((upperleftcorner[1] + lowerrightcorner[1]) / 2))

    text_str4 = ' %.1f' % np.around(
        np.sqrt(np.power(position[0], 2) + np.power(position[1], 2) + np.power(position[2], 2)), 1)

    #text_str4 = ' %.1f' % np.around(position[2], 1)
    text_w, text_h = cv2.getTextSize(text_str4, font_face, font_scale, font_thickness)[0]
    text_pt4 = (middle_row + int(text_w/4), middle_col)


    #text_pt4 = (int(bounding_box_2d[3, 0]), int(bounding_box_2d[3, 1]) +  int(text_h))

    cv2.putText(image_data, text_str4, text_pt4, font_face, font_scale, (0, 0, 255), font_thickness)  # cv2.LINE_AA


################################################################################


##########################################################################################################



import torch
def vis_pose(cap, format='coco'):


    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    CYAN = (255, 255, 0)
    YELLOW = (0, 255, 255)
    ORANGE = (0, 165, 255)
    PURPLE = (255, 0, 255)

    #frame = cap.image_to_display
    im_res =cap.pose

    if format == 'coco':
        l_pair = [
            (0, 1), (0, 2), (1, 3), (2, 4),  # Head
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
            (17, 11), (17, 12),  # Body
            (11, 13), (12, 14), (13, 15), (14, 16)
        ]

        # p_color = [(0, 255, 255), (0, 191, 255),(0, 255, 102),(0, 77, 255), (0, 255, 0), #Nose, LEye, REye, LEar, REar
        #             (77,255,255), (77, 255, 204), (77,204,255), (191, 255, 77), (77,191,255), (191, 255, 77), #LShoulder, RShoulder, LElbow, RElbow, LWrist, RWrist
        #             (204,77,255), (77,255,204), (191,77,255), (77,255,191), (127,77,255), (77,255,127), (0, 255, 255)] #LHip, RHip, LKnee, Rknee, LAnkle, RAnkle, Neck
        # line_color = [(0, 215, 255), (0, 255, 204), (0, 134, 255), (0, 255, 50),
        #             (77,255,222), (77,196,255), (77,135,255), (191,255,77), (77,255,77),
        #             (77,222,255), (255,156,127),
        #             (0,127,255), (255,127,77), (0,77,255), (255,77,36)]

        p_color = [GREEN]*18
        line_color = [BLUE]*15

    elif format == 'mpii':
        l_pair = [
            (8, 9), (11, 12), (11, 10), (2, 1), (1, 0),
            (13, 14), (14, 15), (3, 4), (4, 5),
            (8, 7), (7, 6), (6, 2), (6, 3), (8, 12), (8, 13)
        ]
        p_color = [PURPLE, BLUE, BLUE, RED, RED, BLUE, BLUE, RED, RED, PURPLE, PURPLE, PURPLE, RED, RED, BLUE, BLUE,BLUE,BLUE]
        line_color = [PURPLE, BLUE, BLUE, RED, RED, BLUE, BLUE, RED, RED, PURPLE, PURPLE, RED, RED, BLUE, BLUE]
    else:
        raise NotImplementedError

    #im_name = im_res['imgname'].split('/')[-1]
    img = cap.image_to_display
    height,width = img.shape[:2]

    img = cv2.resize(img,(int(width/2), int(height/2)))

    #for human in im_res['result']:
    for row in im_res :

        part_line = {}
        #kp_preds = row['keypoints']
        #kp_scores = row['kp_score']
        kp_preds = row[:,0:2]
        kp_scores =row[:,2]

        # l_pair = l_pair[4::]
        # kp_preds = kp_preds[4::]
        # kp_scores = kp_scores[4::]
        #
        # tmp = np.zeros((14,2))
        # tmp2 = np.zeros((14,))
        # tmp[0:13,:]=kp_preds
        # tmp2[0:13]=kp_scores.squeeze()
        # tmp[13,:]=(kp_preds[1,:]+kp_preds[2,:])/2
        # tmp2[13]=(kp_scores[1]+kp_scores[2])/2
        # kp_preds = tmp
        # kp_scores = tmp2

        tmp = np.zeros((18,2))
        tmp2 = np.zeros((18,))
        tmp[0:17,:]=kp_preds
        tmp2[0:17]=kp_scores.squeeze()
        tmp[17,:]=(kp_preds[5,:]+kp_preds[6,:])/2
        tmp2[17]=(kp_scores[5]+kp_scores[6])/2
        kp_preds = tmp
        kp_scores = tmp2
        #sword = kp_preds[10,:]-kp_preds[8,:]
        #kp_preds[10,:] =kp_preds[10,:] +sword


        #if args.mirror : kp_preds[:,0] = cap.width - kp_preds[:,0]
        #kp_preds = np.concatenate((kp_preds, np.expand_dims((kp_preds[5,:]+kp_preds[6,:])/2,0)))
        #kp_scores = np.concatenate((kp_scores, np.expand_dims((kp_scores[5,:]+kp_scores[6,:])/2,0)))

        #kp_preds = np.concatenate((kp_preds, (kp_preds[5,:]+kp_preds[6,:])/2,0))
        #kp_scores = np.concatenate((kp_scores, (kp_scores[5,:]+kp_scores[6,:])/2,0))

        #print(len(kp_preds,kp_scores))

        #kp_scores = human['kp_score']
        #kp_preds = torch.cat((kp_preds, torch.unsqueeze((kp_preds[5,:]+kp_preds[6,:])/2,0)))
        #kp_scores = torch.cat((kp_scores, torch.unsqueeze((kp_scores[5,:]+kp_scores[6,:])/2,0)))





        # Draw keypoints
        for n in range(5,kp_scores.shape[0]):
            if kp_scores[n] <= 0.05 or kp_scores[n] >=1:
                continue
            cor_x, cor_y = int(kp_preds[n, 0]), int(kp_preds[n, 1])
            part_line[n] = (int(cor_x/2), int(cor_y/2))
            bg = img.copy()
            cv2.circle(bg, (int(cor_x/2), int(cor_y/2)), 2, p_color[n], 3)
            # Now create a mask of logo and create its inverse mask also
            transparency = float(max(0, min(1, kp_scores[n])))
            transparency=1
            img = cv2.addWeighted(bg, transparency, img, 1-transparency, 0)
        # Draw limbs
        for i, (start_p, end_p) in enumerate(l_pair[5::]):
            if start_p in part_line and end_p in part_line:
                start_xy = part_line[start_p]
                end_xy = part_line[end_p]
                bg = img.copy()

                X = (start_xy[0], end_xy[0])
                Y = (start_xy[1], end_xy[1])
                mX = np.mean(X)
                mY = np.mean(Y)
                length = ((Y[0] - Y[1]) ** 2 + (X[0] - X[1]) ** 2) ** 0.5
                angle = math.degrees(math.atan2(Y[0] - Y[1], X[0] - X[1]))
                stickwidth = (kp_scores[start_p] + kp_scores[end_p]) + 1
                # polygon = cv2.ellipse2Poly((int(mX),int(mY)), (int(length/2), int(stickwidth)), int(angle), 0, 360, 2)
                # cv2.fillConvexPoly(bg, polygon, line_color[i])
                #cv2.line(bg, start_xy, end_xy, line_color[i], int((2 * (kp_scores[start_p] + kp_scores[end_p])) + 1))
                cv2.line(bg, start_xy, end_xy, line_color[i],  4)

                transparency = float(max(0, min(1, 0.5*(kp_scores[start_p] + kp_scores[end_p]))))
                transparency=1
                img = cv2.addWeighted(bg, transparency, img, 1-transparency, 0)
    cap.image_to_display = cv2.resize(img,(width,height),interpolation=cv2.INTER_CUBIC)


def plot_cloud(cloud,ax):
    x = cloud[:,0]
    y = cloud[:,1]
    z = cloud[:,2]

    ax.scatter(x, y, z, c='r', marker='o')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()



def write_detections_on_image(args, cap, obj_cat_id, obj_list,headspng):
    
    for i in range(len(cap)):

            fontscale = get_fonts_and_padding_from_resolution(args.resolution)

            if args.showdisplim :
                if args.mirror:
                    lim = int(cap[i].width - cap[i].displim * (args.rectifydown * args.dispdown))
                else:
                    lim = int(cap[i].displim * (args.rectifydown * args.dispdown))

                cv2.line(cap[i].image_to_display, tuple([lim,0]), tuple([lim,cap[i].height]),(0,0,0), 3, 1, 0)  # top right

            # keep only detections closest to camera
            positions = cap[i].object_center_positions
            if len(positions) != 0:
                distances = np.array(np.linalg.norm(positions, axis=1))
                # confidence = np.array(cap[i].detectionconfidence)
                # distances = (1-confidence)*distances
                sorteddistances = np.argsort(distances)
                keep = sorteddistances[0:args.keepclosest]
                #nbdetec = len(sorteddistances)
                #cap[i].object_center_positions = cap[i].object_center_positions[sorteddistances[0:min(nbdetec, args.keepclosest)]]
                #cap[i].object_2d_boxes = cap[i].object_2d_boxes[sorteddistances[0:min(nbdetec, args.keepclosest)]]
                #cap[i].object_2d_centers = cap[i].object_2d_centers[sorteddistances[0:min(nbdetec, args.keepclosest)]]
                #if args.view_3dbox : cap[i].object_3d_boxes = cap[i].object_3d_boxes[sorteddistances[0:min(nbdetec,args.keepclosest)]]

            ####################################################################
            # LOOP OVER ALL DETECTIONS FOR DISPLAY 
            for k in range(0, min(len(cap[i].object_2d_boxes), args.max_number_objects)):  # len(id_colors)
        
        
                label = cap[i].label[k]  # int(detecs[k,7])
                bounding_box_2d = cap[i].object_2d_boxes[k]
                #headspng.append(cv2.imread('/home/dista/Downloads/zombie.png',cv2.IMREAD_UNCHANGED))
                #headspng.append(cv2.imread('/home/dista/Downloads/mj2.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/babyyoda1.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/babyyoda2.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/babyyoda3.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/babyyoda4.png',cv2.IMREAD_UNCHANGED))
                #headspng.append(cv2.imread('/home/dista/Downloads/babyyoda5.png',cv2.IMREAD_UNCHANGED))
                #headspng.append(cv2.imread('/home/dista/Downloads/ghost.png',cv2.IMREAD_UNCHANGED))
                #headspng.append(cv2.imread('/home/dista/Downloads/ghost2.png',cv2.IMREAD_UNCHANGED))
                #headspng.append(cv2.imread('/home/dista/Downloads/smiley.png',cv2.IMREAD_UNCHANGED))
                #headspng.append(cv2.imread('/home/dista/Downloads/gremlin.png',cv2.IMREAD_UNCHANGED))
                #headspng.append(cv2.imread('/home/dista/Downloads/pacman.png',cv2.IMREAD_UNCHANGED))
                #headspng.append(cv2.imread('/home/dista/Downloads/smurf2.png',cv2.IMREAD_UNCHANGED))

                #headspng.append(cv2.imread('/home/dista/Downloads/clauderoy2.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/smiley3.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/smiley5.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/smiley6.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/smiley7.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/smiley8.png',cv2.IMREAD_UNCHANGED))
                # headspng.append(cv2.imread('/home/dista/Downloads/smiley9.png',cv2.IMREAD_UNCHANGED))


                if args.justdetec:
                    ####################################################################
                    # DRAW 2D BOUNDING BOX
                    if args.mirror == True:
                        bounding_box_2d[:, 0] = cap[i].width - bounding_box_2d[:, 0]
                    if args.view_2dbox:
                        draw_2d_box(cap[i], bounding_box_2d, obj_list, fontscale, k,headspng)
                    #                          if len(cap[i].nexttracking2dbox)!=0:
                    #                              for i in range(len(cap[i].nexttracking2dbox)):
                    #                                  draw_2d_box(cap[i],cap[i].nexttracking2dbox[i],obj_list,fontscale,k)
                    #
                    if args.alphapose:
                        vis_pose(cap[i])




                else:

                    position = np.copy(cap[i].object_center_positions[k])
                    if args.view_3dbox  :
                        dimensions = np.copy(cap[i].object_dimensions[k])
                        bounding_box = np.copy(cap[i].object_3d_boxes[k])


                    ####################################################################
                    # DRAW 2D BOUNDING BOX
                    if args.mirror == True:
                        bounding_box_2d[:, 0] = cap[i].width - bounding_box_2d[:, 0]

                    # if args.mirror == True:
                    #     print(cap[i].pose.shape)
                    #     cap[i].pose[:,:,0] = cap[i].width - cap[i].pose[:,:,0]
                    #     cap[i].wristL[:, 0] = cap[i].width - cap[i].wristL[:, 0]
                    #     cap[i].wristR[:, 0] = cap[i].width - cap[i].wristR[:, 0]

                    #t = time.time()
                    if args.posenet:
                        vis_pose(cap[i])
                    #print('TIMMMME', np.int((time.time() - t) * 1000))

                    if args.view_2dbox:
                        draw_2d_box(cap[i], bounding_box_2d, obj_list, fontscale, k,headspng)


                    if not np.isnan(np.linalg.norm(position)):

                        ####################################################################
                        # DISPLAY DISTANCES AND POSITION ON IMAGE AND SIDE PANEL
                        if args.displaydistance:
                            display_distances_on_image(cap[i].image_to_display, bounding_box_2d, position, fontscale)

                    if args.view_3dbox  and not np.isnan(np.linalg.norm(bounding_box)) and k in keep :#and abs(position[2])<2:

                        ####################################################################
                        # DRAW 3D BOX :
                        imgpts = map_3d_to_2d(args, cap[i], bounding_box)
                        #if max(abs(imgpts.flatten()))<5000:
                        display_3d_bounding_box(cap[i],k, imgpts)

                        ####################################################################
                    # DRAW SEPARATING ARROW _____
        
                    if len(cap[i].object_center_positions) > 1:

                        if args.arrows:
                            display_arrows(cap[i], args.lineupmode, args.lineupdepth, args.maxdist, \
                                           fontscale, args.red_box_arrow_yellow_box, args.mirror, args.nb_neighbors,
                                           args.minheight, args.minwidth, args.mindepth)

                        # t = time.time()

                        if args.handarrows:  # and len(cap.pose):
                            display_handarrows(cap[i], args.lineupmode, args.lineupdepth, args.maxdist, \
                                               fontscale, args.red_box_arrow_yellow_box, args.mirror,
                                               args.nb_neighbors,
                                               args.minheight, args.minwidth, args.mindepth, args.maxdepth)
                        # print('TIMMMmmmMMMMMMMMMMMMMMMMMMMMME', np.int((time.time() - t) * 1000))



                            ####################################################################
def euler_to_rotMat(yaw, pitch, roll):
    Ry_yaw = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]])
    Rx_pitch = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]])
    Rz_roll = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]])
    # R = RzRyRx
    rotMat = np.matmul(Ry_yaw, np.matmul(Rx_pitch, Rz_roll))
    return rotMat

################################################################################    
def map_3d_to_2d(args, cap, points):
    # from old zed info .conf
    #[map_left_x, map_left_y, map_right_x, map_right_y, f, base, px_left, py_left, Q, distCoeffs_left, Tvec, Rvec, R1,
    # camera_matrix_left] = cap.coeff
    #[k1, k2, p1, p2, k3] = distCoeffs_left

    [k1, k2, p1, p2, k3]=cap.coef.distCoefLeft[0]
    R1=np.asarray(cap.coef.R)
    disto=np.asarray(cap.coef.distCoefLeft[0])
    tvec=np.asarray(cap.coef.T)
    rvec = cv2.Rodrigues(R1)[0]
    cam_matrix=np.asarray(cap.coef.cameraMatrixLeft)

    px_left=cam_matrix[0,2]
    py_left=cam_matrix[1,2]
    fx=cam_matrix[0,0]
    fy=cam_matrix[1,1]
    f=(fx+fy)/2

    #rotMat = euler_to_rotMat(0,ang*np.pi/180,0)
    imgpts = np.zeros((len(points), 2))
    for j in range(len(points)):
        point = np.matmul(R1, points[j])
        x = point[0]
        y = point[1]
        z = point[2]
        xp = x / z
        yp = y / z
        r = np.sqrt(np.power(xp, 2) + np.power(yp, 2))
        xpp = xp * (1 + k1 * np.power(r, 2) + k2 * np.power(r, 4) + k3 * np.power(r, 6)) + 2 * p1 * xp * yp + p2 * (
                np.power(r, 2) + 2 * np.power(xp, 2))
        ypp = yp * (1 + k1 * np.power(r, 2) + k2 * np.power(r, 4) + k3 * np.power(r, 6)) + p1 * (
                np.power(r, 2) + 2 * np.power(yp, 2)) + 2 * p2 * xp * yp
        u = int(np.round(xpp * f + px_left))
        v = int(np.round(ypp * f + py_left))

        #impt,jac=cv2.projectPoints(points[j],rvec,tvec,cam_matrix,disto)
        #[u,v]=impt.flatten()
        #impt,jac=cv2.projectPoints(points[j],rvec,tvec,cam_matrix,disto)
        #[u,v]=impt.flatten()

        if args.mirror == True:
            imgpts[j, 0] = cap.width - u
        else:
            imgpts[j, 0] = u
        if args.vmirror:
            imgpts[j, 1] = cap.height - v
        else :
            imgpts[j, 1] = v

    return imgpts.astype(int)


def drawdashedline(img,pt1,pt2,color,thickness=1,style='dotted',gap=20):
    dist =((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5
    pts= []
    for i in  np.arange(0,dist,gap):
        r=i/dist
        x=int((pt1[0]*(1-r)+pt2[0]*r)+.5)
        y=int((pt1[1]*(1-r)+pt2[1]*r)+.5)
        p = (x,y)
        pts.append(p)

    if len(pts)!=0:
        if style=='dotted':
            for p in pts:
                cv2.circle(img,p,thickness,color,-1)
        else:
            #s=pts[0]
            e=pts[0]
            i=0
            for p in pts:
                s=e
                e=p
                if i%2==1:
                    cv2.line(img,s,e,color,thickness)
                i+=1



################################################################################
def display_3d_bounding_box(cap, k,imgpts):
    # alpha=0.2
    # [h,w,c]=overlay.shape
    # poly_path = Path(top.reshape(4,2))
    # y, x = np.mgrid[:h, :w]
    # coors =np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))
    # mask = poly_path.contains_points(coors).reshape(h,w)
    # mask = mask.astype(bool)
    # #cv2.addWeighted(output[mask], 1, overlay[mask], 1 - alpha, 0.0)
    # output[mask] = cv2.addWeighted(image_data, alpha, gradimg, 1 - alpha, 0)[mask]
    # #output[mask] = cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)[mask]

    # shapes =  np.zeros_like(output, np.uint8)
    # cv2.rectangle(shapes, (5, 5), (100, 75), (255, 255, 255), cv2.FILLED)
    # cv2.circle(shapes, (300, 300), 75, (255, 255, 255), cv2.FILLED)
    # alpha = 0.5
    # mask = shapes.astype(bool)
    # output[mask] = cv2.addWeighted(image_data, alpha, gradimg, 1 - alpha, 0)[mask]



    if not args.bottom :
        thick = 8
        thickback=8
    else:
        thick = 8
        thickback=8


    if len(cap.distmat)>1:
        dist=cap.distmat[k]
        dist=np.delete(dist,k)
        #dist=dist[np.nonzero(dist)]
        color = (255, 0, 0) if min(dist) < args.mindist else (255, 0, 0)
    else:
        color = (255, 0, 0)

    image_data = cap.image_to_display

    if max(abs(imgpts.flatten()))<cap.width:

        #top
        # cv2.line(image_data, tuple(imgpts[0 + 4].ravel()), tuple(imgpts[1 + 4].ravel()), color, thickback) #top right
        # cv2.line(image_data, tuple(imgpts[1 + 4].ravel()), tuple(imgpts[2 + 4].ravel()), color, thick) #top back
        # cv2.line(image_data, tuple(imgpts[2 + 4].ravel()), tuple(imgpts[3 + 4].ravel()), color, thickback) #top left
        # #cv2.line(image_data, tuple(imgpts[3 + 4].ravel()), tuple(imgpts[0 + 4].ravel()), color, thickback) #top front
        # drawdashedline(image_data, tuple(imgpts[3+4].ravel()), tuple(imgpts[0+4].ravel()), color, 2, 'dashed', gap=20)
        # bottom
        # cv2.line(image_data, tuple(imgpts[0].ravel()), tuple(imgpts[1].ravel()), color, thickback) # right
        # cv2.line(image_data, tuple(imgpts[1].ravel()), tuple(imgpts[2].ravel()), color, thick) #  front
        # cv2.line(image_data, tuple(imgpts[2].ravel()), tuple(imgpts[3].ravel()), color, thickback) #  left
        # #cv2.line(image_data, tuple(imgpts[3].ravel()), tuple(imgpts[0].ravel()), color, thickback)  #  back
        # drawdashedline(image_data, tuple(imgpts[3].ravel()), tuple(imgpts[0].ravel()), color, 2, 'dashed', gap=20)
        # right
        # #cv2.line(image_data, tuple(imgpts[0].ravel()), tuple(imgpts[0 + 4].ravel()), color, thickback)# side right back
        # #drawdashedline(image_data, tuple(imgpts[0].ravel()), tuple(imgpts[0+4].ravel()), color, 2, 'dashed', gap=20)
        # cv2.line(image_data, tuple(imgpts[1].ravel()), tuple(imgpts[1 + 4].ravel()), color, thick) # side right font
        # cv2.line(image_data, tuple(imgpts[2].ravel()), tuple(imgpts[2 + 4].ravel()), color, thick)# front left
        # #cv2.line(image_data, tuple(imgpts[3].ravel()), tuple(imgpts[3 + 4].ravel()), color, thickback)# side left back
        # drawdashedline(image_data, tuple(imgpts[3].ravel()), tuple(imgpts[3+4].ravel()), color, 2, 'dashed', gap=20)


        overlay = image_data.copy() #image_data.copy()  gradim.copy()
        output = image_data#


        # each face (when facing it) goes from bottom right counter clock wise to bottom left
        bottom = np.array([[imgpts[0],imgpts[1],imgpts[2],imgpts[3]]],np.int32)
        top = np.array([[imgpts[4],imgpts[5],imgpts[6],imgpts[7]]],np.int32)
        rigth = np.array([[imgpts[1],imgpts[5],imgpts[4],imgpts[0]]],np.int32)
        left = np.array([[imgpts[3],imgpts[7],imgpts[6],imgpts[2]]],np.int32)
        front = np.array([[imgpts[0],imgpts[4],imgpts[7],imgpts[3]]],np.int32)
        back = np.array([[imgpts[1],imgpts[5],imgpts[6],imgpts[2]]],np.int32)

        thick = 12
        color=(50,255,255)
        cv2.arrowedLine(image_data, tuple(imgpts[4]-[0,40]), tuple(imgpts[7]-[0,40]), color, thick, 8, 0, 0.1)  # top right
        cv2.arrowedLine(image_data, tuple(imgpts[7]-[0,40]), tuple(imgpts[4]-[0,40]), color, thick, 8, 0, 0.1)  # top right

        thick = 12
        color=(50,255,255)
        cv2.arrowedLine(image_data, tuple(imgpts[3]-[60,0]), tuple(imgpts[7]-[60,0]), color, thick, 8, 0, 0.1)  # top right
        cv2.arrowedLine(image_data, tuple(imgpts[7]-[60,0]), tuple(imgpts[3]-[60,0]), color, thick, 8, 0, 0.1)  # top right

        thick = 7
        color=(50,255,255)
        cv2.arrowedLine(image_data, tuple(imgpts[0]+[60,0]), tuple(imgpts[1]+[60,0]), color, thick, 8, 0, 0.4)  # top right
        cv2.arrowedLine(image_data, tuple(imgpts[1]+[60,0]), tuple(imgpts[0]+[60,0]), color, thick, 8, 0, 0.4)  # top right


        topfront = np.array([[imgpts[0]+(imgpts[4]-imgpts[0])/1.2,imgpts[4],imgpts[7],imgpts[3]+(imgpts[7]-imgpts[3])/1.2]],np.int32)
        bottomfront = np.array([[imgpts[0],imgpts[0]+(imgpts[4]-imgpts[0])/7,imgpts[3]+(imgpts[7]-imgpts[3])/7,imgpts[3]]],np.int32)

        toprigth = np.array([[imgpts[1]+(imgpts[5]-imgpts[1])/1.2,imgpts[5],imgpts[4],imgpts[0]+(imgpts[4]-imgpts[0])/1.2]],np.int32)
        bottomright = np.array([[imgpts[1],imgpts[1]+(imgpts[5]-imgpts[1])/7,imgpts[0]+(imgpts[4]-imgpts[0])/7,imgpts[0]]],np.int32)

        topleft = np.array([[imgpts[3]+(imgpts[7]-imgpts[3])/1.2,imgpts[7],imgpts[6],imgpts[2]+(imgpts[6]-imgpts[2])/1.2]],np.int32)
        bottomleft =  np.array([[imgpts[3],imgpts[3]+(imgpts[7]-imgpts[3])/7,imgpts[2]+(imgpts[6]-imgpts[2])/7,imgpts[2]]],np.int32)


        alpha = 0.1
        cv2.fillPoly(overlay, [bottom], (0,0,255))
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        cv2.fillPoly(overlay, [top], (0,0,255))
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        cv2.fillPoly(overlay, [rigth], (0,0,255))
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        cv2.fillPoly(overlay, [left], (0,0,255))
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

        # alpha = 0.5
        # cv2.fillPoly(overlay1, [top], (0, 0, 255))
        # cv2.addWeighted(overlay1, alpha, output, 1 - alpha, 0, output)
        # cv2.fillPoly(overlay2, [bottom], (0, 0, 255))
        # cv2.addWeighted(overlay2, alpha, output, 1 - alpha, 0, output)


        alpha = 0.1

        # cv2.fillPoly(overlay, [topfront], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        # cv2.fillPoly(overlay, [bottomfront], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

        # cv2.fillPoly(overlay, [top], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        # cv2.fillPoly(overlay, [bottom], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

        alpha = 0.2

        # cv2.fillPoly(overlay, [rigth], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        # cv2.fillPoly(overlay, [bottom], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        # cv2.fillPoly(overlay, [top], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        # cv2.fillPoly(overlay, [left], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        # cv2.fillPoly(overlay, [back], (0, 0, 255))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

        color = (0,0,255)
        cv2.polylines(image_data, [top], True, color, thickness=3)
        cv2.polylines(image_data, [bottom], True, color, thickness=3)
        cv2.polylines(image_data, [rigth], True, color, thickness=3)
        cv2.polylines(image_data, [left], True, color, thickness=3)



        font_face = cv2.FONT_HERSHEY_DUPLEX
        thick = 3
        font_scale = 2
        width = np.around(np.sqrt(np.power(cap.object_dimensions[k][0], 2)), 2)
        height= np.around(np.sqrt(np.power(cap.object_dimensions[k][1], 2)), 2)
        depth = np.around(np.sqrt(np.power(cap.object_dimensions[k][2], 2)), 2)

        largeur = '%.2fm' % width
        hauteur = '%.2fm' % height
        profondeur = '%.2fm' % depth

        text_w, text_h = cv2.getTextSize(profondeur, font_face, font_scale, thick)[0]

        textpt_largeur = (imgpts[7]+(imgpts[4] - imgpts[7])/2 - [0,60]).astype(int)
        textpt_profondeur = (imgpts[0]+(imgpts[1] - imgpts[0])/2 + [80,0]).astype(int)
        textpt_hauteur = (imgpts[3]+(imgpts[7] - imgpts[3])/2 - [60,0]).astype(int)

        font_scale = 2
        #font_scale = font_scale*width
        color=(50,255,255)

        cv2.putText(image_data, largeur, textpt_largeur, font_face, font_scale, color, thick)  # cv2.LINE_AA
        cv2.putText(image_data, profondeur, textpt_profondeur, font_face, font_scale, color, thick)  # cv2.LINE_AA
        cv2.putText(image_data, hauteur, textpt_hauteur, font_face, font_scale, color, thick)  # cv2.LINE_AA


        # midx = int((imgpts[1 + 4][0]+imgpts[2 + 4][0])/2)
        # midy = int((imgpts[0 + 4][1]+imgpts[1 + 4][1])/2)
        # radiusx = int(abs(imgpts[1 + 4][0]-imgpts[2 + 4][0])/2)
        # radiusy = int(abs(imgpts[0 + 4][1]-imgpts[1 + 4][1])/2)
        # angle = 0
        # startAngle = 0
        # endAngle = 360
        # axesLength = (radiusx,radiusy)
        # cv2.ellipse(image_data, (midx,midy), axesLength,angle, startAngle, endAngle, color, thick)
        #cv2.circle(image_data, (midx,midy), radius, color, thick)

        # overlay = image_data.copy()
        # output = image_data#
        # #cv2.rectangle(overlay, (420, 205), (595, 385), (0, 0, 255), -1)
        # alpha=0.2
        # penta = np.array([[[40,160],[120,100],[200,160],[160,240],[80,240]]], np.int32)
        # cv2.polylines(overlay, [penta], True, (0,255,0), thickness=3)
        # #cv2.fillPoly(overlay, [penta], (0,0,0))
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha,0, output)

################################################################################    


################################################################################
def display_arrows(cap, lineupmode, lineupdepth, maxdist, \
                   fontscale, red_box_arrow_yellow_box, mirror, nb_neighbors, minheight, minwidth, mindepth):
    image_data = cap.image_to_display
    distmat = cap.distmat
    imgpts = cap.object_2d_centers

    # LOOP OVER ALL DETECTION/PERSONS

    for i in range(0, distmat.shape[0]):
        
        if not np.isnan(np.linalg.norm(cap.object_center_positions[i])):

            if lineupmode:
                nb_neighbors = 2
                dist = np.copy(distmat[i])
                sortdist = np.argsort(dist)
                sortdist = sortdist[1:min(1 + nb_neighbors, len(sortdist))]
                lineupdepth = lineupdepth
            else:
                dist = np.copy(distmat[i])
                sortdist = np.argsort(dist)
                sortdist = sortdist[1:min(1 + nb_neighbors, len(sortdist))]
                lineupdepth = maxdist
    
            # LOOP OVER ALL NEIGHBOORS
    
            for j in range(0, len(sortdist)):  # if draw to closest neighboors only

                target_id = sortdist[j]
                #obj_h = cap.object_dimensions[i][1]
                #target_h = cap.object_dimensions[target_id][1]
                # obj_w = cap.object_dimensions[i][0]
                # target_w = cap.object_dimensions[target_id][0]
                # obj_d = cap.object_dimensions[i][2]
                # target_d = cap.object_dimensions[target_id][2]
                obj_z = cap.object_center_positions[i][2]
                target_z = cap.object_center_positions[target_id][2]

                if distmat[i, target_id] < 1.95 and distmat[i, target_id] < maxdist : #and obj_z < maxdepth and target_z < maxdepth :#and obj_h > minheight and target_h > minheight and obj_w > minwidth and target_w > minwidth and obj_d > mindepth and target_d > mindepth:
                    midarrow = imgpts[i] + (imgpts[target_id] - imgpts[i]) / 2
                    text_str = str(np.round(distmat[i, target_id], 2))
                    font_face = cv2.FONT_HERSHEY_DUPLEX
                    thick = 3
                    font_scale = fontscale
                    font_thickness = 1
                    text_w, text_h = cv2.getTextSize(text_str, font_face, font_scale, font_thickness)[0]
                    text_pt = (int(midarrow[0]), int(midarrow[1] + text_h+15))

                    if not args.arrowsdist:
                        cv2.putText(image_data, text_str, text_pt, font_face, font_scale, [0, 0, 255], font_thickness,
                                cv2.LINE_AA)
                    cv2.line(image_data, tuple(imgpts[i].ravel()), tuple(imgpts[target_id].ravel()), [0, 0, 255],
                                 int(thick))
    
                if distmat[i, target_id] >= 2 and distmat[i, target_id] < maxdist : # and obj_z < maxdepth and target_z < maxdepth :#and obj_h > minheight and target_h > minheight and obj_w > minwidth and target_w > minwidth and obj_d > mindepth and target_d > mindepth:
                    midarrow = imgpts[i] + (imgpts[target_id] - imgpts[i]) / 2
                    text_str = str(np.round(distmat[i, target_id], 2))
                    font_face = cv2.FONT_HERSHEY_DUPLEX
                    font_scale = fontscale
                    font_thickness = 1
                    text_w, text_h = cv2.getTextSize(text_str, font_face, font_scale, font_thickness)[0]
                    thick = 3
                    text_pt = (int(midarrow[0]), int(midarrow[1] + text_h+15))

                    if not args.arrowsdist:
                        cv2.putText(image_data, text_str, text_pt, font_face, font_scale, [0, 0, 255], font_thickness,
                                cv2.LINE_AA)
                    cv2.line(image_data, tuple(imgpts[i].ravel()), tuple(imgpts[target_id].ravel()), [0, 0, 255],
                             int(thick))
def display_handarrows(cap, lineupmode, lineupdepth, maxdist, \
                   fontscale, red_box_arrow_yellow_box, mirror, nb_neighbors, minheight, minwidth, mindepth, maxdepth):
    image_data = cap.image_to_display
    distmat = cap.distmat
    imgpts = cap.object_2d_centers
    #cloud=np.transpose(np.copy(cap.cloud), (1, 0, 2))
    cloud= cap.cloud
    if args.mirror :cloud[:, 0] = cap.width - cloud[:, 0]





    # LOOP OVER ALL DETECTION/PERSONS
    wristL =np.copy(cap.wristL) /(args.cloudstep * args.rectifydown)
    wristR = np.copy(cap.wristR)/  (args.cloudstep * args.rectifydown)
    pairlist=[]
    positions=cap.object_center_positions

    distances = np.linalg.norm(positions,axis=1)
    sorteddistances = np.argsort(distances)

    if args.mirror:
        defec =np.array([0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60])*(cap.width-1)
    else:
        defec =np.array([0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60])

    #if args.mirror: #because cloud is not flipped
    #    wristL[:,0]=cap.width -wristL[:,0]
    #    wristR[:,0]=cap.width - wristR[:,0]

    #for i in range(0, distmat.shape[0]):
    for i in range(0, 1):
        i= sorteddistances[0]

        if not np.isnan(np.linalg.norm(cap.object_center_positions[i])) :
                #and not np.sum(cap.wristR[i]) in defec:

            if lineupmode:
                nb_neighbors = 2
                dist = np.copy(distmat[i])
                sortdist = np.argsort(dist)
                #sortdist = sortdist[1:min(1 + nb_neighbors, len(sortdist))]
                sortdist = sortdist[1:2]
                lineupdepth = lineupdepth
            else:
                dist = np.copy(distmat[i])
                sortdist = np.argsort(dist)
                #sortdist = sortdist[1:min(1 + nb_neighbors, len(sortdist))]
                sortdist = sortdist[1:2]
                lineupdepth = maxdist

            # LOOP OVER ALL NEIGHBOORS

            for j in range(0, len(sortdist)):  # if draw to closest neighboors only

                target_id = sortdist[j]

                #if not np.sum(cap.wristL[target_id]) in defec and not np.sum(cap.wristR[target_id]) in defec: testing
                a = [i,target_id]
                a.reverse()
                if not a in pairlist and distmat[i, target_id] < maxdist and len(wristL)-1>=i and len(wristL)-1>=target_id and len(wristR)-1>=i and len(wristR)-1>=target_id :  # and obj_z < maxdepth and target_z < maxdepth :#and obj_h > minheight and target_h > minheight and obj_w > minwidth and target_w > minwidth and obj_d > mindepth and target_d > mindepth:
                    pairlist.append([i,target_id])
                    person1L=np.round(wristL[i]).astype(int)
                    person1R=np.round(wristR[i]).astype(int)
                    person2L=np.round(wristL[target_id]).astype(int)
                    person2R=np.round(wristR[target_id]).astype(int)

                    #person2L=np.round(cap.object_2d_centers[target_id]/(args.cloudstep * args.rectifydown)).astype(int)
                    #person2R=np.round(cap.object_2d_centers[target_id]/(args.cloudstep * args.rectifydown)).astype(int)
                    #person2L[0]=cap.width-person2L[0]
                    #person2R[0]=cap.width-person2R[0]

                    #if np.sum(person1L) !=cap.width and np.sum(person1R) !=cap.width and np.sum(person2L) !=cap.width and np.sum(person2R) !=cap.width :


                    pairs = [np.linalg.norm(person1L-person2L), np.linalg.norm(person1L-person2R), np.linalg.norm(person1R-person2L), np.linalg.norm(person1R-person2R)]

                    [a,b,c]=cloud.shape


                    # nperson1L = np.copy(person1L)
                    # nperson1R = np.copy(person1R)
                    # nperson2L = np.copy(person2L)
                    # nperson2R = np.copy(person2R)
                    # nperson1L = (np.copy(person1L) / (args.cloudstep * args.rectifydown)).astype(int)
                    # nperson1R = (np.copy(person1R) / (args.cloudstep * args.rectifydown)).astype(int)
                    # nperson2L = (np.copy(person2L) / (args.cloudstep * args.rectifydown)).astype(int)
                    # nperson2R = (np.copy(person2R) / (args.cloudstep * args.rectifydown)).astype(int)
                    # rad=1
                    # cloudperson1L = cloud[max(0,nperson1L[1]-rad):min(nperson1L[1]+rad,a),max(0,nperson1L[0]-rad):min(nperson1L[0]+rad,b)]
                    # cloudperson1R = cloud[max(0,nperson1R[1]-rad):min(nperson1R[1]+rad,a),max(0,nperson1R[0]-rad):min(nperson1R[0]+rad,b)]
                    # cloudperson2L = cloud[max(0,nperson2L[1]-rad):min(nperson2L[1]+rad,a),max(0,nperson2L[0]-rad):min(nperson2L[0]+rad,b)]
                    # cloudperson2R = cloud[max(0,nperson2R[1]-rad):min(nperson2R[1]+rad,a),max(0,nperson2R[0]-rad):min(nperson2R[0]+rad,b)]
                    #
                    # cloudperson1L = np.reshape(cloudperson1L, (-1, 3))
                    # cloudperson1R = np.reshape(cloudperson1R, (-1, 3))
                    # cloudperson2L = np.reshape(cloudperson2L, (-1, 3))
                    # cloudperson2R = np.reshape(cloudperson2R, (-1, 3))
                    #
                    # meancloudperson1L = np.mean(cloudperson1L,axis=0)
                    # meancloudperson1R = np.mean(cloudperson1R,axis=0)
                    # meancloudperson2L = np.mean(cloudperson2L,axis=0)
                    # meancloudperson2R = np.mean(cloudperson2R,axis=0)

                    rad = 20
                    [a, b, c] = cloud.shape
                    # wristcloudL1 = cloud[max(0, person1L[0] - rad):min(person1L[0] + rad, a),max(0, person1L[1] - rad):min(person1L[1] + rad, b)]
                    # wristcloudR1 = cloud[max(0, person1R[0] - rad):min(person1R[0] + rad, a),max(0, person1R[1] - rad):min(person1R[1] + rad, b)]
                    # wristcloudL2 = cloud[max(0, person2L[0] - rad):min(person2L[0] + rad, a),max(0, person2L[1] - rad):min(person2L[1] + rad, b)]
                    # wristcloudR2 = cloud[max(0, person2R[0] - rad):min(person2R[0] + rad, a),max(0, person2R[1] - rad):min(person2R[1] + rad, b)]

                    wristcloudL1 = cloud[max(0, person1L[1] - rad):min(person1L[1] + rad, a),max(0, person1L[0] - rad):min(person1L[0] + rad, b)]
                    wristcloudR1 = cloud[max(0, person1R[1] - rad):min(person1R[1] + rad, a),max(0, person1R[0] - rad):min(person1R[0] + rad, b)]
                    wristcloudL2 = cloud[max(0, person2L[1] - rad):min(person2L[1] + rad, a),max(0, person2L[0] - rad):min(person2L[0] + rad, b)]
                    wristcloudR2 = cloud[max(0, person2R[1] - rad):min(person2R[1] + rad, a),max(0, person2R[0] - rad):min(person2R[0] + rad, b)]



                    # cv2.rectangle(cap.image_to_display, (int(bounding_box_2d[0, 0]), int(bounding_box_2d[0, 1])),
                    #               (int(bounding_box_2d[2, 0]), int(bounding_box_2d[2, 1])),
                    #               color, 2)  # 3


                    wristcloudL1 = np.reshape(wristcloudL1, (-1, 3))
                    wristcloudR1 = np.reshape(wristcloudR1, (-1, 3))

                    wristcloudL2 = np.reshape(wristcloudL2, (-1, 3))
                    wristcloudR2 = np.reshape(wristcloudR2, (-1, 3))


                    wristcloudL1 = wristcloudL1[~np.isnan(wristcloudL1).any(axis=1)]
                    wristcloudR1 = wristcloudR1[~np.isnan(wristcloudR1).any(axis=1)]
                    wristcloudL1 = wristcloudL1[~np.isinf(wristcloudL1).any(axis=1)]
                    wristcloudR1 = wristcloudR1[~np.isinf(wristcloudR1).any(axis=1)]

                    wristcloudL2 = wristcloudL2[~np.isnan(wristcloudL2).any(axis=1)]
                    wristcloudR2 = wristcloudR2[~np.isnan(wristcloudR2).any(axis=1)]
                    wristcloudL2 = wristcloudL2[~np.isinf(wristcloudL2).any(axis=1)]
                    wristcloudR2 = wristcloudR2[~np.isinf(wristcloudR2).any(axis=1)]

                    wristcloudL1distances = np.linalg.norm(wristcloudL1, axis=1)
                    wristcloudR1distances = np.linalg.norm(wristcloudR1, axis=1)
                    wristcloudL2distances = np.linalg.norm(wristcloudL2, axis=1)
                    wristcloudR2distances = np.linalg.norm(wristcloudL2, axis=1)


                    nbbins = 20
                    keep = 0.5

                    histoL1, edgesL1 = np.histogram(wristcloudL1[:, 2], nbbins)
                    #histoL1, edgesL1 = np.histogram(wristcloudL1distances, nbbins)
                    binmodeL1 = np.argmax(histoL1)
                    binmodeL1sort = np.argsort(histoL1)[::-1]
                    topmin = np.argmin([abs(edgesL1[binmodeL1sort[0]]),abs(edgesL1[binmodeL1sort[1]])
                                         ,abs(edgesL1[binmodeL1sort[2]]),abs(edgesL1[binmodeL1sort[3]]),abs(edgesL1[binmodeL1sort[4]])])
                    binmodeL1 = binmodeL1sort[topmin]
                    zmodeL1 = (edgesL1[binmodeL1] + edgesL1[binmodeL1 + 1]) / 2
                    wristcloudL1 = wristcloudL1[abs(wristcloudL1[:, 2] - zmodeL1) <= keep, :]
                    #wristcloudL1 = wristcloudL1[abs(wristcloudL1[:, 2]) - np.amin(abs(wristcloudL1[:, 2])) <= keep, :]
                    #wristcloudL1 = wristcloudL1[abs(wristcloudL1distances- zmodeL1) <= keep, :]

                    histoR1, edgesR1 = np.histogram(wristcloudR1[:, 2], nbbins)
                    #histoR1, edgesR1 = np.histogram(wristcloudR1distances, nbbins)
                    binmodeR1 = np.argmax(histoR1)
                    binmodeR1sort = np.argsort(histoR1)[::-1]
                    topmin = np.argmin([abs(edgesR1[binmodeR1sort[0]]), abs(edgesR1[binmodeR1sort[1]])
                                          , abs(edgesR1[binmodeR1sort[2]]), abs(edgesR1[binmodeR1sort[3]]),
                                       abs(edgesR1[binmodeR1sort[4]])])
                    binmodeR1 = binmodeR1sort[topmin]
                    zmodeR1 = (edgesR1[binmodeR1] + edgesR1[binmodeR1+ 1]) / 2
                    wristcloudR1 = wristcloudR1[abs(wristcloudR1[:, 2] - zmodeR1) <= keep, :]
                    #wristcloudR1 = wristcloudR1[abs(wristcloudR1[:, 2]) - np.amin(abs(wristcloudR1[:, 2])) <= keep, :]
                    #wristcloudR1 = wristcloudR1[abs(wristcloudL1distances - zmodeR1) <= keep, :]


                    histoL2, edgesL2 = np.histogram(wristcloudL2[:, 2], nbbins)
                    #histoL2, edgesL2 = np.histogram(wristcloudL2distances, nbbins)
                    binmodeL2 = np.argmax(histoL2)
                    binmodeL2sort = np.argsort(histoL2)[::-1]
                    topmin = np.argmin([abs(edgesL2[binmodeL2sort[0]]), abs(edgesL2[binmodeL2sort[1]])
                                          , abs(edgesL2[binmodeL2sort[2]]), abs(edgesL2[binmodeL2sort[3]]),
                                       abs(edgesL2[binmodeL2sort[4]])])
                    binmodeL2 = binmodeL2sort[topmin]
                    zmodeL2 = (edgesL2[binmodeL2] + edgesL2[binmodeL2 + 1]) / 2
                    wristcloudL2 = wristcloudL2[abs(wristcloudL2[:, 2] - zmodeL2) <= keep, :]
                    #wristcloudL2 = wristcloudL2[abs(wristcloudL2[:, 2]) - np.amin(abs(wristcloudL2[:, 2])) <= keep, :]
                    #wristcloudL2 = wristcloudR2[abs(wristcloudL2distances - zmodeL2) <= keep, :]


                    histoR2, edgesR2 = np.histogram(wristcloudR2[:, 2], nbbins)
                    #histoR2, edgesR2 = np.histogram(wristcloudR2distances, nbbins)
                    binmodeR2 = np.argmax(histoR2)
                    binmodeR2sort = np.argsort(histoR2)[::-1]
                    topmin = np.argmin([abs(edgesR2[binmodeR2sort[0]]), abs(edgesR2[binmodeR2sort[1]])
                                           , abs(edgesR2[binmodeR2sort[2]]), abs(edgesR2[binmodeR2sort[3]]),
                                        abs(edgesR2[binmodeR2sort[4]])])
                    binmodeR2 = binmodeR2sort[topmin]
                    zmodeR2 = (edgesR2[binmodeR2] + edgesR2[binmodeR2+ 1]) / 2
                    #wristcloudR2 = wristcloudR2[abs(wristcloudR2[:, 2] - zmodeR2) <= keep, :]
                    wristcloudR2 = wristcloudR2[abs(wristcloudR2[:, 2]) - np.amin(abs(wristcloudR2[:, 2])) <= keep, :]
                    #wristcloudR2 = wristcloudR2[abs(wristcloudR2distances - zmodeR2) <= keep, :]


                    # wristcloudL1 = wristcloudL1[abs(wristcloudL1[:, 2] - np.amin(wristcloudL1)) <= keep, :]
                    # wristcloudR1 = wristcloudR1[abs(wristcloudR1[:, 2] - np.amin(wristcloudR1)) <= keep, :]
                    # wristcloudL2 = wristcloudL2[abs(wristcloudL2[:, 2] - np.amin(wristcloudL2))<= keep, :]
                    # wristcloudR2 = wristcloudR2[abs(wristcloudR2[:, 2] - np.amin(wristcloudR2)) <= keep, :]

                    wristL1position = np.mean(wristcloudL1, axis=0)
                    wristR1position = np.mean(wristcloudR1, axis=0)
                    wristL2position = np.mean(wristcloudL2, axis=0)
                    wristR2position = np.mean(wristcloudR2, axis=0)


                    # wristL1position = np.amin(wristcloudL1)
                    # wristR1position = np.amin(wristcloudL1)
                    # wristL2position = np.amin(wristcloudL1)
                    # wristR2position = np.amin(wristcloudL1)

                    # pairs = [np.linalg.norm(wristL1position - wristL2position),
                    #          np.linalg.norm(wristL1position - wristR2position),
                    #          np.linalg.norm(wristR1position - wristL2position),
                    #          np.linalg.norm(wristR1position - wristR2position)]


                    minposi = np.argmin(pairs)

                    # if args.mirror:  # deflip
                    #     person1L[0]= cap.width-person1L[0]
                    #     person1R[0]= cap.width-person1R[0]
                    #     person2L[0]= cap.width-person2L[0]
                    #     person2R[0]= cap.width-person2R[0]


                        # cv2.rectangle(cap.image_to_display,
                        #               (max(0, cap.width - person1L[0] - rad), max(0, person1L[1] - rad)),
                        #               (min(cap.width - person1L[0] + rad, b), min(person1L[1] + rad, a)),
                        #               (0, 0, 255), 2)  #

                    person1L =(person1L * args.cloudstep * args.rectifydown).astype(int)  # because image is full size unlike the cloud
                    person1R =(person1R * args.cloudstep * args.rectifydown).astype(int)
                    person2L =(person2L * args.cloudstep * args.rectifydown).astype(int)
                    person2R =(person2R * args.cloudstep * args.rectifydown).astype(int)

                    # print(wristL1position,cap.object_center_positions[i])
                    # print(wristR1position,cap.object_center_positions[i])
                    # print(wristL2position,cap.object_center_positions[target_id])
                    # print(wristR2position,cap.object_center_positions[target_id])

                    # if np.linalg.norm(wristL1position-cap.object_center_positions[i])<3\
                    #     and np.linalg.norm(wristR1position - cap.object_center_positions[i])<3\
                    #     and np.linalg.norm(wristL2position - cap.object_center_positions[target_id])<3\
                    #     and np.linalg.norm(wristR2position - cap.object_center_positions[target_id])<3:

                    font_face = cv2.FONT_HERSHEY_DUPLEX
                    thick = 3
                    font_scale = fontscale *1.2
                    font_thickness = 1

                    thick = 3
                    hshift=20
                    hand=0.10
                    text_str = "?"
                    #minposi=2
                    [a,b,c]=cap.image_to_display.shape
                    if minposi == 0:
                        midarrow = person1L + (person2L - person1L) / 2
                        text_pt = (int(midarrow[0]-hshift), int(midarrow[1] - 20))
                        text_str = str(np.round(np.linalg.norm(wristL1position-wristL2position)-hand, 2))
                        #text_str = 'Distance à venir'
                        cv2.line(cap.image_to_display, tuple(person1L.ravel()), tuple(person2L.ravel()), [0, 0, 255],int(thick))
                        cv2.rectangle(cap.image_to_display,
                                      (max(0, person1L[0] - rad), max(0, person1L[1] - rad)),
                                      (min(person1L[0] + rad, b), min(person1L[1] + rad, a)),
                                      (0, 0, 255), 2)  #
                        cv2.rectangle(cap.image_to_display,
                                      (max(0, person2L[0] - rad), max(0, person2L[1] - rad)),
                                      (min(person2L[0] + rad, b), min(person2L[1] + rad, a)),
                                      (0, 0, 255), 2)  #
                    elif minposi == 1:
                        midarrow = person1L + (person2R - person1L) / 2
                        text_pt = (int(midarrow[0]-hshift), int(midarrow[1] - 20))
                        text_str = str(np.round(np.linalg.norm(wristL1position - wristR2position)-hand, 2))
                        #text_str = 'Distance à venir'
                        cv2.line(cap.image_to_display, tuple(person1L.ravel()), tuple(person2R.ravel()), [0, 0, 255],int(thick))
                        cv2.rectangle(cap.image_to_display,
                                      (max(0, person1L[0] - rad), max(0, person1L[1] - rad)),
                                      (min(person1L[0] + rad, b), min(person1L[1] + rad, a)),
                                      (0, 0, 255), 2)  #
                        cv2.rectangle(cap.image_to_display,
                                      (max(0, person2R[0] - rad), max(0, person2R[1] - rad)),
                                      (min(person2R[0] + rad, b), min(person2R[1] + rad, a)),
                                      (0, 0, 255), 2)  #
                    elif minposi == 2:
                        midarrow = person1R + (person2L - person1R) / 2
                        text_pt = (int(midarrow[0]-hshift), int(midarrow[1] - 20))
                        text_str = str(np.round(np.linalg.norm(wristR1position - wristL2position)-hand, 2))
                        #text_str = 'Distance à venir'
                        cv2.line(cap.image_to_display, tuple(person1R.ravel()), tuple(person2L.ravel()), [0, 0, 255],int(thick))
                        cv2.rectangle(cap.image_to_display,
                                      (max(0, person1R[0] - rad), max(0, person1R[1] - rad)),
                                      (min(person1R[0] + rad, b), min(person1R[1] + rad, a)),
                                      (0, 0, 255), 2)  #
                        cv2.rectangle(cap.image_to_display,
                                      (max(0, person2L[0] - rad), max(0, person2L[1] - rad)),
                                      (min(person2L[0] + rad, b), min(person2L[1] + rad, a)),
                                      (0, 0, 255), 2)  #
                    elif minposi == 3:
                        midarrow = person1R + (person2R - person1R) / 2
                        text_pt = (int(midarrow[0]-hshift), int(midarrow[1] - 20))
                        text_str = str(np.round(np.linalg.norm(wristR1position - wristR2position)-hand, 2))
                        #text_str = 'Distance à venir'
                        cv2.line(cap.image_to_display, tuple(person1R.ravel()), tuple(person2R.ravel()), [0, 0, 255],int(thick))

                        cv2.rectangle(cap.image_to_display,
                                      (max(0, person1R[0] - rad), max(0, person1R[1] - rad)),
                                      (min(person1R[0] + rad, b), min(person1R[1] + rad, a)),
                                      (0, 0, 255), 2)  #
                        cv2.rectangle(cap.image_to_display,
                                      (max(0, person2R[0] - rad), max(0, person2R[1] - rad)),
                                      (min(person2R[0] + rad, b), min(person2R[1] + rad, a)),
                                      (0, 0, 255), 2)

                    #cv2.putText(cap.image_to_display, text_str, text_pt, font_face, font_scale, [0, 0, 255], font_thickness,
                    #                cv2.LINE_AA)

                    cv2.putText(cap.image_to_display, 'En progres...', [80,80], font_face, 3, [0, 0, 255],
                                font_thickness,
                                cv2.LINE_AA)


#h, w = [270,480]
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#writer = cv2.VideoWriter('/home/dista/Documents/QDS_cam_images/camcounts/detectcam58.avi', fourcc, 20, (w, h))


def display_and_record(args, capList):
    finalPicture = None
    frameLine = None
    camPerLine = 1
    camCount = len(capList)
    if camCount > 3:
        camPerLine = int(np.sqrt(camCount)) +1

    lineIndex = 0
    imgHeight = 0
    imgWidth = 0
    
    windowName = 'Camera Live Feed'
    resizefactor =  1/4
#    w = args.window_width
#    h = args.window_height
#    cv2.resizeWindow(windowName, (int(w*resizefactor), int(h*resizefactor)))

    #  Scan all pictures
    for i in range(camCount):
        k = cv2.waitKey(1)
        if k == ord('a'):
            opencv_adjust(capList[i])

        #if k != -1:
        #    opencv_camera_settings(k, capList[i])

        #if not args.mmcam and not args.nanocam:
        #    capList[i].showDebug()
            # Display the picture with the box (computation result)
        image = capList[i].image_to_display

        if image is None:
            continue
        # imgHeight, imgWidth, _ = image.shape
        imgWidth = int(args.window_width)
        imgHeight = int(args.window_height)

        image = cv2.resize(image, (int(imgWidth / camPerLine), int(imgHeight / camPerLine)))
            

        lineIndex = lineIndex + 1
        if frameLine is None:
            frameLine = image
        else:
            frameLine = np.concatenate((frameLine, image), axis=1)
            if lineIndex >= camPerLine:
                #  the line is full : append to previously created
                lineIndex = 0
                if finalPicture is None:
                    finalPicture = frameLine
                else:
                    finalPicture = np.concatenate((finalPicture, frameLine), axis=0)
                frameLine = None

    #  Add the last pictures
    if frameLine is not None:
        if camPerLine - lineIndex > 0:
            blankImage = np.zeros( (int(imgHeight / camPerLine), int(imgWidth / camPerLine) * (camPerLine - lineIndex), 3), dtype=np.uint8)
            frameLine = np.concatenate((frameLine, blankImage), axis=1)
        if finalPicture is None:
            # There was only 1 line of picture
            finalPicture = frameLine
        else:
            finalPicture = np.concatenate((finalPicture, frameLine), axis=0)

    if finalPicture is None:
        return


#    finalPicture=cv2.resize(finalPicture,(int(finalPicture.shape[1]*resizefactor),
#                                          int(finalPicture.shape[0]*resizefactor)))

    
    #cv2.waitKey(1)
    cv2.imshow(windowName, finalPicture)
    #cv2.imshow(windowName, capList[0].disparity_to_display)




def display_avg_obj_count(frame, displayWidth, avg):
    debugTextSize = displayWidth / 1280
    thickness = 1 if displayWidth < 1280 else 2
    TEXT_COLOR = (0, 0, 255)
    TEXT_POSITION = (0, 0)
    textPosX, textPosY = TEXT_POSITION
    textPosX += int(40 * debugTextSize)
    textPosY += int(40 * debugTextSize)
    cv2.putText(frame, f'Max person count in last 5 frames : {avg} ',
                (textPosX, textPosY),
                cv2.FONT_HERSHEY_SIMPLEX, debugTextSize, TEXT_COLOR, thickness,
                cv2.LINE_AA)


def memfile(args,camCount):

    
    camPerLine = 1
#    if camCount > 3:
    camPerLine = int(np.sqrt(camCount)) +1    
    
    resizefactor = 1 if args.show else 0.1

    
    w = int(args.window_width  * resizefactor * camPerLine)
    h = int(args.window_height  * resizefactor)
    n = (h*w*3)
    
    fd = os.open('/tmp/img_mmap', os.O_CREAT | os.O_TRUNC | os.O_RDWR)
    os.truncate(fd, n)  # resize file
    
    return [fd,n]




def img_pipe():
    
#    FIFO = '/var/run/mypipe'
    FIFO = '/home/dista/Npipe.mpjg'
    try:
        os.mkfifo(FIFO)
    except OSError as oe: 
        if oe.errno != errno.EEXIST:
            raise

#    os.mkfifo(FIFO)
    
    return FIFO













