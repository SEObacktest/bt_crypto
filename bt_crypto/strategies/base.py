from enum import Enum
from typing import Dict 
import backtrader as bt
import datetime
import os
from bt_crypto.api_manager import ApiManager,Side
from bt_crypto.config import Config
class TradingWay(Enum):
    CLOSE_ONLY=0,
    OPEN=1,
    CLOSE_THEN_OPEN=2
TradingSignal = Dict[str, Enum]
class BaseStrategy(bt.Strategy):
    params=(
        ('position_to_balance',0.05),
        ('log_hidden',1)
    )
    def __init__(self):
        config=Config()
        self.client=ApiManager(config)
        self.volume=self.data.volume
        self.close_price=self.data.close
        self.open_price=self.data.open
        self.high_price=self.data_high
        self.low_price=self.data.low
        self.init_cash=None
        self.trading_signal:Dict=None
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
        if self.trading_signal is  not None:
            self.client.place_order('DOGEUSDT',Side.SELL,'MARKET',12)
        else:
            print('No trading signal detected')
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
def gen_trading_signal(self)-> TradingSignal:
    pass
