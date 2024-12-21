import logging
import os 
class Logger:
    def __init__(self):
        self.Logger=logging.getLogger('live_trade_logger')
        self.Logger.setLevel(logging.DEBUG)
        formatter=logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        fh=logging.FileHandler('logs/live_trade.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.Logger.addHandler(fh)

    def log(self,message,level="info"):
        if level=="info":
            self.Logger.info(message)
    def info(self,message):
        self.log(message,"info")

