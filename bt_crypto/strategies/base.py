import backtrader as bt
import datetime
import os
class BaseStrategy(bt.Strategy):
    params=(
        ('position_to_balance',0.05),
        ('log_hidden',1)
    )
    def __init__(self):
        self.close_price=self.data.close
        self.open_price=self.data.open
        self.high_price=self.data_high
        self.low_price=self.data.low
        self.init_cash=None
    def log(self,txt,dt=None):
        dt=dt or self.datetime.date(0)
        print(f'{dt.isoformat()}:{txt}')
    def start(self):
        self.init_cash=self.broker.get_value()
    def stop(self):
        skip_attr=['notdefault','isdefault']
        param_info=[]
        for name in dir(self.p):
            if not name.startswith('_') and name not in skip_attr:
                value = getattr(self.p, name)
                param_info.append(f'{name}={value}')
        param_str=' ,'.join(param_info)
        print(f'Current Strategy:{self.__class__.__module__}')
        print(f'Param Info:{param_str}')
        print(f'Starting Portfolio Value:{self.init_cash:.2f}')
        print(f'Final Protfolio value:{self.broker.get_value():.2f}\n')
    def notify_order(self,order):
        if self.p.log_hidden:
            return
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
