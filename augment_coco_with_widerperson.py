#%%
#%% 
import shutil
import PIL
import json
import numpy as np
import copy
#%%
annot = open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_train2017_person.json", 'r')
annotation = json.load(annot)

path='/home/dista/Documents/dista/efficientdetection/datasets/WiderPerson'
cocopath='/home/dista/Documents/dista/efficientdetection/datasets/coco'

trainimgidfile =open(path+'/train.txt', 'r')

coco_annotid=9000000000000
coco_imgid=9000000000000

ctnot=0
ctimg=0
for line in trainimgidfile:
    line=line.split()
    widerperson_imgid=line[0]
    shutil.copy(path+'/Images/'+widerperson_imgid+'.jpg', cocopath+'/train2017/'+str(coco_imgid)+'.jpg') 

    image = PIL.Image.open(path+'/Images/'+widerperson_imgid+'.jpg')
    width, height = image.size
        
    newima= {"license": 1,"file_name": str(coco_imgid) +".jpg","coco_url": "na","height": height,"width": width,"date_captured": "na","flickr_url": "na","id": coco_imgid,}      
#    annotation['images'].append(newima)    
    annotation["images"].insert(0,newima)    
#    annotation['images'][ctimg]=newima   
#    annotation['images'][ctimg]["license"]=1   
#    annotation['images'][ctimg]["file_name"]=str(coco_imgid) +".jpg"   
#    annotation['images'][ctimg]["coco_url"]=r"na"   
#    annotation['images'][ctimg]["height"]=height   
#    annotation['images'][ctimg]["width"]=width   
#    annotation['images'][ctimg]["date_captured"]=r"2013-11-14 11:18:45"   
#    annotation['images'][ctimg]["flickr_url"]=r"na"   
#    annotation['images'][ctimg]["id"]=coco_imgid   




    
    
    anotfile =open('/home/dista/Documents/dista/efficientdetection/datasets/WiderPerson/Annotations/'+ widerperson_imgid +'.jpg.txt', 'r')
    firstline=next(anotfile)
    for line in anotfile:
        numbers=line.split()
        box=[]
        for number in numbers:
            box.append(float(number))
            
        if box[0]!=4 and box[0]!=5:              
            newnot={"segmentation": [[213.5, 227.79, 259.62, 202.1, 232.1, 219.2]],"area": 14484,"iscrowd": 0,"image_id": coco_imgid,"bbox": [box[1],box[2],box[3]-box[1],box[4]-box[2]],"category_id": 1,"id": coco_annotid,}
    #        annotation['annotations'].append(newnot)    
            annotation["annotations"].insert(0,newnot)    
    #        annotation['annotations'][ctnot]=newnot
    #        annotation['annotations'][ctnot]["segmentation"]=[[213.5, 227.79, 259.62]]
    #        annotation['annotations'][ctnot]["area"]=14484   
    #        annotation['annotations'][ctnot]["iscrowd"]=0   
    #        annotation['annotations'][ctnot]["image_id"]=coco_imgid   
    #        annotation['annotations'][ctnot]["bbox"]=[box[1],box[2],box[3]-box[1],box[4]-box[2]]   
    #        annotation['annotations'][ctnot]["category_id"]=1   
    #        annotation['annotations'][ctnot]["id"]=coco_annotid   
            ctnot+=1
    
            
            coco_annotid+=1

    coco_imgid+=1
    ctimg+=1        

new_annot = open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_train2017_person_augmented_widerpers.json", 'w')
json.dump(annotation, new_annot) 

#%%
annot = open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_val2017_person.json", 'r')
annotation = json.load(annot)

path='/home/dista/Documents/dista/efficientdetection/datasets/WiderPerson'
cocopath='/home/dista/Documents/dista/efficientdetection/datasets/coco'

valimgidfile =open(path+'/val.txt', 'r')

coco_annotid=8000000000000
coco_imgid=8000000000000

ctnot=0
ctimg=0
for line in valimgidfile:
    line=line.split()
    widerperson_imgid=line[0]
    shutil.copy(path+'/Images/'+widerperson_imgid+'.jpg', cocopath+'/val2017/'+str(coco_imgid)+'.jpg') 

    image = PIL.Image.open(path+'/Images/'+widerperson_imgid+'.jpg')
    width, height = image.size
    

    newima= {"license": 1,"file_name": str(coco_imgid) +".jpg","coco_url": "na","height": height,"width": width,"date_captured": "na","flickr_url": "na","id": coco_imgid,}      
#    annotation['images'].append(newima)    
    annotation["images"].insert(0,newima)    
#    annotation['images'][ctimg]=newima   
#    annotation['images'][ctimg]["license"]=1   
#    annotation['images'][ctimg]["file_name"]= str(coco_imgid) +".jpg"   
#    annotation['images'][ctimg]["coco_url"]=r"na"   
#    annotation['images'][ctimg]["height"]=height   
#    annotation['images'][ctimg]["width"]=width   
#    annotation['images'][ctimg]["date_captured"]=r"2013-11-14 11:18:45"   
#    annotation['images'][ctimg]["flickr_url"]=r"na"   
#    annotation['images'][ctimg]["id"]=coco_imgid  
    
    


    anotfile =open('/home/dista/Documents/dista/efficientdetection/datasets/WiderPerson/Annotations/'+ widerperson_imgid +'.jpg.txt', 'r')
    firstline=next(anotfile)
    for line in anotfile:
        numbers=line.split()
        box=[]
        for number in numbers:
            box.append(float(number))
            
        if box[0]!=4 and box[0]!=5:              
            newnot={"segmentation": [[213.5, 227.79, 259.62, 202.1, 232.1, 219.2]],"area": 14484,"iscrowd": 0,"image_id": coco_imgid,"bbox": [box[1],box[2],box[3]-box[1],box[4]-box[2]],"category_id": 1,"id": coco_annotid,}
    #        annotation['annotations'].append(newnot)    
            annotation["annotations"].insert(0,newnot)    
    #        annotation['annotations'][ctnot]=newnot
    #        annotation['annotations'][ctnot]["segmentation"]=[[213.5, 227.79, 259.62]]
    #        annotation['annotations'][ctnot]["area"]=14484   
    #        annotation['annotations'][ctnot]["iscrowd"]=0   
    #        annotation['annotations'][ctnot]["image_id"]=coco_imgid   
    #        annotation['annotations'][ctnot]["bbox"]=[box[1],box[2],box[3]-box[1],box[4]-box[2]]   
    #        annotation['annotations'][ctnot]["category_id"]=1   
    #        annotation['annotations'][ctnot]["id"]=coco_annotid   
            ctnot+=1
            
            coco_annotid+=1

    coco_imgid+=1
    ctimg+=1        

new_annot = open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_val2017_person_augmented_widerpers.json", 'w')
json.dump(annotation, new_annot) 


#%%
with open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_val2017_person_augmented_widerpers.json", 'r') as annot:
    annotation_augmented = json.load(annot)
#%%
with open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_val2017.json", 'r') as annot:
    annotation_augmented = json.load(annot)

# %% delete all non person annotation : that'S my solution for coco_eval.py
    # not necessay if already deleted from coco see coco_person_only.py
#
#annotlist=copy.deepcopy(annotation_augmented['annotations'])
#del annotation_augmented['annotations']
#annotation_augmented['annotations']=[]
#
#for i in range(len(annotlist)):    
#    if annotlist[i]['category_id']==1:
#        annotation_augmented['annotations'].append(annotlist[i])
#
#new_annot = open("/home/dista/Documents/dista/efficientdetection/datasets/coco/annotations/instances_val2017_augmented_widerpers.json", 'w')
#json.dump(annotation_augmented, new_annot) 
#%%
for a in annotation:    
    print(a)

for a in annotation_augmented:    
    print(a)


#%%
for a in annotation_augmented['annotations']:    
    print(a['bbox'])
    print(a['category_id'])
    print(a['image_id'])
    print(a['id'])
# %%

a =annotation_augmented['annotations'][-100]
print(a)    
    
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
anno=annotation_augmented['annotations']
cate=annotation_augmented['categories']
ima=annotation_augmented['images']

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
            

