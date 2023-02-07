<













# =============================================================================
 =ÉIMPORT os, sys
# =============================================================================

user = os.environ['HOME']
from config import *
from lib.NetCam import *

if __name__ == '__main__':
    print('Started streamer.py...')
    args = parse_args()

    source = 0
    display = None
    
    if len(args.linuxid) != 0:
        source = args.linuxid


    # print(f'display : {args.display}')

    netCam = NetCam(display=args.display,
                    source=source,
                    capture=args.resolution,
                    isCsiCam = args.csi,
                    port=args.ports_in)

    if args.vflip:
        netCam.invertVertical()

    # netCam.toggleFullScreen()
    netCam.toggleDebug()
    netCam.startBroadcast()

    try:
        while netCam.isRunning():
           netCam.display()


    except KeyboardInterrupt:
        netCam.clearAll()
    except Exception as err:
        netCam.clearAll()
        raise err
    exit()
