################################################################################
##          Classe NetCam
##      Gere un flux camera caméra à travers un réseau
##  Author : J. Coupez
##  Date : 10/10/2020
##  Copyright Dista
##  Version : 1.0
################################################################################

import json
import socket
import subprocess
import time
from threading import Thread

import cv2
import numpy as np
import zmq

from lib.FpsCatcher import FpsCatcher

class NetCam:
    DEFAULT_CLIENT_PORT = '5555'
    DEFAULT_WINDOW_NAME = 'Stream'
    WINDOW_COUNTER = 0

    DEFAULT_RES = 'HD'
    MAX_FPS = 60
    NBR_BUFFER = 5

    TEXT_COLOR = (0, 0, 255)
    TEXT_POSITION = (0, 0)

    def __init__(self,
                 capture='VGA',
                 display=None,
                 isStereoCam=None,
                 isCsiCam=False,
                 source='0',
                 ip=None,
                 port=None,
                 consolelog=True):

        self.consoleLog = consolelog
        self.captureResolution = capture
        self.displayResolution = display
        self.source = source
        self.isCsiCam = isCsiCam
        self.isFlirCam = False

        self.checkIsStereoCam(isStereoCam)

        self.imgWidth, self.imgHeight = resolutionFinder(self.captureResolution)

        self.displayWidth, self.displayHeight = resolutionFinder(self.displayResolution)

        self.fps = NetCam.MAX_FPS

        self.imgBuffer = [np.zeros((self.imgHeight,self.imgWidth,3),dtype=np.uint8)] * NetCam.NBR_BUFFER
        self.imgBufferReady = 0
        self.imgBufferWriting = 0
        self.flipVertical = False
        self.flipHorizontal = False
        self.isReleased = False
        self.isCaptureRunning = False
        self.isDisplayRunning = False
        self.isNetworkRunning = False
        self.fullScreen = False
        self.videoStream = None
        self.videoStreamSecondary = None
        self.cameraSettingName = None
        self.cameraSettingValue = None

        ## Debug informations
        self.displayDebug = False
        self.showStereo = False
        self.displayFps = FpsCatcher()
        self.captureFps = FpsCatcher()
        self.networkFps = FpsCatcher()

        # Network information
        self.hostname = socket.gethostname()
        self.ip_address = ip
        self.ip_port = port or NetCam.DEFAULT_CLIENT_PORT
        self.command_port = int(self.ip_port) + 1
        self.windowName = ip or self.hostname or NetCam.DEFAULT_WINDOW_NAME
        NetCam.WINDOW_COUNTER += 1
        if NetCam.WINDOW_COUNTER > 1:
            self.windowName += f' ({NetCam.WINDOW_COUNTER})'
        self.commandSocket = None
        self.threadList = []

        self.console('Starting NetCam...')

        if self.ip_address is None:
            # Start the capture
            self.startCapture()
        else:
            # Start to receive the stream
            self.startReceive()

        time.sleep(0.1)

        ## Init the display when requested (on main thread)
        if self.displayResolution:
            self.initDisplay()
            time.sleep(0.1)

    def startCapture(self):
        """
            Start capturing video frame and put them in the imgBuffer
        """
        ## Close any previously opened stream
        if self.isCaptureRunning and self.videoStream:
            self.videoStream.release()
            if self.videoStreamSecondary:
                self.videoStreamSecondary.release()
            self.isCaptureRunning = False

        if isinstance(self.source, str) and ',' in self.source:
            sourceList = self.source.split(",")
            self.videoStream = self.initVideoStream(sourceList[0])
            self.videoStreamSecondary = self.initVideoStream(sourceList[1])
        else:
            self.videoStream = self.initVideoStream(self.source)

        self.checkIsStereoCam(self.isStereoCam)
        width, height = resolutionFinder(self.captureResolution, self.isStereoCam)

        self.imgWidth = width
        self.imgHeight = height

        if self.videoStream.isOpened():
            ## Get the real width, height and fps supported by the camera
            self.imgWidth = int(self.videoStream.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.imgHeight = int(self.videoStream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.console(f'Requested Camera resolution : {width}x{height}', 2)
            self.console(f'Retrieved Camera resolution : {self.imgWidth}x{self.imgHeight}', 2)

            if self.videoStreamSecondary and self.videoStreamSecondary.isOpened():
                self.imgWidth += int(self.videoStreamSecondary.get(cv2.CAP_PROP_FRAME_WIDTH))

            # ratio = float(self.imgWidth) / float(self.imgHeight)
            # if ratio > 2.0:
            #     self.isStereoCam = True  # Ratio more than double = probably a stereo cam
            #     self.showStereo = True  # by default display stereo
            self.fps = self.videoStream.get(cv2.CAP_PROP_FPS)
            self.console(f'Retrieved Camera FPS : {self.fps}', 2)

        self.computeDisplayHeight()

        ## prepare the triple buffering
        self.imgBufferWriting = 0
        for i in range(NetCam.NBR_BUFFER):
            # Initialise each buffer
            self.imgBuffer[i] = np.zeros(shape=(self.imgHeight, self.imgWidth, 3), dtype=np.uint8)
        ## Guarantee the first frame
        frame = self.renderWaitingMessage(self.imgBuffer[self.imgBufferWriting])
        self.imgBuffer[self.imgBufferWriting] = frame
        self.imgBufferReady = self.imgBufferWriting
        self.imgBufferWriting += 1

        ## Launch the capture thread
        self.console(f'Capture resolution : {self.imgWidth} x {self.imgHeight} @ {self.fps}', 1)
        videoThread = Thread(target=self.captureThreadRunner, args=([self.videoStream, self.videoStreamSecondary]),
                             daemon=True)
        videoThread.start()

    def startBroadcast(self):
        """
            Launch the network client ( broadcast the camera signal)
        """

        ## Launch the networdThread
        self.ip_address = get_ip()

        self.console(f'Launch broadcast...')
        zmqContext = zmq.Context()
        socket = zmqContext.socket(zmq.PUB)
        workerThread = Thread(target=self.clientThreadRunner, args=([socket]))
        self.threadList.append(workerThread)
        workerThread.start()
        time.sleep(0.1)

        # Start a command thread that will listen to command from a connected machine
        commandThread = Thread(target=self.commandThreadRunner)
        self.threadList.append(commandThread)
        commandThread.start()
        time.sleep(0.1)

        self.console(f'Now broadcasting. URI of Camera : {self.ip_address}:{self.ip_port} !')

    def startReceive(self):
        """
             Launch the network client ( broadcast the camera signal)
        """
        ## Launch the networdThread
        self.console(f'Connecting to camera on {self.ip_address}:{self.ip_port}...', 1)

        zmqContext = zmq.Context()
        socket = zmqContext.socket(zmq.SUB)
        workerThread = Thread(target=self.serverThreadRunner, args=([socket]), daemon=True)
        self.threadList.append(workerThread)
        workerThread.start()
        time.sleep(0.1)

    def getCsiSourceName(self, sensor_id=0):
        width, height = resolutionFinder(self.captureResolution)
        return ('nvarguscamerasrc sensor-id=%d ! '
                'video/x-raw(memory:NVMM), '
                'width=(int)%d, height=(int)%d, '
                'format=(string)NV12, framerate=(fraction)%d/1 ! '
                'nvvidconv flip-method=0 ! '
                'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
                'videoconvert ! '
                'video/x-raw, format=(string)BGR ! appsink' % (
                    sensor_id, width, height, self.fps, width, height))

    def initVideoStream(self, source):
        """
            Initialize the video stream with the right resolution and settings
        :param source: the name of the camera device to use for capture. use video0 if not provided
        """

        linuxId = source
        videoStream = None

        if isinstance(source, str):
            if source.startswith("/dev/video"):
                source = source.replace("/dev/video","")
            if len(source) == 1:
                linuxId = int(source)
            elif source.startswith("flir://"):
                import EasyPySpin
                linuxId = int(source.replace("flir://", ''))
                videoStream = EasyPySpin.VideoCapture(linuxId)
                self.isFlirCam = True

        if videoStream is None:
            captureMode = cv2.CAP_V4L2
            if self.isCsiCam:
                command = ['sudo', 'service', 'nvargus-daemon', 'restart']
                subprocess.call(command, shell=True)
                self.console("Restart nvargus-daemon ")
                self.imgWidth, self.imgHeight = resolutionFinder(self.displayResolution)
                linuxId = self.getCsiSourceName(linuxId)
                captureMode = cv2.CAP_GSTREAMER
            videoStream = cv2.VideoCapture(linuxId, captureMode)

        isOpened = videoStream.isOpened()
        ## Launch the camera capture thread
        self.console(f'Init camera {source} capture...{isOpened}', 1)

        if not isOpened:
            # Try to open the camera without the Video for linux driver
            videoStream = cv2.VideoCapture(linuxId)
            isOpened = videoStream.isOpened()
            self.console(f'Trying without captureMode...{isOpened}', 2)

        ## Get the requested resolution
        width, height = resolutionFinder(self.captureResolution, self.isStereoCam)

        if isOpened:
            if not self.isCsiCam:
                ## Define all video settings
                videoStream.set(cv2.CAP_PROP_BUFFERSIZE,
                                NetCam.NBR_BUFFER)  # increase camera buffering to 3 for triple buffering
                videoStream.set(cv2.CAP_PROP_FPS, NetCam.MAX_FPS)  # try to put the fps to MAX_FPS
                videoStream.set(cv2.CAP_PROP_FOURCC,
                                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # define the compression to mjpg
                if width is not None:
                    videoStream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                if height is not None:
                    videoStream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        else:
            self.console(
                f'Unable to open the camera . Is your camera connected (look for /dev/video{source} in terminal)')
        return videoStream

    def captureThreadRunner(self, stream, streamSecondary):
        """
            Read next stream frame in a daemon thread
        :param stream: videoStream to read from
        :param streamSecondary: videoStream to read from as a second source
        """

        if not stream.isOpened():
            time.sleep(3)
            if not self.isReleased:
                # Unable to connect, retry
                self.console(f'Unable to find the camera, waiting 3s before retry...', 1)
                self.startCapture()
            return

        self.isCaptureRunning = True
        self.console('Capture thread is now running.', 1)
        failureCounter = 0

        while self.isCaptureRunning:
            # Look if we need to update a camera setting
            if self.cameraSettingName is not None:
                stream.set(self.cameraSettingName, self.cameraSettingValue)
                if streamSecondary:
                    streamSecondary.set(self.cameraSettingName, self.cameraSettingValue)
                self.console(f"Updated {self.cameraSettingName}, {self.cameraSettingValue}")
                self.cameraSettingName = None
                time.sleep(0.01)

            # For buffering : Never read where we write
            try:
                result, frame = stream.read()
                resultSecondary = True
                frameSecondary = []
                if streamSecondary:
                    resultSecondary, frameSecondary = streamSecondary.read()
                if result and resultSecondary:
                    failureCounter = 0
                    self.imgBuffer[self.imgBufferWriting] = self.applyTransformation(frame, frameSecondary)
                    self.imgBufferReady = self.imgBufferWriting
                    self.imgBufferWriting = 0 if self.imgBufferWriting == NetCam.NBR_BUFFER - 1 else self.imgBufferWriting + 1
                else:
                    failureCounter += 1
                    self.console(f'frame is not grabbed. {failureCounter} so far...')
                    time.sleep(0.1)

            except Exception as err:
                failureCounter += 1
                self.console(f'Capture error (failureCounter), retry in 1s.')
                time.sleep(1)

            if self.displayDebug:
                self.captureFps.compute()

            if failureCounter > 10:
                self.console(f'Too much capture failure ')
                break
            time.sleep(0.001)

        if self.videoStream and self.videoStream.isOpened():
            self.videoStream.release()
            if self.videoStreamSecondary:
                self.videoStreamSecondary.release()
            self.console('Released camera.', 1)

        self.videoStream = None
        self.videoStreamSecondary = None
        if failureCounter > 10:
            # Too much failure : retry connecting to the camera
            self.console(f'Retry connecting to the camera...', 1)
            self.startCapture()
        else:
            # Normal Exit
            self.console('Capture thread stopped.', 1)

    def clientThreadRunner(self, socket):
        """
            Publish Data to any connected Server
        :param socket:
        """
        url_publish = "tcp://*:%s" % self.ip_port
        socket.setsockopt(zmq.CONFLATE, 1)
        socket.set_hwm(2)
        socket.bind(url_publish)
        self.isNetworkRunning = True
        self.console(f'Network thread is now running ( {url_publish} )...', 1)


        while self.isNetworkRunning:
            if self.displayDebug:
                self.networkFps.compute()
            currentTime = FpsCatcher.currentMilliTime()
            frame = self.imgBuffer[self.imgBufferReady]
            if frame is not None:
                encoded, buffer = cv2.imencode('.bmp', frame)
                socket.send(buffer, copy=False)
            processTime = FpsCatcher.currentMilliTime() - currentTime
            self.console(f'NetworkProcessing time : {processTime} - Network FPS : {self.networkFps.getFps()}')
            waitTime = 1
            if processTime > 0 and processTime < 30:
                waitTime = 30 - processTime
            waitTime = waitTime / 1000.0
            time.sleep(waitTime)

        self.console('Network thread stopped.')

    def commandThreadRunner(self):
        """
            Wait for a host to connect and reply with command result
        """
        url_publish = "tcp://*:%s" % self.command_port

        zmqContext = zmq.Context()

        while self.isNetworkRunning:
            # Open a channel to listen the server
            try:
                # commandSocket.setsockopt(zmq.SOL_SOCKET, zmq.SO_REUSEADDR, 1)
                self.commandSocket = zmqContext.socket(zmq.PAIR)
                self.commandSocket.bind(url_publish)
                poller = zmq.Poller()
                poller.register(self.commandSocket, zmq.POLLIN)

                should_continue = True
                while self.isNetworkRunning and should_continue:
                    socks = dict(poller.poll(1000))
                    if self.commandSocket in socks and socks[self.commandSocket] == zmq.POLLIN:
                        json_string = self.commandSocket.recv()
                        # There is a command : manage it
                        response = self.receiveCommand(json_string)
                        # Send back the result
                        self.commandSocket.send_string(response)
                        # should_continue = False
                # self.commandSocket.close()


            except Exception as err:
                # Swallow the exception
                self.console(f'Error while receiving command {err}.')
            finally:
                zmqContext.term()
                zmqContext = zmq.Context()

        self.console('Command thread stopped.')

    def serverThreadRunner(self, socket):
        url_publisher = f"tcp://{self.ip_address}:{self.ip_port}"

        socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
        socket.set_hwm(2)
        socket.setsockopt(zmq.CONFLATE, 1)
        socket.connect(url_publisher)
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        self.isNetworkRunning = True

        self.console(f'Connected To {url_publisher}')
        timeoutMsg = 0
        bufferSize = 0

        while self.isNetworkRunning:
            try:
                socks = dict(poller.poll())
                if socket in socks and socks[socket] == zmq.POLLIN:
                    buffer = socket.recv(flags=zmq.NOBLOCK, copy=False)
                    bufferSize += len(buffer) / 1024
                    shape = [len(buffer.bytes), 1]
                    buffer = np.frombuffer(buffer, dtype='uint8')
                    buffer = buffer.reshape(shape)

                    # For buffering : Never read where we write
                    self.imgBufferReady = self.imgBufferWriting
                    self.imgBufferWriting = 0 if self.imgBufferWriting == NetCam.NBR_BUFFER - 1 else self.imgBufferWriting + 1

                    self.imgBuffer[self.imgBufferWriting] = cv2.imdecode(buffer, 1)

                    if self.displayDebug:
                        self.networkFps.compute()

                    if timeoutMsg >= 1000:  # 1 sec elapsed
                        self.console(f'Re-Connected To {url_publisher}')
                    timeoutMsg = 0

            except Exception as err:
                timeoutMsg += 1
                if timeoutMsg >= 3000:  # 3 sec before writing timeout message
                    self.console(f'Waiting image from {url_publisher} ...')
                    timeoutMsg = 0

            time.sleep(0.001)

        self.isNetworkRunning = False
        self.console('Network thread stopped.')

    def getDetail(self):
        width = 0
        if self.imgWidth is not None:
            width = self.imgWidth
        if self.isStereoCam:
            width = 2 * width

        return ({
            'captureResolution': self.captureResolution,
            'displayResolution': self.displayResolution,
            'isStereo': self.isStereoCam,
            'imwidth': self.imgWidth,
            'width': width,
            'height': self.imgHeight,
            'maxFps': self.fps,
            'isCaptureRunning': self.isCaptureRunning,
        })

    def initDisplay(self):
        self.console('Init display...', 1)
        self.console(f'Display resolution : {self.displayResolution} ({self.displayWidth} x {self.displayHeight})', 2)
        cv2.namedWindow(self.windowName, cv2.WINDOW_GUI_NORMAL)
        self.toggleFullScreen(self.fullScreen)
        self.isDisplayRunning = True
        time.sleep(0.1)
        self.console('Display is now ready.', 2)

    def read(self):
        frame = self.imgBuffer[self.imgBufferReady]

        if self.displayDebug:
            self.displayFps.compute()
            width = self.displayWidth or 1280
            debugTextSize = width / 1280
            thickness = 1 if width < 1280 else 2

            textPosX, textPosY = NetCam.TEXT_POSITION
            textPosX += int(40 * debugTextSize)
            textPosY += int(40 * debugTextSize)
            captureString = ''
            displayString = ''
            networkString = ''
            if self.captureFps.fps > 0.0:
                captureString = f'Capture : {self.captureFps.fps:.2f} fps ({self.captureResolution}) | '
            if self.displayFps.fps > 0.0:
                displayString = f'Display : {self.displayFps.fps:.2f} fps ({self.displayResolution}) | '
            if self.networkFps.fps > 0.0:
                networkString = f'Network : {self.networkFps.fps:.2f} fps'
            frame = cv2.putText(frame, f'{captureString}'
                                       f'{displayString}'
                                       f'{networkString}',
                                (textPosX, textPosY),
                                cv2.FONT_HERSHEY_SIMPLEX, debugTextSize, NetCam.TEXT_COLOR, thickness,
                                cv2.LINE_AA)
            textPosY += int(40 * debugTextSize)
            frame = cv2.putText(frame, f'f : fullscreen | s : see stereo | F1 to F5 : change display',
                                (textPosX, textPosY), cv2.FONT_HERSHEY_SIMPLEX, debugTextSize, NetCam.TEXT_COLOR,
                                thickness,
                                cv2.LINE_AA)

        return frame

    def readLeft(self):
        frame = self.imgBuffer[self.imgBufferReady]
        if frame is None:
            return None  # Nothing to display
        if self.isStereoCam:
            # the Display is not in stereo, remove the half of the picture
            height, width = frame.shape[0],frame.shape[1]
            frame = frame[0:height, 0:width // 2]

        if self.displayDebug:
            frame = self.addDebugInfo(frame)
        return frame

    def readRight(self):
        frame = self.imgBuffer[self.imgBufferReady]
        if frame is None:
            return None  # Nothing to display
        if self.isStereoCam:
            # the Display is not in stereo, remove the half of the picture
            height, width = frame.shape[0],frame.shape[1]
            frame = frame[0:height, width // 2:width]

        if self.displayDebug:
            frame = self.addDebugInfo(frame)
        return frame

    def addDebugInfo(self, frame):
        self.displayFps.compute()
        height, width = frame.shape[0], frame.shape[1]
        debugTextSize = width / 1280
        thickness = 1 if width < 1280 else 2

        textPosX, textPosY = NetCam.TEXT_POSITION
        textPosX += int(40 * debugTextSize)
        textPosY += int(40 * debugTextSize)
        frame = cv2.putText(frame, f'Capture : {self.captureFps.getFps()} fps ({self.captureResolution}) | '
                                   f'Display : {self.displayFps.getFps()} fps ({self.displayResolution}) | '
                                   f'Network : {self.networkFps.getFps()} fps.',
                            (textPosX, textPosY),
                            cv2.FONT_HERSHEY_SIMPLEX, debugTextSize, NetCam.TEXT_COLOR, thickness,
                            cv2.LINE_AA)
        textPosY += int(40 * debugTextSize)
        frame = cv2.putText(frame, f'Source : {self.source}',
                            (textPosX, textPosY), cv2.FONT_HERSHEY_SIMPLEX, debugTextSize, NetCam.TEXT_COLOR,
                            thickness,
                            cv2.LINE_AA)
        if self.displayResolution:
            textPosY += int(40 * debugTextSize)
            frame = cv2.putText(frame,
                                f'f : fullscreen | s : see stereo | F1 to F5 : change display',
                                (textPosX, textPosY), cv2.FONT_HERSHEY_SIMPLEX, debugTextSize, NetCam.TEXT_COLOR,
                                thickness,
                                cv2.LINE_AA)
        return frame

    def display(self):

        if not self.displayResolution:
            # No Display was setup
            # self.console('You need to setup the display Resolution in NetCam constructor. ex : NetCam(display=\'VGA\'')
            # time(1)
            return
        if not self.isDisplayRunning:
            cv2.destroyAllWindows()
            return
        # Try to see if the window has been closed by clicking on the right upper cross
        try:
            isWindowClosed = cv2.getWindowProperty(self.windowName, 0)
            if isWindowClosed == -1:
                # the window has been closed
                self.console("Window was closed.")
                self.clearAll()
        except:
            self.console("Window was closed.")
            self.clearAll()
            return

        frame = self.imgBuffer[self.imgBufferReady]
        if frame is None:
            return  # Nothing to display

        if self.isStereoCam and not self.showStereo:
            # the Display is not in stereo, so remove the half of the picture
            height, width = frame.shape[0],frame.shape[1]
            frame = frame[0:height, 0:width // 2]

        if self.displayHeight != self.imgHeight:
            # Resize the picture for display purpose
            width = self.displayWidth if not self.showStereo else self.displayWidth * 2
            frame = cv2.resize(frame, (width, self.displayHeight))
        else:
            frame = np.copy(frame)

        if self.displayDebug:
            frame = self.addDebugInfo(frame)

        cv2.imshow(self.windowName, frame)
        self.listenKeyboard()

    def setDisplayResolution(self, resolution):
        if (resolution != None):
            self.displayResolution = resolution
            self.displayWidth, self.displayHeight = resolutionFinder(resolution)
            self.computeDisplayHeight()
            cv2.resizeWindow(self.windowName, self.displayWidth, self.displayHeight)
            self.console(f'Changed Display resolution for : {resolution} ({self.displayWidth} x {self.displayHeight})')

    def toggleFullScreen(self, isFullScreen=None):
        self.fullScreen = isFullScreen if isFullScreen is not None else not self.fullScreen
        if self.fullScreen:
            self.console(f'Toggle fullscreen')
            cv2.namedWindow(self.windowName, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            # cv2.setWindowProperty(self.windowName, cv2.WND_PROP_TOPMOST, 1.0)
        else:
            cv2.namedWindow(self.windowName, cv2.WINDOW_AUTOSIZE)
            cv2.setWindowProperty(self.windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.windowName, self.displayWidth, self.displayHeight)
            # cv2.setWindowProperty(self.windowName, cv2.WND_PROP_TOPMOST, 0.0)

    def toggleDisplayStereo(self, isShowStereo=None):
        self.showStereo = isShowStereo if isShowStereo is not None else not self.showStereo
        self.console(f'Show Stereo : {self.showStereo}')

    def listenKeyboard(self):
        key = cv2.waitKey(20)
        if key != -1:
            if key == ord('q'):  # q to quit
                self.clearAll()
            elif key == 35 or key == 47:  # Tilde to show debug
                self.toggleDebug()
            elif key == 190 or key == 122:  # F1
                self.setDisplayResolution('QVGA')
            elif key == 191 or key == 120:  # F2
                self.setDisplayResolution('VGA')
            elif key == 192 or key == 99:  # F3
                self.setDisplayResolution('HD')
            elif key == 193 or key == 118:  # F4
                self.setDisplayResolution('FHD')
            elif key == 194 or key == 96:  # F5
                self.setDisplayResolution('2K')
            elif key == ord('f'):  # F to toggle fullscreen
                self.toggleFullScreen()
            elif key == ord('s'):  # S to toggle display stereo
                self.toggleDisplayStereo()
            elif key == 27:  # Esc key was pressed,
                self.toggleFullScreen(False)
            else:
                print(f'Key pressed: {key}')

    def toggleDebug(self):
        self.displayDebug = not self.displayDebug
        self.console(f'Debugging is now {self.displayDebug}.')
        self.displayFps.initTime()
        self.captureFps.initTime()
        self.networkFps.initTime()

    def release(self):
        return self.clearAll()

    def clearAll(self):
        if self.commandSocket is not None:
            self.commandSocket.close()
            self.commandSocket = None

        if self.isNetworkRunning:
            self.console('Stopping Network...')
            self.isNetworkRunning = False
        time.sleep(0.1)
        if self.isDisplayRunning:
            self.console('Stopping Display...')
            self.isDisplayRunning = False
        time.sleep(0.1)
        if self.isCaptureRunning:
            self.console('Stopping Capture...')
            self.isCaptureRunning = False
        time.sleep(0.1)

        self.threadList = []
        zmqContext = zmq.Context.instance()
        zmqContext.term()
        time.sleep(0.5)
        self.isReleased = True
        self.console('Stopping Done.')

    def computeDisplayHeight(self):
        widthMultiplier = 2 if self.isStereoCam else 1

        if self.imgWidth and self.imgHeight and self.displayWidth:
            self.displayHeight = int(self.displayWidth / (self.imgWidth // widthMultiplier) * self.imgHeight)

    def invertVertical(self):
        self.flipVertical = not self.flipVertical

    def invertHorizontal(self):
        self.flipHorizontal = not self.flipHorizontal

    def isRunning(self):
        return self.isCaptureRunning or self.isDisplayRunning or self.isNetworkRunning

    def set(self, param, value):
        if self.videoStream:
            self.cameraSettingName = param
            self.cameraSettingValue = value
        elif self.isNetworkRunning:
            return self.sendCommand("set", param, value)

    def get(self, param):
        if param == "width":
            return self.imgWidth
        if param == "height":
            return self.imgHeight

        if self.videoStream:
            if param == 3 and self.imgWidth:
                return self.imgWidth
            return self.videoStream.get(param)
        elif self.isNetworkRunning:
            return self.sendCommand("get", param)
        return None

    def sendCommand(self, cmd, param, value=None):
        # send the get to the client
        url_publish = f"tcp://{self.ip_address}:{self.command_port}"
        data = json.dumps({'cmd': cmd, 'param': param, 'value': value})

        if self.commandSocket is None:
            context = zmq.Context()
            self.commandSocket = context.socket(zmq.PAIR)
            self.console(f"sending to : {url_publish}")
            self.commandSocket.connect(url_publish)
            self.console(f"connected to : {url_publish}...")
        self.commandSocket.send_string(data)
        self.console(f"data sent to : {url_publish}...")
        # self.console(f'Command {data} sent to {self.ip_address}...', 1)
        json_string = self.commandSocket.recv()
        self.console(f"response received from : {url_publish} : {json_string}")
        data = json.loads(json_string)
        result = data["result"]
        self.console(f"Received : {result}")
        return result

    def receiveCommand(self, json_string):
        data = json.loads(json_string)
        self.console(f"Command received : {data}", 2)

        command = data["cmd"] or None
        param = data["param"] or None
        value = data["value"] or None
        response = {'response': 'OK', 'result': None}
        if command == "get":
            response["result"] = self.get(param)
        elif command == "set":
            self.set(param, value)
            response["result"] = "DONE"

        self.console(f"Command result : {response}", 2)
        return json.dumps(response)

    def console(self, text, indentlevel=0):
        if self.consoleLog:
            output = time.strftime('%b %d at %H:%M:%S') + ' : '
            for count in range(0, indentlevel):
                output = output + '\t'
            print(f'{output}{text}')

    def showDebug(self):
        self.displayDebug = True

    def applyTransformation(self, frame, frameSecondary=[]):
        finalFrame = frame
        if self.flipVertical and self.flipHorizontal:
            frame = cv2.flip(frame, -1)
            if len(frameSecondary) > 0:
                frameSecondary = cv2.flip(frameSecondary, -1)
        elif self.flipVertical:
            frame = cv2.flip(frame, 0)
            if len(frameSecondary) > 0:
                frameSecondary = cv2.flip(frameSecondary, 0)
        elif self.flipHorizontal:
            frame = cv2.flip(frame, 1)
            if len(frameSecondary) > 0:
                frameSecondary = cv2.flip(frameSecondary, 1)
        if len(frameSecondary) > 0:
            finalFrame = np.concatenate((frame, frameSecondary), axis=1)
        else:
            finalFrame = frame

        if (len(finalFrame.shape) < 3):
            # It's a grayscale image, convert it to 3 channel gray scale
            finalFrame = cv2.merge([finalFrame,finalFrame,finalFrame])

        return finalFrame

    def renderWaitingMessage(self, frame):
        debugTextSize = 0.80
        thickness = 1 if self.imgHeight < 1280 else 2
        text = f'En attente du flux video source {self.source}  ({self.captureResolution})'
        textSize = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, debugTextSize, thickness)[0]
        textPosX = int((self.imgWidth - textSize[0]) / 2)
        textPosY = int((self.imgHeight - textSize[1]) / 2)
        frame = cv2.putText(frame, text, (textPosX, textPosY),
                            cv2.FONT_HERSHEY_SIMPLEX, debugTextSize, NetCam.TEXT_COLOR, thickness,
                            cv2.LINE_AA)
        return frame

    def checkIsStereoCam(self, isStereoCam=None):
        if isinstance(self.source, str) and ',' in self.source:
            self.isStereoCam = True
        else:
            self.isStereoCam = isStereoCam


def resolutionFinder(res, isstereocam=False):
    if res == None or res == 'Auto':
        return (None, None)
    widthMultiplier = 2 if isstereocam else 1
    switcher = {
        'QVGA': (320 * widthMultiplier, 240),
        'VGA': (640 * widthMultiplier, 480),
        'NANO': (800 * widthMultiplier, 480),
        'HD': (1280 * widthMultiplier, 720),
        'FHD': (1920 * widthMultiplier, 1080),
        '2K': (2048 * widthMultiplier, 1080),
        '5MP': (2592 * widthMultiplier, 1944),
        '2.2K': (2208 * widthMultiplier, 1242),

    }
    return switcher.get(res, (640 * widthMultiplier, 480))


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
