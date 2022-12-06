import mmap
import time
import os
import cv2

print("Opening camera...")

cap = cv2.VideoCapture(0)
#print(cap.get(cv.CAP_PROP_FRAME_WIDTH))  # 640
#print(cap.get(cv.CAP_PROP_FRAME_HEIGHT)) # 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1344)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 376)
h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
shape = (h, w, 3)
n = (h*w*3)

fd = os.open('/tmp/mmaptest', os.O_CREAT | os.O_TRUNC | os.O_RDWR)
#os.write(fd, b'\x00' * n)  # resize file
os.truncate(fd, n)  # resize file

mm = None
try:
    while True:
        ret, img = cap.read()
        
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