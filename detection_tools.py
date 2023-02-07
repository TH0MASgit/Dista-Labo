import os
import sys

user = os.environ['HOME']
path = os.path.dirname(os.path.realpath(__file__)) + '/efficientdetection'
sys.path.append(path)
os.chdir(path)

#testtrtretefsdfsdfsdfsdetterter
           
import torch
from torchvision.transforms import transforms
import torch.nn.functional as F
import numpy as np
import cv2
from config import *
from Camera import *
from camera_tools import *
from functools import partial
from display_tools import *
from scipy.spatial import distance_matrix
from lib.FpsCatcher import FpsCatcher
from database_tools import *
import globalvar
from torch.backends import cudnn
import matplotlib
import threading
import queue
import multiprocessing as mp
#mp.set_start_method('spawn')

import time


#import mmap
#from fast_histogram import histogram1d


args = parse_args()

if args.show:
    from vidgear.gears import NetGear


if len(args.catego) != 0:
    args.catego = list(map(str, args.catego.split(',')))

if len(args.euler) != 0:
    args.euler = list(map(int, args.euler.split(',')))

if args.nanocam:
    import nanocamera as nano

################################################################################
if args.yolo4:
    # yolov4
    sys.path.append(user + '/Documents/dista/yolov4')
    os.chdir(user + '/Documents/dista/yolov4')
    from demo import *
    from tool.utils import *
    from tool.torch_utils import *
    from tool.darknet2pytorch import Darknet

elif args.yolo5:
    from pathlib import Path

    path = os.path.dirname(os.path.realpath(__file__)) + '/yolov5n'
    sys.path.append(path)
    os.chdir(path)
    from models.experimental import attempt_load
    from utils.datasets import LoadImages, LoadStreams, xywh2xyxy, imgtoyolo5
    from utils.general import apply_classifier, check_img_size, check_imshow, check_requirements, check_suffix, \
        colorstr, \
        increment_path, non_max_suppression, print_args, save_one_box, scale_coords, set_logging, \
        strip_optimizer, xyxy2xywh,xywh2xyxy
    from utils.plots import Annotator, colors
    from utils.torch_utils import load_classifier, select_device, time_sync
    from utils.augmentations import  letterbox


elif args.yolo7:

    from pathlib import Path
    path = os.path.dirname(os.path.realpath(__file__)) + '/yolov7'
    sys.path.append(path)
    os.chdir(path)

    import time
    from pathlib import Path

    import cv2
    import torch
    import torch.backends.cudnn as cudnn
    from numpy import random

    from models.experimental import attempt_load
    from utils.datasets import LoadStreams, LoadImages, imgtoyolo5
    from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
        scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
    from utils.plots import plot_one_box
    from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel



else :
    path = os.path.dirname(os.path.realpath(__file__)) + '/efficientdetection'
    sys.path.append(path)
    os.chdir(path)
    from backbone import EfficientDetBackbone
    from efficientdet.utils import BBoxTransform, ClipBoxes
    from utils.utils import preprocess, preprocess_video, postprocess, STANDARD_COLORS, standard_to_bgr


if args.posenet:
    path = os.path.dirname(os.path.realpath(__file__)) + '/AlphaPose'
    sys.path.append(path)
    os.chdir(path)
    from pPose_nms import pose_nms, write_json

    from SPPE.src.main_fast_inference import *
    from dataloader_webcam import WebcamLoader, DetectionLoader, DetectionProcessor, DataWriter, crop_from_dets, Mscoco, \
        Stereocam
    from SPPE.src.utils.img import im_to_torch

    import torch
    import torch.nn as nn
    import torch.utils.data
    import torch.utils.data.distributed
    import torch.nn.functional as F
    import numpy as np
    from SPPE.src.utils.img import flip, shuffleLR
    from SPPE.src.utils.eval import getPrediction
    from SPPE.src.models.FastPose import createModel
    from pathlib import Path


    if args.yolo5:
        path = os.path.dirname(os.path.realpath(__file__)) + '/yolov5'
        sys.path.append(path)
        os.chdir(path)
    elif args.yolo7:
        path = os.path.dirname(os.path.realpath(__file__)) + '/yolov7'
        sys.path.append(path)
        os.chdir(path)

print(args.catego)

# if len(args.catego) != 0:
#     args.catego = list(map(str, args.catego.split(',')))

if len(args.camid) != 0:
    camid = list(args.camid.split(','))

angleports =[]
for i in range(len(camid)):
    angleports.append(int('60' + camid[i]))

################################################################################
class Pose_Net:

    def __init__(self, args):
        path = os.path.dirname(os.path.realpath(__file__)) + '/AlphaPose'
        sys.path.append(path)
        os.chdir(path)

        pose_dataset = Mscoco()
        self.pose_model = InferenNet_fast(4 * 1 + 1, pose_dataset)
        self.pose=None
        path = os.path.dirname(os.path.realpath(__file__)) + '/yolov5'
        sys.path.append(path)
        os.chdir(path)
    def getpose(self,cap,keep):
        boxes= torch.from_numpy(cap.detecs[keep,1:5]).float()


        # positions = cap.object_center_positions
        # if len(positions) != 0:
        #     distances = np.linalg.norm(positions, axis=1)
        #     sorteddistances = np.argsort(distances)
        #     nbdetec = len(sorteddistances)
        #     boxes= boxes[sorteddistances[0:min(nbdetec, 2)]]



        # if args.mirror:
        #    boxes[:,0] = cap.width - boxes[:,0]
        #    boxes[:,2] = cap.width - boxes[:,2]
        #inp = im_to_torch(cv2.cvtColor(cv2.resize(cap.net_image, (320, 180)), cv2.COLOR_BGR2RGB))
        inp = im_to_torch(cv2.cvtColor(cap.netimage_data, cv2.COLOR_BGR2RGB))

        #inp = im_to_torch(cap.image_to_display)

        inps = torch.zeros(boxes.shape[0], 3, 320,256)
        pt1 = torch.zeros(boxes.shape[0], 2)
        pt2 = torch.zeros(boxes.shape[0], 2)


        with torch.no_grad():
            #t=time.time()
            #print(inp.dtype, boxes.dtype, inps.dtype, pt1.dtype, pt2.dtype)
            inps, pt1, pt2 = crop_from_dets(inp, boxes, inps, pt1, pt2)
            #print('TIMMMME', np.int((time.time() - t) * 1000))
            inps_in=inps.cuda()
            hm=self.pose_model(inps_in)
            hm = hm.cpu().data
            preds_hm, preds_img, preds_scores = getPrediction(hm, pt1, pt2, 320, 256, 80, 64)
            scores = torch.from_numpy(cap.detecs[:,6])
            self.result = pose_nms(boxes, scores, preds_img, preds_scores)
            pose = np.zeros((len(self.result), 17, 3))   # last collumn is score trick to send it along key points
            pose= pose.astype(np.float32)
            for i in range(len(self.result)):
                pose[i, :, 0:2] = self.result[i]['keypoints'].numpy()
                pose[i, :, 2] = self.result[i]['kp_score'].numpy().squeeze()
            if args.mirror: pose[:, :, 0] = cap.width - pose[:, :, 0]
            cap.pose=np.copy(pose)


class Neural_Net:

    
    def __init__(self, args):

        self.compound_coef = args.netsize
        self.force_input_size = None  # set None to use default size
    
        # replace this part with your project's anchor config
        self.anchor_ratios = [(1.0, 1.0), (1.4, 0.7), (0.7, 1.4)]
        self.anchor_scales = [2 ** 0, 2 ** (1.0 / 3.0), 2 ** (2.0 / 3.0)]
    
        self.use_cuda = True if not args.nocuda else False
        self.use_float16 = args.use16
        cudnn.fastest = True
        cudnn.benchmark = True
    
        self.obj_list = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
                    'fire hydrant', '', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
                    'cow', 'elephant', 'bear', 'zebra', 'giraffe', '', 'backpack', 'umbrella', '', '', 'handbag', 'tie',
                    'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
                    'skateboard', 'surfboard', 'tennis racket', 'bottle', '', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
                    'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut',
                    'cake', 'chair', 'couch', 'potted plant', 'bed', '', 'table', '', '', 'toilet', '', 'tv',
                    'laptop', 'mouse', 'remote', 'keyboard', 'cellphone', 'microwave', 'oven', 'toaster', 'sink',
                    'refrigerator', '', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
                    'toothbrush']
    
        self.obj_thick_dict = {'person': 0.5, 'bicycle': 0.3, 'car': 1, 'motorcycle': 0.3, 'airplane': 5, 'bus': 3, 'train': 3,
                          'truck': 3, 'boat': 3, 'traffic light': 0.2,
                          'fire hydrant': 0.2, '_': 0.02, 'stop sign': 0.1, 'parking meter': 0.1, 'bench': 0.2, 'bird': 0.1,
                          'cat': 0.2, 'dog': 0.2, 'horse': 0.4, 'sheep': 0.4,
                          'cow': 0.4, 'elephant': 1, 'bear': 0.5, 'zebra': 0.5, 'giraffe': 0.5, '_': 0.02, 'backpack': 0.3,
                          'umbrella': 0.1, '_': 0.02, '_': 0.02, 'handbag': 0.2, 'tie': 0.02,
                          'suitcase': 0.1, 'frisbee': 0.02, 'skis': 0.1, 'snowboard': 0.1, 'sports ball': 0.02, 'kite': 0.1,
                          'baseball bat': 0.02, 'baseball glove': 0.1,
                          'skateboard': 0.1, 'surfboard': 0.1, 'tennis racket': 0.02, 'bottle': 0.1, '_': 0.02,
                          'wine glass': 0.02, 'cup': 0.02, 'fork': 0.02, 'knife': 0.02, 'spoon': 0.02,
                          'bowl': 0.1, 'banana': 0.02, 'apple': 0.02, 'sandwich': 0.02, 'orange': 0.02, 'broccoli': 0.02,
                          'carrot': 0.02, 'hot dog': 0.02, 'pizza': 0.02, 'donut': 0.02,
                          'cake': 0.02, 'chair': 0.5, 'couch': 0.2, 'potted plant': 0.1, 'bed': 0.5, '_': 0.02,
                          'table': 0.3, '_': 0.02, '_': 0.02, 'toilet': 0.2, '_': 0.02, 'tv': 0.01,
                          'laptop': 0.1, 'mouse': 0.05, 'remote': 0.02, 'keyboard': 0.02, 'cellphone': 0.05,
                          'microwave': 0.2, 'oven': 0.3, 'toaster': 0.1, 'sink': 0.2,
                          'refrigerator': 0.3, '_': 0.02, 'book': 0.02, 'clock': 0.02, 'vase': 0.02, 'scissors': 0.02,
                          'teddy bear': 0.1, 'hair drier': 0.1,
                          'toothbrush': 0.02}

        delete = [11, 25, 28, 29, 44, 65, 67, 68, 70, 82]
        sorted_indecies_to_delete = sorted(delete, reverse=True)
        if args.yolo5 or args.yolo7 or args.yolo4:
            for index in sorted_indecies_to_delete:
                del self.obj_list[index]

        if args.yolo4:
            self.input_sizes = [288, 640, 768, 896, 1024, 1280, 1280, 1536,1920] #512 is the netsize 0 for efficent and yolov5
        else:
            self.input_sizes = [512, 640, 768, 896, 1024, 1280, 1280, 1536,1920] #512 is the netsize 0 for efficent and yolov5

        self.input_size = self.input_sizes[self.compound_coef] if self.force_input_size is None else self.force_input_size
        self.netshape = None


        self.detection_threshold=args.detection_threshold
        self.nonmax_threshold=args.nonmax_threshold
        self.imsplit = args.imsplit

        if args.yolo4:
            # yolo4
            cfgfile = user + '/Documents/dista/yolov4/cfg/yolov4-tiny.cfg'
            weightfile = user + '/Documents/dista/yolov4/yolov4-tiny.weights'
            self.model = Darknet(cfgfile)
            self.model.load_weights(weightfile)
            self.model.cuda()
            self.model.eval()
            if self.use_float16:
                self.model = self.model.half()

        elif args.yolo5:
            self.device = select_device('0')
            self.half = self.use_float16
            #self.half = self.device.type == 'cpu'  # half precision only supported on CUDA
            weights= 'crowdhuman_yolov5m.pt' #'yolov5n.pt' #'best.pt'#'crowdhuman_yolov5m.pt'

            w = str(weights[0] if isinstance(weights, list) else weights)
            classify, suffix, suffixes = False, Path(w).suffix.lower(), ['.pt', '.onnx', '.tflite', '.pb', '']
            check_suffix(w, suffixes)  # check weights have acceptable suffix
            pt, onnx, tflite, pb, saved_model = (suffix == x for x in suffixes)  # backend booleans
            self.stride, names = 64, [f'class{i}' for i in range(1000)]  # assign defaults
            #if pt:
            self.model = torch.jit.load(w) if 'torchscript' in w else attempt_load(weights, map_location=self.device)
            self.stride = int(self.model.stride.max())  # model stride
            names = self.model.module.names if hasattr(self.model, 'module') else self.model.names  # get class names

            if self.half:
                self.model.half()  # to FP16
            self.imgsz = [check_img_size(self.input_size, s=self.stride)]  # check image size
            self.imgsz *= 2 if len(self.imgsz) == 1 else 1
            self.model(torch.zeros(1, 3, *self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once

        elif args.yolo7 :
            self.half = self.use_float16

            weights= 'yolov7-w6.pt' #'yolov7x.pt'(640) #'yolov7-w6.pt (1280) #'yolov7-e6.pt' #'yolov7-D6.pt'#
            self.device = select_device('0')

            self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
            self.stride = int(self.model.stride.max())  # model stride
            #imgsz = check_img_size(imgsz, s=stride)  # check img_size
            #if trace:
            #    model = TracedModel(model, device, opt.img_size)

            if self.half:
                self.model.half()  # to FP16

        else:

            self.model = EfficientDetBackbone(compound_coef=self.compound_coef, num_classes=len(self.obj_list),
                                              ratios=self.anchor_ratios, scales=self.anchor_scales)
            self.model.load_state_dict(torch.load(
                f'weights/efficientdet-d{self.compound_coef}.pth'))  # _17_144252  _first_test_person_adam_15ep_augmented
            self.model.requires_grad_(False)
            self.model.eval()
            if self.use_cuda:
                self.model = self.model.cuda()
            if self.use_float16:
                self.model = self.model.half()


        
        self.obj_cat_id=[]
        for i in range(len(args.catego)):
            self.obj_cat_id.append(self.obj_list.index(args.catego[i]))


        class SquarePad:
            
            def __init__(self,netsize):
                 self.netsize = netsize

            def __call__(self, image):
                c, h, w = image.size()
                padding = (0, 0, 0, self.netsize - h * self.netsize // w )
                return F.pad(image, padding, 'constant', 0)

        class resize():

            if args.yolo4:
                def __init__(self, width, height):
                    self.width = width
                    self.height = height

                def __call__(self, image):
                    return F.interpolate(image.unsqueeze(0), size=[self.height, self.width]).squeeze()

            elif args.yolo5 or args.yolo7:
                def __init__(self, netsize):
                    self.netsize = netsize
                def __call__(self, image):
                    ratio = self.netsize / max(image.shape[1],image.shape[2])
                    return F.interpolate(image.unsqueeze(0),size=[int(image.shape[2] * ratio), int(image.shape[1] * ratio)]).squeeze()

            else:
                def __init__(self, netsize):
                    self.netsize = netsize

                def __call__(self, image):
                    return F.interpolate(image.unsqueeze(0), size=[image.shape[1] * self.netsize // image.shape[2],self.netsize]).squeeze()


        if args.yolo4:
            self.transform_compose = transforms.Compose([
                resize(self.model.width, self.model.height)])
        elif args.yolo5 or args.yolo7 :
            self.transform_compose = transforms.Compose([
                resize(self.input_size),
                SquarePad(self.input_size)])
        else:
            self.transform_compose = transforms.Compose([
                resize(self.input_size),
                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
                SquarePad(self.input_size)])

        if self.use_cuda:
            self.totensor = lambda img: torch.from_numpy(img).cuda().permute(2, 0, 1).to(dtype=torch.float) / 255.
        else:
            self.totensor = lambda img: torch.from_numpy(img).permute(2, 0, 1).to(dtype=torch.float) / 255.

    def toyolo5(self,image):
        image = letterbox(image, self.input_size, stride=self.stride, auto=True)[0]
        # Convert
        image = image.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        image = np.ascontiguousarray(image)
        image = torch.from_numpy(image).to(self.device)
        image = image.half() if self.half else image.float()  # uint8 to fp16/32
        image = image / 255.0  # 0 - 255 to 0.0 - 1.0
        #if len(image.shape) == 3:
        #    image = image[None]  # expand for batch dim
        #image=image.permute(2, 0, 1)
        return  image

    def transform(self, images):
        if not args.yolo5 and not args.yolo7:
            transformed_imgs = [self.transform_compose(self.totensor(img[:, :, [2, 1, 0]])) for img in images]
        else:
            #transformed_imgs = [self.toyolo5(img) for img in images]
            # imgtoyolo5 is from previous version : testing if faster then my
            transformed_imgs = [imgtoyolo5(img, self.input_size, stride=self.stride) for img in images]
            transformed_imgs = [self.totensor(img[:, :, [2, 1, 0]]) for img in transformed_imgs]
            #transformed_imgs = [img[:, :, [2, 1, 0]] for img in transformed_imgs]

            self.netshape = transformed_imgs[0].shape[1:]
        return transformed_imgs

    def get_detection(self, left_frame_list):

        #split images in quadrants : put all splits into a single batch
        new_left_frame_list = splitimage(left_frame_list[0], args.imsplit)
        for i in range(1,len(left_frame_list)):
            new_left_frame_list = [*new_left_frame_list,*splitimage(left_frame_list[i], args.imsplit)]
        imh, imw, c = new_left_frame_list[0].shape

        if globalvar.detectionFps is None:
            globalvar.detectionFps = FpsCatcher(autoStart=False)
        if globalvar.totalNetFps is None:
            globalvar.totalNetFps = FpsCatcher(autoStart=False)
            
            
    
        t=time.time()
        framed_imgs=self.transform(new_left_frame_list)
        globalvar.prepro = np.int((time.time()-t)*1000)
        


        if self.use_cuda:
            #x = torch.stack([fi for fi in framed_imgs], 0)
            x = torch.stack(framed_imgs, 0)
        else:
            x = torch.stack([torch.from_numpy(fi) for fi in framed_imgs], 0)
                        
        x = x.to(torch.float32 if not self.use_float16 else torch.float16)
        with torch.no_grad():

            now = FpsCatcher.currentMilliTime()
            t=time.time()

            if args.yolo4 :
                imh, imw, c = new_left_frame_list[0].shape
                outputs = do_detect(args,imh, imw, self.model, x, self.detection_threshold, self.nonmax_threshold, use_cuda=True)
                globalvar.nettime = np.int((time.time() - t) * 1000)
                current = FpsCatcher.currentMilliTime()
                globalvar.detectionFps.compute(current - now)
                t = time.time()
                globalvar.post = np.int((time.time() - t) * 1000)

                outputs = [np.asarray(out) for out in outputs]
                for i in range(len(outputs)):
                   if len(outputs[i]) !=0:
                    outputs[i] = np.delete(outputs[i],4,1) # extra confidence column for some reason

            elif args.yolo5:
                #self.model(torch.zeros(1, 3, *self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once
                #x = x.half() if self.half else x.float()  # uint8 to fp16/32
                outputs = self.model(x, augment=False, visualize=False)[0]
                globalvar.nettime = np.int((time.time() - t) * 1000)
                current = FpsCatcher.currentMilliTime()
                globalvar.detectionFps.compute(current - now)
                #this was done twice
                #outputs[:, :4] = scale_coords(x.shape[2:], outputs[:, :4], new_left_frame_list[0].shape).round()
                #outputs = xywh2xyxy(outputs)



                tt = time.time()
                outputs = non_max_suppression(outputs, self.detection_threshold,
                                                 self.nonmax_threshold, classes=self.obj_cat_id, agnostic=False)
                globalvar.post = np.int((time.time() - tt) * 1000)
            elif args.yolo7:

                outputs = self.model(x, augment=False)[0]
                globalvar.nettime = np.int((time.time() - t) * 1000)
                current = FpsCatcher.currentMilliTime()
                globalvar.detectionFps.compute(current - now)
                #outputs[:, :4] = scale_coords(x.shape[2:], outputs[:, :4], new_left_frame_list[0].shape).round()
                #outputs = xywh2xyxy(outputs)

                tt = time.time()
                outputs = non_max_suppression(outputs, self.detection_threshold,
                                              self.nonmax_threshold, classes=self.obj_cat_id, agnostic=False)
                globalvar.post = np.int((time.time() - tt) * 1000)
            else:
                features, regression, classification, anchors = self.model(x)
                globalvar.nettime = np.int((time.time()-t)*1000)
                current = FpsCatcher.currentMilliTime()
                globalvar.detectionFps.compute(current - now)



                regressBoxes = BBoxTransform()
                clipBoxes = ClipBoxes()

                outputs = postprocess(self, args, x, imw, imh,
                                      anchors, regression, classification,
                                      regressBoxes, clipBoxes,
                                      )

                for i in range(len(outputs)):
                    detecs = np.zeros((outputs[i]['rois'].shape[0], 6))
                    if len(outputs[i]['rois'])!=0:
                        detecs[:, 0:4] = outputs[i]['rois']
                        detecs[:, 4] = outputs[i]['scores']
                        detecs[:, 5] = outputs[i]['class_ids']
                    outputs[i] = detecs
        return outputs


################################################################################


def format_detection(outputs):

    detecs = np.zeros((outputs.shape[0], 11))
    detecs[:, 1:5] = outputs[:, 0:4] # box
    detecs[:, 6] = outputs[:, 4] # confidence
    detecs[:, 7] = outputs[:, 5] # class id

    return detecs

################################################################################
# def format_detection(outputs):
#     #                JUST TO MAKE DETECT OUTPUT FORMAT SAME AS OTHER MODELS (AS YOLO) SO THE REST OF THE CODE DOES NOT CHANGE.
#     detecs = np.zeros((outputs['rois'].shape[0], 8))
#     detecs[:, 7] = outputs['class_ids']
#     detecs[:, 1:5] = outputs['rois']
#     detecs[:, 6] = outputs['scores']
#
#     return detecs

################################################################################

def scale_2d_bounding_box(detecs, input_size, netshape, w, h):
    # SCALE BOUDING BOX TO ORIGINAL IMAGE (CAMERA) SIZE
    netsize = np.asarray([input_size, input_size])
    widht=np.copy(w)#/args.rectifydown
    height=np.copy(h)#/args.rectifydown
    imsize = np.asarray([height, widht])
    if args.yolo5 or args.yolo7:
        ##Rescale boxes from netshape to original image size
        scale_factors = min(netshape[0] / height, netshape[1] / widht)  # gain  = old / new
        pad = (netshape[1] - widht * scale_factors) / 2, (netshape[0] - height * scale_factors) / 2  # wh padding
        detecs[:, [1, 3]] -= pad[0]  # x padding
        detecs[:, [2, 4]] -= pad[1]  # y padding
        detecs[:, :5] /= scale_factors
    #else :
    #    return detecs
        # #scale_factors = np.max(imsize / netsize, axis=0)
        # scale_factors = 1
        # #    scale_factors = imsize / netsize
        # detecs[:, 1] = detecs[:, 1] * scale_factors
        # detecs[:, 3] = detecs[:, 3] * scale_factors
        # detecs[:, 2] = detecs[:, 2] * scale_factors
        # detecs[:, 4] = detecs[:, 4] * scale_factors

    ## MAKE SURE IT DOEST NOT GO OVER IMAGE LIMIT
    detecs[:, 1] = np.min((detecs[:, 1], np.repeat(imsize[1], detecs.shape[0])), axis=0)
    detecs[:, 3] = np.min((detecs[:, 3], np.repeat(imsize[1], detecs.shape[0])), axis=0)
    detecs[:, 2] = np.min((detecs[:, 2], np.repeat(imsize[0], detecs.shape[0])), axis=0)
    detecs[:, 4] = np.min((detecs[:, 4], np.repeat(imsize[0], detecs.shape[0])), axis=0)

    return detecs
################################################################################
# def scale_2d_bounding_box(detecs, input_size, w, h):
#     #   SCALE BOUDING BOX TO ORIGINAL IMAGE (CAMERA) SIZE
#
#     netsize = np.asarray([input_size, input_size])
#     imsize = np.asarray([h, w])
#
#     wstart = int((w-input_size) /2)
#     scale_factors = np.max(imsize / netsize, axis=0)
# #    scale_factors = imsize / netsize
#
#     detecs[:, 1] = detecs[:, 1] * scale_factors
#     detecs[:, 3] = detecs[:, 3] * scale_factors
#     detecs[:, 2] = detecs[:, 2] * scale_factors
#     detecs[:, 4] = detecs[:, 4] * scale_factors
#
#
#     #             MAKE SURE IT DOEST NOT GO OVER IMAGE LIMIT
#     detecs[:, 1] = np.min((detecs[:, 1], np.repeat(imsize[1], detecs.shape[0])), axis=0)
#     detecs[:, 3] = np.min((detecs[:, 3], np.repeat(imsize[1], detecs.shape[0])), axis=0)
#     detecs[:, 2] = np.min((detecs[:, 2], np.repeat(imsize[0], detecs.shape[0])), axis=0)
#     detecs[:, 4] = np.min((detecs[:, 4], np.repeat(imsize[0], detecs.shape[0])), axis=0)
#
#     return detecs


################################################################################


#######################################################
def get_bounding_box_samples(image_data2, bounding_box_2d, percent, nbsamples):
    #    nbsamples=50
    a = (bounding_box_2d[2, 1] - bounding_box_2d[0, 1])
    b = (bounding_box_2d[2, 0] - bounding_box_2d[0, 0])
    rangex = int(np.floor(percent * b))
    rangey = int(np.floor(percent * a))
    x1 = int(np.floor((b - rangex) / 2))
    x2 = int(min(x1 + rangex, a - 1))
    y1 = int(np.floor((a - rangey) / 2))
    y2 = int(min(y1 + rangey, b - 1))
    horisamples = np.asarray(np.linspace(x1, x2, min(nbsamples, rangex - 1)), dtype=int)
    vertisamples = np.asarray(np.linspace(y1, y2, min(nbsamples, rangey - 1)), dtype=int)

    patch = image_data2[int(bounding_box_2d[0, 1]):int(bounding_box_2d[2, 1]),
            int(bounding_box_2d[0, 0]):int(bounding_box_2d[2, 0])]

    sample = patch[tuple(np.meshgrid(horisamples, vertisamples))]  # .transpose(1,0,2) # warning multidimen

    return sample


################################################################################
def filter_cloud_inside_object_box(cap, bounding_box_2d, obj_thick):
    cap.buggycloud = False
    cap.buggycloudcenter = False


    cloud=np.copy(cap.cloud)
    # adjust detection bounding box size to disparity map size
    step = 1#args.cloudstep
    scale_factors = 1 / step
    #downscale = args.rectifydown
    downscale = cap.rectifydown

    #nbounding_box_2d = np.copy(bounding_box_2d) * (cap.width) / args.netsizes[args.netsize]  # for resized image
    #nbounding_box_2d = np.copy(nbounding_box_2d) * scale_factors * 1 / downscale  # for downsampled cloud and rectified image

   # cloud[:,:,2] = -cloud[:,:,2]
    #cloud[:,:,1] = -cloud[:,:,1]
    # if not args.nerian:
    #     cloud=-cloud
    # else:
    #     cloud[:,0] = -cloud[:,0]  # negative X


    nbounding_box_2d = np.copy(bounding_box_2d) * scale_factors * 1 / downscale  # for downsampled cloud and rectified image
    #nbounding_box_2d[nbounding_box_2d<0]
    a,b,c = cloud.shape
    boxcloud = np.copy(cloud[int(max(nbounding_box_2d[0, 1],0)):int(min(nbounding_box_2d[2, 1],a)),
               int(max(nbounding_box_2d[0, 0],0)):int(min(nbounding_box_2d[2, 0],b))][:, :, 0:3])
    a = boxcloud.shape[0]
    b = boxcloud.shape[1]
    # GET THE 3D POINTS OF A UNIFORM SAMPLES (GRID) OVER THE 2D BOX
   # samples=[]
#    if args.view_3dbox:
    nbsamples = 50
    rangex = int(np.floor(0.99 * b))
    rangey = int(np.floor(0.99 * a))
    x1 = int(np.floor((b - rangex) / 2))
    x2=x1+rangex#    x2 = int(min(x1 + rangex, a - 1))
    y1 = int(np.floor((a - rangey) / 2))
    y2=y1+rangey #    y2 = int(min(y1 + rangey, b - 1))
    horisamples=np.asarray(np.linspace(x1,x2,min(nbsamples,rangex-1)),dtype=int) #rangex-1
    vertisamples=np.asarray(np.linspace(y1,y2,min(nbsamples,rangey-1)),dtype=int)#rangey-1
    samples = boxcloud[tuple(np.meshgrid(vertisamples, horisamples))]  # warning multidimensional indexing will require futur
    [a,b,c]=samples.shape
    centerregion = np.copy(samples[int(a/4):a-int(a/4),int(b/4):b-int(b/4)])

    samples = np.reshape(samples, (-1, 3))
    samples = samples[~np.isnan(samples).any(axis=1)]
    samples = samples[~np.isinf(samples).any(axis=1)]
    centerregion = np.reshape(centerregion, (-1, 3))
    centerregion = centerregion[~np.isnan(centerregion).any(axis=1)]
    centerregion = centerregion[~np.isinf(centerregion).any(axis=1)]

    try :
        samples[abs(samples) >= 100] = np.min(samples[:,2])
    except :
        samples[abs(samples) >= 100] = 0

    try:
        centerregion[abs(centerregion) >= 100] = np.min(centerregion[:, 2])
    except:
        centerregion[abs(centerregion) >= 100] = 0

    # # GET THE 3D POINTS OF A UNIFORM SAMPLES (GRID) OVER CENTER OF THE 2D BOX
    # nbsamples = 20
    # horisamples = np.asarray(np.linspace(b / 4, b - b / 4, min(nbsamples, int(b / 2))), dtype=int)
    # verisamples = np.asarray(np.linspace(a / 4, a - a / 4, min(nbsamples, int(a / 2))), dtype=int)
    # centerregion = np.copy(boxcloud[tuple(np.meshgrid(verisamples, horisamples))])  # warning multidimensional indexing will require futur
    # centerregion = np.reshape(centerregion, (-1, 3))
    # centerregion = centerregion[~np.isnan(centerregion).any(axis=1)]
    # centerregion = centerregion[~np.isinf(centerregion).any(axis=1)]
    #
    # try:
    #     centerregion[abs(centerregion) >= 100] = np.min(centerregion[:, 2])
    # except:
    #     centerregion[abs(centerregion) >= 100] = 0
    # # GET THE MODAL CLASS (USING DEPTH BINS) OF DEPTH IN THE CENTER REGION (SHOULD BE THE OBJECT...NOT THE BACKGROUND OR OCCLUSIONS)
    # # REMOVE POINTS TO FAR FROM THE THE MODAL DEPTH

    if len(centerregion) != 0:

        #nbbins=max(1,int(np.ceil((max(centerregion[:,2])-min(centerregion[:,2]))/obj_thick)))  # 0.02  # before 0.2
        nbbins = 250
        histo, edges = np.histogram(centerregion[:, 2], nbbins)
#        histo=histogram1d(centerregion[:, 2], range=[min(centerregion[:, 2]),max(centerregion[:, 2])+0.001], bins=nbbins)
#        edges = np.linspace(min(centerregion[:, 2]),max(centerregion[:, 2]),nbbins+1)
        binmode = np.argmax(histo)
        zmode = (edges[binmode]+edges[binmode+1])/2

        if args.view_3dbox: samples = samples[abs(samples[:, 2] - zmode) <= obj_thick, :]

        centerregion=centerregion[abs(centerregion[:,2]-zmode)<=obj_thick,:]


    if len(centerregion) == 0 : #or np.linalg.norm(np.mean(centerregion, axis=0)) <= 0.001:
        cap.buggycloudcenter = True
    if len(samples) == 0 : #or np.linalg.norm(np.mean(centerregion, axis=0)) <= 0.001:
        cap.buggycloud = True
#        print('filtered cloud is empty at cam number : ' + str(i))




    #get wrist 3d position

    # wristL = (cap.wristL   /(args.cloudstep * args.rectifydown)).astype(int)
    # wristR = (cap.wristR   /(args.cloudstep * args.rectifydown)).astype(int)
    # wristL_3d_position = [] #np.zeros((wristL.shape[0],3))
    # wristR_3d_position = [] #np.zeros((wristR.shape[0],3))

    # rad = 20
    # [a, b, c] = cloud.shape
    # for i in range(len(wristL)):
    #
    #
    #     wristcloudL = cloud[max(0, wristL[i][1] - rad):min(wristL[i][1] + rad, a),max(0, wristL[i][0] - rad):min(wristL[i][0] + rad, b)]
    #     wristcloudR = cloud[max(0, wristR[i][1] - rad):min(wristR[i][1] + rad, a),max(0, wristR[i][0] - rad):min(wristR[i][0] + rad, b)]
    #     wristcloudL = np.reshape(wristcloudL, (-1, 3))
    #     wristcloudR = np.reshape(wristcloudR, (-1, 3))
    #     wristcloudL = wristcloudL[~np.isnan(wristcloudL).any(axis=1)]
    #     wristcloudR = wristcloudR[~np.isnan(wristcloudR).any(axis=1)]
    #     wristcloudL = wristcloudL[~np.isinf(wristcloudL).any(axis=1)]
    #     wristcloudR = wristcloudR[~np.isinf(wristcloudR).any(axis=1)]
    #
    #     nbbins = 250
    #
    #     histoL, edgesL = np.histogram(wristcloudL[:, 2], nbbins)
    #     binmodeL = np.argmax(histoL)
    #     zmodeL = (edges[binmodeL] + edges[binmodeL + 1]) / 2
    #     wristcloudL=wristcloudL[abs(wristcloudL[:,2]-zmodeL)<=0.2,:]
    #     #if len(wristcloudL)!=0:
    #     wristLposition = np.mean(wristcloudL, axis=0)
    #     wristL_3d_position.append(wristLposition)
    #
    #
    #     histoR, edgesR = np.histogram(wristcloudR[:, 2], nbbins)
    #     binmodeR = np.argmax(histoR)
    #     zmodeR = (edges[binmodeR] + edges[binmodeR + 1]) / 2
    #     wristcloudR=wristcloudR[abs(wristcloudR[:,2]-zmodeR)<=0.2,:]
    #     #if len(wristcloudR)!=0 :
    #     wristRposition = np.mean(wristcloudR, axis=0)
    #     wristR_3d_position.append(wristRposition)
    #
    # cap.wristL_3d_position = wristL_3d_position
    # cap.wristR_3d_position = wristR_3d_position

    return samples, centerregion


################################################################################


################################################################################
def get_3d_box(samples, position):

    rotsamples=np.copy(samples)
    if len(args.euler)==3:
        [yaw,pitch, roll] = args.euler
    else:
        [yaw,pitch, roll] = [0,0,0]

    rotMat = euler_to_rotMat(0,0,roll*np.pi/180)

    if len(args.euler)==3:
        for j in range(len(rotsamples)):
            rotsamples[j]=np.matmul(rotMat,rotsamples[j])

    heigth = abs(max(rotsamples[:, 1]) - min(rotsamples[:, 1]))
    width = abs(max(rotsamples[:, 0]) - min(rotsamples[:, 0]))
    depth = abs(max(rotsamples[:, 2]) - min(rotsamples[:, 2]))
    dimensions = np.array([width, heigth, depth])

    #print(dimensions)
    #  CREATE 3D BOX

    # closestdepth = min(abs(samples[:, 2]))
    # farestdepth = max(abs(samples[:, 2]))
    #
    # lowestheight= min(samples[:,1])
    # highesttheight= max(samples[:,1])
    #
    # leftmost = min(samples[:,0])
    # rightmost = max(samples[:,0])
    #
    # if not args.vflip:
    #     A=[-(leftmost+rightmost)/2, -highesttheight,closestdepth]
    #     B=[-leftmost, -highesttheight,farestdepth]
    #     D=[-rightmost, -highesttheight,farestdepth]
    #     C= np.asarray(B) +(np.asarray(D)-np.asarray(A))
    # else:
    #     A=[(leftmost+rightmost)/2, highesttheight,closestdepth]
    #     B=[leftmost, highesttheight,farestdepth]
    #     D=[rightmost, highesttheight,farestdepth]
    #     C= np.asarray(B) +(np.asarray(D)-np.asarray(A))
    #
    # E = np.copy(A)
    # F = np.copy(B)
    # G = np.copy(C)
    # H = np.copy(D)
    # if not args.vflip:
    #     E[1]+=heigth
    #     F[1]+=heigth
    #     G[1]+=heigth
    #     H[1]+=heigth
    # else:
    #     E[1]-=heigth
    #     F[1]-=heigth
    #     G[1]-=heigth
    #     H[1]-=heigth
    # # all_lowestheights_bool = samples[:,1]==lowestheight
    # # all_closestdepths_bool = samples[:,2]==closestdepth
    # # all_leftmosts_bool = samples[:,0]==leftmost
    # # all_rightmosts_bool = samples[:,0]==rightmost
    # # all_lowestheights_points=samples[all_lowestheights_bool,:]
    # # all_lowestheights_leftmost_points=all_lowestheights_points[all_lowestheights_points[:,0]==min(all_lowestheights_points[:,0]),:]
    # # lowestheights_leftmost_point=all_lowestheights_leftmost_points[0]
    # # all_lowestheights_rightmost_points=all_lowestheights_points[all_lowestheights_points[:,0]==max(all_lowestheights_points[:,0]),:]
    # # lowestheights_rightmost_point=all_lowestheights_rightmost_points[0]
    # # all_lowestheights_closest_points=all_lowestheights_points[abs(all_lowestheights_points[:,2])==min(abs(all_lowestheights_points[:,2])),:]
    # # lowestheights_closest_point=all_lowestheights_closest_points[0]

    wradius = width / 2
    hradius = heigth / 2
    draduis = depth / 2

    A = [(- wradius), ( + hradius) , ( - draduis)]
    B = [(- wradius), ( + hradius), ( + draduis)]
    C = [( + wradius), ( + hradius), ( + draduis)]
    D = [( + wradius), ( + hradius) , ( - draduis)]

    E = [( - wradius) , ( - hradius) , ( - draduis)]
    F = [( - wradius), ( - hradius), ( + draduis)]
    G = [( + wradius), ( - hradius), ( + draduis)]
    H = [( + wradius) , ( - hradius) , ( - draduis)]

    centeredbounding_box = np.asarray([A, B, C, D, E, F, G, H])
    bounding_box = np.asarray([A, B, C, D, E, F, G, H])
    for j in range(len(centeredbounding_box)):
        bounding_box[j]=np.matmul(rotMat,centeredbounding_box[j]) + position
        #bounding_box[j]= centeredbounding_box[j]+ position


    # A = [(position[0] - wradius), (position[1] + hradius) , (position[2] - draduis)]
    # B = [(position[0] - wradius), (position[1] + hradius), (position[2] + draduis)]
    # C = [(position[0] + wradius), (position[1] + hradius), (position[2] + draduis)]
    # D = [(position[0] + wradius), (position[1] + hradius) , (position[2] - draduis)]
    #
    # E = [(position[0] - wradius) , (position[1] - hradius) , (position[2] - draduis)]
    # F = [(position[0] - wradius), (position[1] - hradius), (position[2] + draduis)]
    # G = [(position[0] + wradius), (position[1] - hradius), (position[2] + draduis)]
    # H = [(position[0] + wradius) , (position[1] - hradius) , (position[2] - draduis)]


    #bounding_box = np.asarray([A, B, C, D, E, F, G, H])
    return dimensions, bounding_box


################################################################################


def get_desired_categories(detecs, obj_cat_id):
    # GET ONLY DESIRED CATEGORIES
    objects_indices = [0]
    for i in range(0, len(args.catego)):
        objects_indices = np.concatenate((objects_indices, np.where(detecs[:, 7] == obj_cat_id[i])[0]))

    objects_indices = objects_indices[1:]

    detecs = detecs[objects_indices]

    return detecs

def get_2d_centers(args,cap,object_2d_boxes):
    
    imgpts=np.zeros((len(object_2d_boxes),2)).astype(int)

    
    for j in range(len(object_2d_boxes)):
        

        bounding_box_2d=object_2d_boxes[j]
        
        upperleftcorner=bounding_box_2d[0] 
        lowerrightcorner= bounding_box_2d[2]    
                 
        u=int(np.round((upperleftcorner[0]+lowerrightcorner[0])/2))
        v=int(np.round((upperleftcorner[1]+lowerrightcorner[1])/2))
        
        if args.mirror==True:
            imgpts[j,0]=int(cap.width-u)
        else:
            imgpts[j,0]=int(u)
        imgpts[j,1]=int(v)
         
        
    return np.array(imgpts)
################################################################################       

def get_2d_boxes(args,cap,input_size,netshape, max_number_objects):
    [h,w,c]=cap.image_to_display.shape
    #w = cap.width
    #h = cap.height
    # RESSCALE 2D BOX COORDINATES TO MATCH CAMERA RESOLUTION
    cap.detecs = scale_2d_bounding_box(cap.detecs, input_size,netshape, w, h)  # image_data
#    object_2d_boxes = np.zeros((len(cap.detecs),4,2))
    object_2d_boxes = []
    cap.label=[]
    cap.detectionconfidence=[]

    
    ####################################################################
    # GET ALL 2D BOXES,
   
    for k in range(0, min(len(cap.detecs), max_number_objects)):  # len(id_colors)
#        trackingconfidence=0
        # CREATE 2D BOX  FOR CURRENT OBJECT
        oneobject = cap.detecs[k]
        bounding_box_2d = np.zeros((4, 2))
        bounding_box_2d[0, :] = [oneobject[1], oneobject[2]]  # upper left corner
        bounding_box_2d[1, :] = [oneobject[3], oneobject[2]]  # upper right corner
        bounding_box_2d[2, :] = [oneobject[3], oneobject[4]]  # bottom right corner
        bounding_box_2d[3, :] = [oneobject[1], oneobject[4]]  # bottom left corner
    
        if cap.detecs[k,6]>args.detection_threshold :
            object_2d_boxes.append(bounding_box_2d)
            cap.label.append(int(cap.detecs[k, 7]))
            cap.detectionconfidence.append(cap.detecs[k,6])
        
#
    cap.object_2d_boxes=np.asarray(object_2d_boxes)        
    cap.object_2d_centers=get_2d_centers(args,cap,cap.object_2d_boxes)
    

##
def get_3d_positions_and_dimensions(args,cap, netout, neural_net):


    #compute2dboxes(args, cap, netout, neural_net)


    for i in range(len(cap)):


        # RESSCALE 2D BOX COORDINATES TO MATCH CAMERA RESOLUTION
        #cloud=cap[i].cloud
        # INITIALIZE LISTS CONTAINING ALL DETECTIONS                     
        object_center_positions = []
        object_3d_boxes = []
        object_dimensions = []
        object_cloud = []
    
        w = cap[i].width
        h = cap[i].height
    
        ####################################################################
        #  FILTER THE POINT CLOUD INSIDE 2D BOXES AND GET 3D DIMENSIONS
    
    
        # LOOP OVER ALL DETECTIONS AND FILTER POINT CLOUD INSIDE 2D BOX
        for k in range(0, min(len(cap[i].object_2d_boxes), args.max_number_objects)):  # len(id_colors)
    
            # GET CLASS LABEL FOR CURRENT OBJECT
            label = cap[i].label[k] #int(cap[i].detecs[k, 7])
    
            if not args.justdetec:

                # TO PREVENT "BUGGY" POINT CLOUD  : TOO SMALL BOXES :
                boxwitdth = abs(cap[i].object_2d_boxes[k][2,0] - cap[i].object_2d_boxes[k][0,0])
                boxheight = abs(cap[i].object_2d_boxes[k][2,1] - cap[i].object_2d_boxes[k][0,1])
                if boxwitdth < 0.02 * w or boxheight < 0.02 * h:  # 0.02
    #                cap[i].buggycloud = True
                    position=[np.nan, np.nan, np.nan]
                    dimensions=[np.nan, np.nan, np.nan]
                    bounding_box=[np.nan]*8
                    object_center_positions.append(position)
                    object_dimensions.append(dimensions)
                    object_3d_boxes.append(bounding_box)
    #                print('2d boxe is too small for stereo')

                # FILTER POINTCLOUD INSIDE 2D BOX
                else:    
                    name = neural_net.obj_list[label]
#                    t=time.time()
                    samples, centerregion = filter_cloud_inside_object_box(cap[i], cap[i].object_2d_boxes[k], neural_net.obj_thick_dict[name])
                    object_cloud.append(samples)
#                    getfiltercloud = time.time()-t
#                    print(f'GET FILTERCLOUD : {np.int(getfiltercloud*1000)}')


                    if cap[i].buggycloud:
                        print('empty box')
                        dimensions=np.array([np.nan, np.nan, np.nan])
                        bounding_box=[np.nan]*8
                        position = np.array([np.nan, np.nan, np.nan])
                    else:

                        if cap[i].buggycloudcenter:
                            print('empty center')
                            position = np.mean(samples, axis=0)
                            offset =  0#neural_net.obj_thick_dict[name] # add 5 cm because point cloud ore only for visible/front points
                            position = np.asarray([position[0], position[1], position[2] - offset])
                            #position=np.array([np.nan, np.nan, np.nan])
                        else:
                            # GET THE AVERAGE POSITION IN THE CENTER OF 3D CLOUD
                            position = np.mean(centerregion, axis=0)
                            offset =  0#neural_net.obj_thick_dict[name]/2.0 # add 5 cm because point cloud ore only for visible/front points
                            position = np.asarray([position[0], position[1], position[2] - offset])
                            # GET 3D DIMENSION OF 3D BOX AND CREATE 3D BOX
                        if args.view_3dbox : dimensions, bounding_box = get_3d_box(samples, position)


                            
                    #  STORE CENTER POSTION 
                    object_center_positions.append(position)
                    if args.view_3dbox : object_dimensions.append(dimensions)
                    if args.view_3dbox : object_3d_boxes.append(bounding_box)

        cap[i].object_center_positions=object_center_positions
        cap[i].object_3d_boxes=object_3d_boxes
        cap[i].object_dimensions=object_dimensions
        cap[i].object_cloud=object_cloud
        compute_distance_matrix(cap[i])
        
#
#                 
def compute_distance_matrix(cap):
    if len(cap.object_center_positions)!=0:
         cap.distmat=distance_matrix(np.asarray(cap.object_center_positions),np.asarray(cap.object_center_positions))
    else:
        cap.distmat = []
     


################################################################################################


def compute2dboxes(args,cap, netout,neural_net):

    for i in range(len(netout)):
        
        # GET ONLY DESIRED CATEGORIES, GO BACK TO BEGINING OF LOOP IF NOTHING IS DETECTED
        cap[i].detecs = []
        cap[i].object_2d_boxes = []
        cap[i].object_2d_centers = []
        outlength = len(netout[i])
        if outlength != 0:
            detecs = format_detection(netout[i])
            cap[i].detecs = get_desired_categories(detecs, neural_net.obj_cat_id)

            if len(cap[i].detecs) > 0:
                get_2d_boxes(args, cap[i], neural_net.input_size,neural_net.netshape, args.max_number_objects)
            else:
                cap[i].object_2d_boxes = []
                cap[i].object_2d_centers = []



def displayloop(args,cap):
    
    ct=0
    while True:
                  
            ####################################################################
            # ADJUST AND DISPLAY IMAGES FOR ALL CAMERAS                                                 
            if args.adjust and ct==0:
                for i in range(len(cap)):
                    opencv_adjust(cap[i])
                    
            for i in range(len(cap)):
                cap[i].image_data, cap[i].right_image_data=cap[i].get_rectified_left_right()
                cap[i].image_to_display=np.copy(cap[i].image_data)
            display_and_record(args,cap)
            ####################################################################            
            # ESCAPE LOOP AND INITIALIZE WINDOWS AGAIN
            ct=ct+1  
            k = cv2.waitKey(1)
            if k == 27:
                set_windows(args)
                break
#########################################################################################################

def splitimage(img,splits):
    overlap = args.overlap
    hstart = np.arange(0 , img.shape[1] , int(img.shape[1]/splits)) - overlap
    hstart[0] = 0
    vstart = np.arange(0 , img.shape[0] , int(img.shape[0]/splits)) - overlap
    vstart[0] = 0
    hend = hstart + int(img.shape[1]/splits) + overlap
    vend = vstart + int(img.shape[0]/splits) + overlap
    imlist=[]
    for i in range(splits):
       for j in range(splits):
           imlist.append(img[vstart[i]:vend[i],hstart[j]:hend[j],:])

    return imlist


def detectionloop(args,cap,neural_net,database):

    if args.posenet :
        posenet = Pose_Net(args)
        posenet.pose_model.cuda()
        posenet.pose_model.eval()

    frameCounter=0

#    if args.thread:
    q_thread_imagesstereo=[]
    q_thread_imagesnet=queue.Queue(maxsize=2)
    q_thread_net=queue.Queue(maxsize=2)
    q_thread_cloud=[]


    if args.thread:
        barrier1 = threading.Barrier(1   + len(cap)  if not args.justdetec else 1 + 1 , timeout = 5 )
        barrier2 = threading.Barrier(1   + len(cap)  if not args.justdetec else 1 + 1 , timeout = 5 )

    else :
        detectionlock = threading.Barrier(1, timeout = 5 )
        
    ################################################  


    def fetch_images():
        netimages=[]
        for i in range(len(cap)):

            if args.justdetec and not args.netrectify:
                cap[i].netimage_data = cap[i].get_left()
            elif args.justdetec:
                cap[i].netimage_data = cap[i].net_get_rectified_left()

            else:
                leftimage,rightimage=cap[i].get_rectified_left_right()
                cap[i].image_data , cap[i].right_image_data = leftimage,rightimage
                cap[i].disparity_to_display = np.zeros_like(cap[i].image_data)

                if args.netrectify:
                    cap[i].netimage_data = cap[i].net_rectified_left()

                if q_thread_imagesstereo[i].full():
                    q_thread_imagesstereo[i].get()
                q_thread_imagesstereo[i].put(np.copy([cap[i].image_data,cap[i].right_image_data]))

            cap[i].image_to_display = cv2.flip(np.copy(cap[i].netimage_data.astype(np.uint8)),1) if args.mirror else np.copy(cap[i].netimage_data.astype(np.uint8))

            #netimages.append(np.copy(cap[i].netimage_data[..., ::-1]))  #to rgb
            netimages.append(np.copy(cap[i].netimage_data))  #

        q_thread_imagesnet.put(netimages)


    def imageloop():
        while not globalvar.stopthread_images:
            fetch_images()
            #barrier1.wait()
                
    ################################################  
            
            
    def fetch_stereo(cap, q_thread_imagesstereo, q_thread_cloud,count):
        
        image_data, right_image_data=q_thread_imagesstereo.get(block=True,timeout=15)
        cloud, disparity_to_display = cap.get_pointcloud(image_data, right_image_data)

        previousclouds[count % args.timeavg], previousdisparities[count % args.timeavg] = cap.get_pointcloud(image_data, right_image_data)
        cloud = np.mean(previousclouds, axis=0)
        disparity_to_display = np.mean(previousdisparities, axis=0)


        q_thread_cloud.put([cloud, disparity_to_display])


    def stereoloop(cap, q_thread_imagesstereo, q_thread_cloud,count):
        while not globalvar.stopthread_stereo:
            #barrier1.wait()
            t  = time.time()
            fetch_stereo(cap, q_thread_imagesstereo, q_thread_cloud,count)
            globalvar.stereotime = np.int((time.time()-t)*1000)
            #barrier2.wait()
        

    ################################################

    def fetch_net(q_thread_imagesnet, q_thread_net, neural_net):
    
        netimages=q_thread_imagesnet.get(block=True,timeout=15)
        netout = neural_net.get_detection(netimages)
        q_thread_net.put(netout)


    def netloop(q_thread_imagesnet, q_thread_net, neural_net):
        while not globalvar.stopthread_net:
            
            #barrier1.wait()
            fetch_net(q_thread_imagesnet, q_thread_net, neural_net)
            #barrier2.wait()

        

    ################################################
    avgtotalfps = 0
    count = 0


    #define threads        
    thread_images=threading.Thread(target=imageloop)
    thread_stereo=[]        
    for j in range(len(cap)):
        q_thread_imagesstereo.append(queue.Queue(maxsize=2))
        q_thread_cloud.append(queue.Queue(maxsize=2))
        thread_stereo.append(threading.Thread(target=stereoloop,args=(cap[j], q_thread_imagesstereo[j], q_thread_cloud[j],count)))
 
    thread_net=threading.Thread(target=netloop, args=(q_thread_imagesnet,q_thread_net, neural_net))

    # #  prefetch
    # fetch_images()
    # for i in range(len(cap)):
    #     fetch_stereo(cap[i], q_thread_imagesstereo[i], q_thread_cloud[i])
    # fetch_net(q_thread_imagesnet, q_thread_net, neural_net)
    # fetch_images()


    # start threads
            
    if args.thread:          
        thread_images.start()
        for i in range(len(cap)):
            if not args.justdetec : thread_stereo[i].start()  
        thread_net.start()

#
    avgtotalfps = 0
    count = 0
    if globalvar.stereoFps is None:
        globalvar.stereoFps = FpsCatcher(autoStart=False)



    def compute_posenet(cap,keep):
        if len(cap[0].detecs) !=0:
            posenet.getpose(cap[0],keep)
        #cap[0].pose=posenet.result

    def get_hands(args, cap):

        for i in range(len(cap)):

            imgpts1 = np.zeros((len(cap[i].pose), 2)).astype(int)
            imgpts2 = np.zeros((len(cap[i].pose), 2)).astype(int)

            for j in range(len(cap[i].pose)):
                wristL = np.copy(cap[i].pose[j][9, 0:2].astype(int))
                wristR = np.copy(cap[i].pose[j][10, 0:2].astype(int))
                imgpts1[j] = wristL
                imgpts2[j] = wristR

            cap[i].wristL = imgpts1.astype(int)
            cap[i].wristR = imgpts2.astype(int)

    headspng=[]

    headspng.append(cv2.imread('/home/dista/Downloads/smiley.png', cv2.IMREAD_UNCHANGED))


    previousclouds=[np.zeros((int(cap[0].height/args.rectifydown),int(cap[0].width/args.rectifydown),3))] *args.timeavg
    previousdisparities=[np.zeros((int(cap[0].height/args.rectifydown),int(cap[0].width/args.rectifydown)))] *args.timeavg

    # matplotlib.use('TkAgg')
    # X = np.random.rand(100, 3)  *4 - 2
    # Y = np.random.rand(100, 3)  *4 - 2
    # plt.ion()
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # sc = ax.scatter(X[:, 0], X[:, 1], X[:, 2])
    # fig.show()

    # def get_color_gradient(c1, c2, n):
    #     """
    #     Given two hex colors, returns a color gradient
    #     with n colors.
    #     """
    #     assert n > 1
    #     c1_rgb = np.array(c1).astype(int)
    #     c2_rgb = np.array(c2).astype(int)
    #     mix_pcts = [x / (n - 1) for x in range(n)]
    #     rgb_colors = [((1 - mix) * c1_rgb + (mix * c2_rgb)) for mix in mix_pcts]
    #     return np.array(rgb_colors).astype(
    #         int)  # ["#" + "".join([format(int(round(val*255)), "02x") for val in item]) for item in rgb_colors]
    #
    # grad = get_color_gradient([0, 0, 255], [0, 0, 240], 1080)
    # gradim = np.zeros((grad.shape[0], 1920, 3)).astype(np.uint8)
    # for i in range(gradim.shape[1]):
    #     gradim[:, i, :] = grad
    # gradim = gradim.astype(np.uint8)

    while True:

            tt = time.time()
            
            ####################################################################

            #  DATABASE GET FRAME ID
#            frame_id = store_frame(database, cap[cam_id].sn)

            if not args.thread :fetch_images()

            # GET NET OUT
            if not args.thread :
                fetch_net(q_thread_imagesnet, q_thread_net, neural_net)
            netout=q_thread_net.get(block=True,timeout=50)

            # GET CLOUD
            now = FpsCatcher.currentMilliTime()
            t = time.time()
            if not args.justdetec and count % args.hold_for ==0:
                for i in range(len(cap)):
                    if not args.thread :
                        fetch_stereo(cap[i], q_thread_imagesstereo[i], q_thread_cloud[i],count)

                    previousclouds[count % args.timeavg], previousdisparities[count % args.timeavg] = q_thread_cloud[i].get(block=True,timeout=15)
                    cap[i].cloud = np.mean(previousclouds, axis=0)
                    cap[i].disparity_to_display = np.mean(previousdisparities, axis=0)
                    #cap[i].cloud, cap[i].disparity_to_display = q_thread_cloud[i].get(block=True,timeout=15)


            globalvar.stereotime = np.int((time.time()-t)*1000)
            current = FpsCatcher.currentMilliTime()
            globalvar.stereoFps.compute(current - now)
            #print(np.amin(cap[i].disparity_to_display),np.amax(cap[i].disparity_to_display))
            #print(cap[i].disparity_to_display)

            # disparityMap = cv2.normalize(cap[0].disparity_to_display, cap[0].disparity_to_display, 0, 256,
            #                              cv2.NORM_MINMAX, cv2.CV_8UC3)
            # disparityMap = cv2.applyColorMap(disparityMap, cv2.COLORMAP_JET)
            #
            # cv2.imshow('disp',disparityMap)
            #cv2.waitKey(1)
            #if args.thread : barrier2.wait()
            # GET 2D BOXES
            compute2dboxes(args, cap, netout, neural_net)


            # for i in range(len(cap)):
            #     cap[i].image_to_display[0:int(cap[i].height/4),0:int(cap[i].width/2.5)]=0


            # GET POSITION
            t  = time.time()
            get_3d_positions_and_dimensions(args,cap, netout, neural_net)
            posi = np.int((time.time()-t)*1000)

            if args.posenet:
                positions = cap[i].object_center_positions
                if len(positions) != 0:
                    distances = np.linalg.norm(positions, axis=1)
                    sorteddistances = np.argsort(distances)
                    keep = sorteddistances[0:args.keepclosest]


                # positions = cap[0].object_center_positions
                # if len(positions)!=0:
                #     distances = np.linalg.norm(positions, axis=1)
                #     sorteddistances = np.argsort(distances)
                #     nbdetec =   len(sorteddistances)
                #     cap[0].object_center_positions=cap[0].object_center_positions[sorteddistances[0:min(nbdetec,2)]]
                #     cap[0].object_2d_boxes=cap[0].object_2d_boxes[sorteddistances[0:min(nbdetec,2)]]
                #     cap[0].object_2d_centers = cap[0].object_2d_centers[sorteddistances[0:min(nbdetec,2)]]
                #     #cap[0].object_3d_boxes = cap[0].object_3d_boxes[sorteddistances[0:min(nbdetec,2)]]

                    compute_posenet(cap,keep)
                    get_hands(args, cap)

            #compute_distance_matrix(cap[0])


             # WRITE ON IMAGE
            t  = time.time()
            write_detections_on_image(args,cap, neural_net.obj_cat_id, neural_net.obj_list,headspng)
            write = np.int((time.time()-t)*1000)   
            

#           store_detections(database, frame_id, cap[cam_id])

            ####################################################################
            # DISPLAY FINAL IMAGE AND RECORD VIDEO
            t  = time.time()
            display_and_record(args,cap)
            display = np.int((time.time()-t)*1000)
                        
            totaltime = np.int((time.time()-tt)*1000)

            avgtotalfps = (avgtotalfps * count + 1000/totaltime) / (count+1)
            count+=1

            frameCounter=frameCounter+1
            print(f'NET {np.int(globalvar.detectionFps.getFps()):3d} FPS) / STEREO : {np.int(globalvar.stereoFps.getFps()):3d} FPS ')
            print(f'net time {globalvar.nettime :3d} /  stereo {globalvar.stereotime:3d} / preprocessing {globalvar.prepro:3d} /  positions {posi:3d} /  WRITE {write:3d} /  display {display:3d} / total time : {totaltime:3d} / GLOBAL FPS : {np.int(avgtotalfps):3d} ')

            # x = cap[0].object_cloud[0][:, 0]*3
            # y = cap[0].object_cloud[0][:, 1]#*5
            # z = cap[0].object_cloud[0][:, 2]#*5
            # plt.pause(0.1)
            # sc._offsets3d = (x, -y, abs(z))
            # plt.draw()

################################################################################################################
