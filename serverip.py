import mmap
import time
import os
import cv2

print("Opening camera...")

#cap = cv2.VideoCapture(0)

#ip='192.168.59.40'
ip='10.180.5.124'

port=8554 #8554
#cap = cv2.VideoCapture(f'rtsp://admin:m0P04b*PYMG@{ip}:{port}/profile3/media.smp')  
cap = cv2.VideoCapture(f'rtsp://admin:Admin2021@{ip}:{port}/profile4/media.smp')
1080

print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 640
print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 480
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
h=720
w=1280
shape = (h, w, 3)
n = (h*w*3)



fd = os.open('/tmp/mmaptest', os.O_CREAT | os.O_TRUNC | os.O_RDWR)

#os.write(fd, b'\x00' * n)  # resize file
os.truncate(fd, n)  # resize file

mm = None
try:
    while True:
        ret, img = cap.read()
        
        print(img.shape)
        
        if not ret:
            break
        
        if mm is None:
            mm = mmap.mmap(fd, n, mmap.MAP_SHARED, mmap.PROT_WRITE)  # it has to be only for writing

        # write image
        start = time.perf_counter()
        
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