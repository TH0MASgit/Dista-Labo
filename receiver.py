#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np
import socket
import struct
from lib.FpsCatcher import FpsCatcher

receiveFps = FpsCatcher(autoStart=False)

MAX_DGRAM = 2**16

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break

def main():
    """ Getting image udp frame &
    concate before decode and output image """
    
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('192.168.2.69', 9999))
    dat = b''
    dump_buffer(s)

    while True:
        now = FpsCatcher.currentMilliTime()
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)
            if img is not None :
                cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''
        current = FpsCatcher.currentMilliTime()
        receiveFps.compute(current - now)
        print(receiveFps.getFps())


    # cap.release()
    cv2.destroyAllWindows()
    s.close()

if __name__ == "__main__":
    main()
