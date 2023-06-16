import cv2
import zmq
import base64
import numpy as np

context_receive = zmq.Context()
socket_receive = context_receive.socket(zmq.SUB)
socket_receive.bind('tcp://*:5555')
socket_receive.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))


context_stream = zmq.Context()
socket_stream = context_stream.socket(zmq.PUB)
socket_stream.connect('tcp://192.168.2.54:5556')



while True:
    
    try:
    
        frame = socket_receive.recv_string()
        img = base64.b64decode(frame)
#        source = cv2.imdecode(np.fromstring(frame, dtype=np.uint8), 1)
        npimg = np.fromstring(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        cv2.imshow("Stream", source)
        key=cv2.waitKey(1)
        
        
        
        
#        context_receive = zmq.Context()
#        self.socket_receive = context_receive.socket(zmq.SUB)
#        self.socket_receive.bind('tcp://*:'+str(ports[i]))
#        self.socket_receive.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))       
#
#        self.poller = zmq.Poller()
#        self.poller.register(self.socket_receive, zmq.POLLIN)       
                
        
   def read(self):

        evts=[]
        while len(evts)==0:
            evts = self.poller.poll(1)
        
    except KeyboardInterrupt:
            cv2.destroyAllWindows()
            break        
#        
        