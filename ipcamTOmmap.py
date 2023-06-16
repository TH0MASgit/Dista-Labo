import mmap
import time
import os
import cv2
from config import *

args = parse_args()

if len(args.pwd) != 0:
    pwd = list(args.pwd.split(','))

ip = args.ip

if len(args.ports_in) != 0:
    port = list(args.ports_in.split(','))

if len(args.camid) != 0:
    camid = list(args.camid.split(','))

print(camid[0])

cap = cv2.VideoCapture(f'rtsp://admin:{pwd[0]}@{ip[0]}:{port[0]}/profile1/media.smp')

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 640
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 480
print(w)
print(h)
n = (h*w*3)
fd = os.open('/tmp/mmapqds'+camid[0], os.O_CREAT | os.O_TRUNC | os.O_RDWR)
os.truncate(fd, n)  # resize file
mm = mmap.mmap(fd, n, mmap.MAP_SHARED, mmap.PROT_WRITE)  # it has to be only for writing

try:
    while True:
        ret, img = cap.read()
        if not ret:
            break
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