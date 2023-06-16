import cv2
import math
import numpy as np
import os
from config import *
user = os.environ['HOME']
args = parse_args()

class Stereo :
    
    def __init__(self,args):
    
                ################################################################################
            # DISPARITY COMPUTATION
            self.args=args
            if args.displim==None:
                self.num_disp = 32
            else:
                self.num_disp = args.displim    # for SGBM in HD #64 is good at 1m and above   # 32 = min 4-5 meters   16 = at least 6 meters # for BM same but no concluding
            self.min_disp=0
            self.wsize =5   # for SGBM in HD 5 is god # for BM 15 seems "ok" not concluding
            self.lambd = 8000  #8000
            self.sigma = 2 #1.5
            self.vis_mult = 1.0
            self.specklewindowsize=2
            self.speckleSize=0           
            self.maxSpeckleDiff=0    
            self.uniquenessratio=5    
            self.preFilterCap=63
            
            self.left_matcher=cv2.StereoSGBM_create(minDisparity=self.min_disp,
                                numDisparities=self.num_disp,    #256
                                blockSize=self.wsize,
                                P1=24*self.wsize*self.wsize,
                                P2=96*self.wsize*self.wsize,  #96
                            #   disp12MaxDiff=1,
                                preFilterCap=63,    #63
#                                uniquenessRatio=5,  #5
#                                speckleWindowSize=200,
                            #                                   speckleRange=2
                                mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY )   #     STEREO_SGBM_MODE_SGBM_3WAY  STEREO_SGBM_MODE_HH
    
            
            self.right_matcher = cv2.ximgproc.createRightMatcher(self.left_matcher)
            self.wls_filter = cv2.ximgproc.createDisparityWLSFilter(self.left_matcher)
            self.wls_filter.setLambda(self.lambd)
            self.wls_filter.setSigmaColor(self.sigma)
            self.left_matcher.setSpeckleWindowSize(self.specklewindowsize)
#            self.left_matcher.setUniquenessRatio(self.uniquenessratio)
#            self.left_matcher.setPreFilterCap(self.preFilterCap)

    def initalize_stereo_trackbar(self,w,h,cloud_name):
        

        def on_trackbar_set_min_disparities(value):
            self.left_matcher.setMinDisparity(max(1, value * 1))
        
        def on_trackbar_set_disparities(value):
            self.left_matcher.setNumDisparities(max(16, value * 16))
        
        def on_trackbar_set_blocksize(value):
            if not(value % 2):
                value = value + 1
            self.left_matcher.setBlockSize(max(3, value))
        
        def on_trackbar_set_speckle_range(value):
            self.left_matcher.setSpeckleRange(value)
        
        def on_trackbar_set_speckle_window(value):
            self.left_matcher.setSpeckleWindowSize(value)
        
        def on_trackbar_set_setDisp12MaxDiff(value):
            self.left_matcher.setDisp12MaxDiff(value)
        
        def on_trackbar_set_setP1(value):
            self.left_matcher.setP1(value)
        
        def on_trackbar_set_setP2(value):
            self.left_matcher.setP2(value)
        
        def on_trackbar_set_setPreFilterCap(value):
            self.left_matcher.setPreFilterCap(value)
        
        def on_trackbar_set_setUniquenessRatio(value):
            self.left_matcher.setUniquenessRatio(value)
        
        def on_trackbar_set_wlsLmbda(value):
            self.wls_filter.setLambda(value)
        
        def on_trackbar_set_wlsSigmaColor(value):
            self.wls_filter.setSigmaColor(value)
        
        def on_trackbar_null(value):
            return        
        
    
        cv2.createTrackbar("Min Disparity(x 16): ", cloud_name, 0, 16, on_trackbar_set_min_disparities)
        cv2.createTrackbar("Max Disparity(x 16): ", cloud_name, int(self.num_disp/16), 16, on_trackbar_set_disparities)
        cv2.createTrackbar("Window Size: ", cloud_name, self.wsize, 50, on_trackbar_set_blocksize)
        cv2.createTrackbar("Speckle Window: ", cloud_name, self.specklewindowsize, 200, on_trackbar_set_speckle_window)
        cv2.createTrackbar("LR Disparity Check Diff:", cloud_name, 0, 25, on_trackbar_set_setDisp12MaxDiff)
        cv2.createTrackbar("Disparity Smoothness P1: ", cloud_name, 0, 4000,on_trackbar_set_setP1)
        cv2.createTrackbar("Disparity Smoothness P2: ", cloud_name, 0, 16000,on_trackbar_set_setP2 )
        cv2.createTrackbar("Pre-filter Sobel-x- cap: ", cloud_name, 0, 5, on_trackbar_set_setPreFilterCap)
        cv2.createTrackbar("Winning Match Cost Margin %: ", cloud_name, 0, 20,on_trackbar_set_setUniquenessRatio)
#        cv2.createTrackbar("Speckle Size: ", cloud_name, math.floor((w * h) * 0.0005), 10000, on_trackbar_null)  #* 0.0005), 10000,
#        cv2.createTrackbar("Max Speckle Diff: ", cloud_name, 16, 2048, on_trackbar_null)
        cv2.createTrackbar("Speckle Size: ", cloud_name, 0, 10000, on_trackbar_null)  #* 0.0005), 10000,
        cv2.createTrackbar("Max Speckle Diff: ", cloud_name, 0, 2048, on_trackbar_null)
        cv2.createTrackbar("WLS Filter Lambda: ", cloud_name, self.lambd, 10000,on_trackbar_set_wlsLmbda)
        cv2.createTrackbar("WLS Filter Sigma Color (x 0.1): ", cloud_name, math.ceil(self.sigma), 50,
                           on_trackbar_set_wlsSigmaColor)
    
    
    
    
    def get_pointcloud(self,left_frame_rect,right_frame_rect,coeff,cloud_name):
        
        
        f,base,px_left,py_left=coeff[4:8]
        Q=coeff[8]

        left_matcher=self.left_matcher
        right_matcher=self.right_matcher
        wls_filter=self.wls_filter
        
        left_frame_rect =cv2.cvtColor(left_frame_rect, cv2.COLOR_BGR2GRAY) #
        right_frame_rect = cv2.cvtColor(right_frame_rect, cv2.COLOR_BGR2GRAY)                 
        
    
        
        downscale=2
        n_width = int(left_frame_rect.shape[1] * 1/downscale)
        n_height = int(left_frame_rect.shape[0] * 1/downscale) 
        left_frame_rect_down = cv2.resize(left_frame_rect, (n_width, n_height))
        right_frame_rect_down = cv2.resize(right_frame_rect,(n_width, n_height))

        left_disp = left_matcher.compute(cv2.UMat(left_frame_rect_down), cv2.UMat(right_frame_rect_down))
        right_disp = right_matcher.compute(cv2.UMat(right_frame_rect_down), cv2.UMat(left_frame_rect_down))  
        left_disp = np.int16(cv2.UMat.get(left_disp))
        right_disp = np.int16(cv2.UMat.get(right_disp))    
    
#    
#        print(left_disp)
#        print(right_disp)
#        print(left_frame_rect)

        filtered_disp = wls_filter.filter(left_disp,left_frame_rect,None,right_disp  )
        
        if self.args.cloudtrackbar and self.args.showcloud :
            speckleSize = cv2.getTrackbarPos("Speckle Size: ", cloud_name)
            maxSpeckleDiff = cv2.getTrackbarPos("Max Speckle Diff: ", cloud_name)
            cv2.filterSpeckles(filtered_disp, 0, speckleSize, maxSpeckleDiff)
        else:
            cv2.filterSpeckles(filtered_disp, 0, self.speckleSize, self.maxSpeckleDiff)    
    
        
        filtered_disp =filtered_disp.astype(np.float32) / 16.0 
            
        minDisp = np.min(filtered_disp)
        maxDisp = np.max(filtered_disp)

        disparity_to_display = ((filtered_disp - minDisp) / (maxDisp-minDisp) * 255. ).astype(np.uint8)
        cloud = cv2.reprojectImageTo3D(filtered_disp, Q, handleMissingValues=True)        
                    
        return [cloud,disparity_to_display]
        ################################################################################