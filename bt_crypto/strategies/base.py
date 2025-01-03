import time
from enum import Enum
from typing import Dict 
import backtrader as bt
import datetime
import os
from bt_crypto.api_manager import ApiManager,Side
from bt_crypto.config import Config
from bt_crypto.logger import Logger
from bt_crypto.db import DataBase
class TradingWay(Enum):
    CLOSE=0,
    LONG=1,
    SHORT=2,
    CLOSE_THEN_LONG=3,
    CLOSE_THEN_SHORT=4
TradingSignal = Dict[str, Enum]
class BaseStrategy(bt.Strategy):
    params=(
        ('position_to_balance',0.05),
        ('log_hidden',1),
        ('pair','DOGEUSDT'),
        ('livetrade',False)
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
        self.open_amount=None
        self.trade_logger=Logger(f'live_trading:{self.__module__}')
        self.db_logger=Logger('database')
        self.bt_logger=Logger('backtest')
        self.db=DataBase(self.db_logger)
    def log(self,txt,dt=None):
        dt=dt or self.datetime.date(0)
        print(f'{dt.isoformat()}:{txt}')
    def start(self):
        self.init_cash=self.broker.get_value()
        if(self.p.livetrade):
            print("You are under live trading")
            balance=self.client.get_balance()
            self.open_amount=balance*self.p.position_to_balance
    def stop(self):
        skip_attr=['notdefault','isdefault']
        param_info=[]
        for name in dir(self.p):
            if not name.startswith('_') and name not in skip_attr:
                value = getattr(self.p, name)
                param_info.append(f'{name}={value}')
        param_str=' ,'.join(param_info)
        if not self.p.livetrade:
            print(f'Current Strategy:{self.__class__.__module__}')
            print(f'Param Info:{param_str}')
            print(f'Starting Portfolio Value:{self.init_cash:.2f}')
            print(f'Final Protfolio value:{self.broker.get_value():.2f}\n')
        else:
            print(f'date:{bt.num2date(self.datetime[0]).strftime("%Y-%m-%d %H:%M:%S")}')
            print(f'Latest price={self.close_price[0]}')
            print(bt.num2date(self.datetime[0]).timestamp())
            #在K线结束前的20%时间确定交易信号
    #            interval=bt.num2date(self.datetime[0]).timestamp()-bt.num2date(self.datetime[-1]).timestamp()
    #            order_timestamp=bt.num2date(self.datetime[0]).timestamp()+interval*0.8
    #            datetime_obj=datetime.datetime.fromtimestamp(order_timestamp)
    #            now=datetime.datetime.utcnow().timestamp()
    #            now_obj=datetime.datetime.fromtimestamp(now)
    #            sleep_time=int(order_timestamp-now)
    #            if sleep_time<0:
    #                new_sleep_time=bt.num2date(self.datetime[0]).timestamp()+interval
    #                print(f'start to sleep for next bar:{new_sleep_time}')
    #                time.sleep(new_sleep_time-now)
    #                new_now=datetime.datetime.utcnow()
    #                new_now_str = new_now.strftime("%Y-%m-%d %H:%M:%S")
    #                print(new_now)
    #                print(f'sleep finished')
    #            print('start to sleep')
    #            time.sleep(sleep_time)
    #            print('sleep finished!')
            self.trading_signal=self.gen_trading_signal()
            self.trading_signal=TradingWay.CLOSE
            self.client.get_certain_position(self.p.pair)
            open_quantity=int(self.open_amount/self.close_price[0])
            if self.trading_signal is None:
                print('no signal detected')
            if self.trading_signal == TradingWay.CLOSE:
                self.client.close_certain_position(self.p.pair)
            if self.trading_signal==TradingWay.LONG:
                print(self.close_price[0])
                print(int(self.open_amount/self.close_price[0]))
                result=self.client.place_order(symbol=self.p.pair,
                                    side=Side.BUY,
                                    order_type='MARKET',
                                    price=self.close_price[0])
                if result is not None:
                    self.logger.info(f'做多信号出现，品种：{self.p.pair},数量：{open_quantity}')
            if self.trading_signal==TradingWay.SHORT:
                self.logger.info(f'做空信号出现，品种：{self.p.pair},数量：{open_quantity}')
                result=self.client.place_order(symbol=self.p.pair,
                                    side=Side.SELL,
                                    order_type='MARKET',
                                    quantity=int(self.open_amount/self.close_price[0]))
            if self.trading_signal==TradingWay.CLOSE_THEN_SHORT:
                result=self.client.close_then_place(symbol=self.p.pair,
                                side=Side.SELL,
                                order_type='MARKET',
                                quantity=int(self.open_amount/self.close_price[0]))
                if result is not None:
                    direction='多' if float(result.get("origQty"))>0 else "空"
                    self.logger.info(f'反转信号出现：平多并做空，品种：{self.p.pair},数量：{abs(float(result.get("origQty")))},方向:{direction}')
            if self.trading_signal==TradingWay.CLOSE_THEN_LONG:
                result=self.client.close_then_place(symbol=self.p.pair,
                                side=Side.BUY,
                                order_type='MARKET',
                                quantity=int(self.open_amount/self.close_price[0]))
                if result is not None:
                    direction='多' if float(result.get("origQty"))>0 else "空"
                    self.logger.info(f'反转信号出现：平空并做多，品种：{self.p.pair},数量：{abs(float(result.get("origQty")))},方向:{direction}')
                            
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
