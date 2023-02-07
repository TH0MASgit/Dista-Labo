################################################################################
##          Classe CountDown
##      Fait un compte a rebourd et indique quand le temps est écoulé
##  Author : J. Coupez
##  Date : 10/12/2020
##  Copyright Dista
##  Version : 1.0
##
## Utilisation :
## 1. Créer un objet CountDown (avant un boucle par exemple):
##      self.countdown = CountDown(3000)  # Create a 3 seconde countDown
## 2. En haut de votre boucle, calculez vos FPS :
##      self.countdown.start()
##      while(True):
##           ... Code de boucle
## 3. Vous pouvez ensuite savoir si le decompte est fini :
##           print(f'les fps : {self.countdown.isFinished}')
##    ou en appelant print():
##           self.displayFps.print()

################################################################################

import time
import math

from threading import Thread


class CountDown:
    currentMilliTime = lambda: int(round(time.time() * 1000))

    def __init__(self, countDown):
        self.countDown = countDown
        self.refreshThread = None
        self.isRunning = False
        self.resetCountDown()

    def resetCountDown(self):
        self.startTime = CountDown.currentMilliTime()
        self.remainingMilliTime = self.countDown * 1000
        self.isFinished = False
        self.isCanceled = False

    def start(self):
        if not self.isRunning:
            # The CountDown is not running : Start it
            if self.refreshThread and self.refreshThread.is_alive():
                self.isFinished = True
                time.sleep(0.01)
            self.resetCountDown()
            self.isRunning = True
            self.refreshThread = Thread(target=self.refreshThreadRunner, args=(), daemon=True)
            self.refreshThread.start()
        else:
            # The countDown Was already running, reinitialise it
            self.resetCountDown()

    def stop(self):
        self.isCanceled = True
        self.isFinished = False

    def refreshThreadRunner(self):
        while not self.isFinished and not self.isCanceled:
            now = CountDown.currentMilliTime()
            self.remainingMilliTime = self.countDown * 1000 - (now - self.startTime)
            # self.print()
            if self.remainingMilliTime <= 0:
                self.isFinished = True
                self.remainingMilliTime = 0
                break
            time.sleep(0.001)
        self.isRunning = False
        self.refreshThread = None

    def getRemainingSeconds(self):
        return math.ceil(self.remainingMilliTime / 1000) or 0

    def print(self):
        print(f'Decompte restant : {int(self.remainingMilliTime / 100) / 10.0} sec.')
