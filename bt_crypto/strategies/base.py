import backtrader as bt
import datetime
class BaseStrategy(bt.Strategy):
    def __init__(self):
        self.close_price=self.data.close
        self.open_price=self.data.open
        self.high_price=self.data_high
        self.low_price=self.data.low
    def log(self,txt,dt=None):
        dt=dt or self.datetime.date(0)
        print(f'{dt.isoformat()}:{txt}')
    def notify_order(self,order):
        if order.status is order.Submitted:
           #self.log('Order Submitted')
           pass
        if order.status is order.Accepted:
           # self.log('Order Accepted')
           pass
        if order.status is order.Completed:
            if order.isbuy():
                self.log(f'Buy executed:{order.executed.price:.2f} Cost:{order.executed.value:.2f}'
                         f' Commision:{order.executed.comm:.2f} Size:{order.executed.size}')
            if order.issell():
                    self.log(f'Sell executed:{order.executed.price:.2f} Cost:{order.executed.value:.2f}'
                             f' Commision:{order.executed.comm:.2f} Size:{order.executed.size}')
            self.log(f'Total balance:{self.broker.get_value()}')
            self.order=None
        elif order.status in [order.Canceled,order.Margin,order.Rejected]:
            self.log(f'Order rejected')
class TurtleStrategy(BaseStrategy):
    params=(
        ('open_period',20),
        ('close_period',10),
            )
    def __init__(self):
        super().__init__()
        self.DonchianH_entry=bt.indicators.Highest(self.high_price(0),period=self.params.open_period)
        self.DonchianL_exit=bt.indicators.Lowest(self.low_price(0),period=self.params.close_period)
        self.DonchianH_exit=bt.indicators.Highest(self.high_price(0),period=self.params.close_period)
        self.DonchianL_entry=bt.indicators.Lowest(self.low_price(0),period=self.params.open_period)
        self.order=None
    def notify_trade(self,trade):
        print('from trade:hi')
    def next(self):
        if self.broker.getposition(self.data).size == 0:
            self.order=self.buy(exectype=bt.Order.Stop,size=0.00001,price=self.DonchianH_entry[0],valid=self.data.datetime.date(0)+datetime.timedelta(days=1))
            self.order=self.sell(exectype=bt.Order.Stop,size=0.00001,price=self.DonchianL_entry[0],valid=self.data.datetime.date(0)+datetime.timedelta(days=1))
        if self.broker.getposition(self.data).size>0:
            if self.low_price[0]<self.DonchianL_exit[-1]:
                self.close()
        if self.broker.getposition(self.data).size<0:
            if self.high_price[0]>self.DonchianH_exit[-1]:
                self.close()
