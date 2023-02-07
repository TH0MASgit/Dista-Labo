import os, sys

user = os.environ['HOME']
from config import *
from lib.NetCam import *

if __name__ == '__main__':
    print('Started client.py...')
    args = parse_args()


    if len(args.linuxid) != 0:
        source = args.linuxid

    netCam = NetCam(display='HD',
                    capture=args.resolution,
                    isStereoCam=True,
                    ip = args.ip[0],
                    port=args.ports_in)

    if args.vflip:
        netCam.invertVertical()

    try:
        netCam.toggleDebug()
        while netCam.isRunning():
           netCam.display()


    except KeyboardInterrupt:
        netCam.clearAll()
    except Exception as err:
        netCam.clearAll()
        raise err
    exit()
