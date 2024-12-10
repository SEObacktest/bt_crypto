import backtrader as bt
from bt_crypto.strategies.base import BaseStrategy, TradingWay
import datetime


class Strategy(BaseStrategy):
    params = (
        ('ema_period', 20),
        ('atr_period', 14),
        ('atr_multiplier', 2),
    )

    def __init__(self):
        super().__init__()
        # Define the Keltner Channel indicators
        self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.upper_band = self.ema + self.params.atr_multiplier * self.atr
        self.lower_band = self.ema - self.params.atr_multiplier * self.atr

        # Define the average K-line indicators
        self.avg_high = bt.indicators.SimpleMovingAverage(self.high_price(0), period=self.params.ema_period)
        self.avg_low = bt.indicators.SimpleMovingAverage(self.low_price(0), period=self.params.ema_period)

        # Initialize order tracking
        self.order = None

    def next(self):
        # Entry logic when no position is held
        if self.broker.getposition(self.data).size == 0:
            if self.data.close > self.upper_band:
                self.order = self.buy(
                    exectype=bt.Order.Stop,
                    size=self.broker.get_value() * self.p.position_to_balance / self.data.close[0],
                    price=self.data.close[0],
                    valid=self.data.datetime.date(0) + datetime.timedelta(days=1)
                )

            elif self.data.close < self.lower_band:
                self.order = self.sell(
                    exectype=bt.Order.Stop,
                    size=self.broker.get_value() * self.p.position_to_balance / self.data.close[0],
                    price=self.data.close[0],
                    valid=self.data.datetime.date(0) + datetime.timedelta(days=1)
                )

        elif self.broker.getposition(self.data).size > 0:
            if self.data.close < self.avg_low:
                self.close()

        elif self.broker.getposition(self.data).size < 0:
            if self.data.close > self.avg_high:
                self.close()
