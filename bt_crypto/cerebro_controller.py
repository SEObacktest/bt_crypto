from strategies import get_strategy
import backtrader as bt
from config import Config
from api_manager import ApiManager
from trade_enum import Side
from datetime import datetime
from config import Config
class CerebroController():
    def __init__(self):
        self.config=Config()
        self.cerebro=bt.Cerebro()
        self.client=ApiManager(self.config)
    def cerebro_init(self):
        self.cerebro.broker.setcash(float(self.config.INIT_BAL))
        self.cerebro.broker.setcommission(commission=float(self.config.COMMISSION))
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    def cerebro_starter(self,strategy:bt.Strategy=None):
        strategy=get_strategy(self.config.CURR_STRATEGY)
        df=self.client.get_kline(
        symbol=self.config.CURR_PAIR,
        interval='1d',
        end_time=self.config.END_DATE
    )
        start_date=datetime.strptime(self.config.START_DATE,'%Y%m%d')
        end_date=datetime.strptime(self.config.END_DATE,'%Y%m%d')
        data=bt.feeds.PandasData(dataname=df,datetime=None,open=-1,close=-1,low=-1,high=-1,fromdate=start_date,todate=end_date)
        self.cerebro.adddata(data)
        self.cerebro.addstrategy(strategy)
        self.cerebro.run()
