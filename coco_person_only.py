# %% 
import shutil
import PIL
import json
import numpy as np
import copy

#%%
with open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_train2017.json", 'r') as annot:
    annotation = json.load(annot)

# %% delete all non person annotation 
    
annotlist=copy.deepcopy(annotation['annotations'])
del annotation['annotations']
annotation['annotations']=[]

for i in range(len(annotlist)):    
    if annotlist[i]['category_id']==1:
        annotation['annotations'].append(annotlist[i])

new_annot = open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_train2017_person.json", 'w')
json.dump(annotation, new_annot) 

#%%
with open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_train2017_person.json", 'r') as annot:
    annotation = json.load(annot)

#%%
for a in annotation:    
    print(a)

#%%
for a in annotation['annotations']:    
#    print(a['bbox'])
    print(a['category_id'])
#    print(a['image_id'])
#    print(a['id'])
    
#%% this does not work because or
anno=annotation['annotations']
cate=annotation['categories']
ima=annotation['images']
licen=annotation['licenses']

for i in range(1):
    print(cate[i]['name'])
    print(cate[i]['supercategory'])
    print(cate[i]['id'])    
    
for i in range(1):    
    
    print(anno[i]['bbox'])
    print(anno[i]['category_id'])
    print(anno[i]['image_id'])
    print(anno[i]['id'])
    print(anno[i]['area'])
    print(anno[i]['segmentation'])
    
for i in range(1):
    print(ima[i]['file_name'])
    print(ima[i]['height'])
    print(ima[i]['width'])
    print(ima[i]['id'])
    print(ima[i]['date_captured'])
    print(ima[i]['coco_url'])
    print(ima[i]['flickr_url'])
    print(ima[i]['license'])
        
    
for i in range(8):
    print(licen[i]['id'])
    print(licen[i]['name'])
    print(licen[i]['url']) 
    
#%%
    
    
    
    
    
    
    
with open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_val2017.json", 'r') as annot:
    annotation = json.load(annot)

# %% delete all non person annotation 
    
annotlist=copy.deepcopy(annotation['annotations'])
del annotation['annotations']
annotation['annotations']=[]

for i in range(len(annotlist)):    
    if annotlist[i]['category_id']==1:
        annotation['annotations'].append(annotlist[i])

new_annot = open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_val2017_person.json", 'w')
json.dump(annotation, new_annot) 

#%%
# with open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_val2017_person.json", 'r') as annot:
#     annotation = json.load(annot)
#
# #%%
# for a in annotation:
#     print(a)
#
# #%%
# for a in annotation['annotations']:
# #    print(a['bbox'])
#     print(a['category_id'])
# #    print(a['image_id'])
# #    print(a['id'])
#
# #%% this does not work because or
# anno=annotation['annotations']
# cate=annotation['categories']
# ima=annotation['images']
# licen=annotation['licenses']
#
# for i in range(1):
#     print(cate[i]['name'])
#     print(cate[i]['supercategory'])
#     print(cate[i]['id'])
#
# for i in range(1):
#
#     print(anno[i]['bbox'])
#     print(anno[i]['category_id'])
#     print(anno[i]['image_id'])
#     print(anno[i]['id'])
#     print(anno[i]['area'])
#     print(anno[i]['segmentation'])
#
# for i in range(1):
#     print(ima[i]['file_name'])
#     print(ima[i]['height'])
#     print(ima[i]['width'])
#     print(ima[i]['id'])
#     print(ima[i]['date_captured'])
#     print(ima[i]['coco_url'])
#     print(ima[i]['flickr_url'])
#     print(ima[i]['license'])
#
#
# for i in range(8):
#     print(licen[i]['id'])
#     print(licen[i]['name'])
#     print(licen[i]['url'])
#
