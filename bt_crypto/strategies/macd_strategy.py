import backtrader as bt
import datetime
from strategies.base import BaseStrategy
class Strategy(BaseStrategy):
    params = (
        ('fast', 12),
        ('slow', 26),
        ('signal', 9),
             )
    def __init__(self):
        super().__init__()
        self.macd=bt.indicators.MACD(
                self.close_price,
                period_me1=self.p.fast,
                period_me2=self.p.slow,
                period_signal=self.p.signal,
        )
        self.crossover=bt.indicators.CrossOver(self.macd.macd,self.macd.signal)
        self.sizer=bt.sizers.PercentSizer(percents=20)
    def next(self):
        if self.broker.getposition(self.data).size==0:
            if self.crossover[0] >0:
                self.buy(
                    size=self.broker.get_value()*self.p.position_to_balance/self.close_price[0]
                    )
            if self.crossover[0]<0:
                self.sell(
                    size=self.broker.get_value()*self.p.position_to_balance/self.close_price[0]
                    )
        else:
            if self.broker.getposition(self.data).size<0:
                if self.crossover[0]>0:
                    self.close()
                    self.buy(
                        size=self.broker.get_value()*self.p.position_to_balance/self.close_price[0]
                    )
            else:
                if self.crossover[0]<0:
                    self.close()
                    self.sell(
                        size=self.broker.get_value()*self.p.position_to_balance/self.close_price[0]
                    )
