import backtrader as bt
from config import Config
from api_manager import ApiManager
from trade_enum import Side
from strategies import TurtleStrategy
from datetime import datetime
from config import Config
class CerebroController():
    def __init__(self,config:Config):
        self.config=Config()
        self.cerebro=bt.Cerebro()
        self.client=ApiManager(self.config)
    def cerebro_starter(self,strategy:bt.Strategy=None):
        df=self.client.get_kline(
        symbol=self.config.CURR_PAIR,
        interval='1d',
    )
        start_date=datetime.strptime(self.config.START_DATE,'%Y%m%d')
        end_date=datetime.strptime(self.config.END_DATE,'%Y%m%d')
        data=bt.feeds.PandasData(dataname=df,datetime=None,open=-1,close=-1,low=-1,high=-1,fromdate=start_date,todate=end_date)
        self.cerebro.adddata(data)
        self.cerebro.addstrategy(TurtleStrategy)
        self.cerebro.run()
