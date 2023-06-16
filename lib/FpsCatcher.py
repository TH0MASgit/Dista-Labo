################################################################################
##          Classe FpsCatcher
##      Calcul des FPS dans n'importe quel context
##  Author : J. Coupez
##  Copyright Dista
##  Date : 10/10/2020
##  Version : 1.0
##
## Utilisation :
## 1. Créer un objet FpsCatcher (avant un boucle par exemple):
##      self.displayFps = FpsCatcher()
## 2. En haut de votre boucle, calculez vos FPS :
##      while(True):
##           self.displayFps.compute()
##           ... Code de boucle
## 3. Vous pouvez ensuite recupere les FPS facilement
##           print(f'les fps : {self.displayFps.fps}')
##    ou en appelant print():
##           self.displayFps.print()

################################################################################

import time
from threading import Thread


class FpsCatcher:
    currentMilliTime = lambda: int(round(time.time() * 1000))

    def __init__(self, autoStart=True):
        self.initTime(autoStart)

    def __del__(self):
        self.release()

    def initTime(self, autoStart=True):
        self.currentFrame = 0
        self.fps = 0

        self.currentTime = 0
        self.tickCount = 0
        if autoStart:
            self.isRunning = True
            self.refreshThread = Thread(target=self.refreshFpsRunner, args=(), daemon=True)
            self.refreshThread.start()

    def refreshFpsRunner(self):
        while self.isRunning:
            now = FpsCatcher.currentMilliTime()
            diff = float(now - self.currentTime)
            if diff >= 1000:
                self.fps = self.tickCount / diff * 1000.0
                self.tickCount = 0
                self.currentTime = now
            time.sleep(1)

    def compute(self, timeDiff=None):
        self.tickCount += 1
        if timeDiff:
            self.currentTime += timeDiff
            if self.currentTime >= 1000:
                self.fps = self.tickCount / self.currentTime * 1000.0
                self.tickCount = 0
                self.currentTime = 0

    # now = FpsCatcher.currentMilliTime()
    # if now - self.currentTime >= 1000:
    #     self.currentTime = now
    #     self.fps = self.currentFrame
    #     self.currentFrame = 0
    # self.currentFrame += 1

    def release(self):
        self.isRunning = False

    def getFps(self):
        return round(self.fps, 1)

    def print(self):
        print(f'Images par seconde : {self.fps}fps')
