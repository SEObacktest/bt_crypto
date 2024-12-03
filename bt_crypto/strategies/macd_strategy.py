from strategies.base import BaseStrategy

class Strategy(BaseStrategy):
    params = (
        ('fast', 12),
        ('slow', 26),
        ('signal', 9)
             )
    def __init__(self):
        super().__init__()

        self.ema_fast_period = self.params.fast
        self.ema_slow_period = self.params.slow
        self.signal_period = self.params.signal

        self.ema_fast = None
        self.ema_slow = None
        self.macd = None
        self.signal = None

    def calculate_ema(self, prev_ema, price, period):
        if prev_ema is None:
            return price
        k = 2 / (period + 1)
        return (price * k) + (prev_ema * (1 - k))

    def next(self):
        price = self.data.close[0]

        self.ema_fast = self.calculate_ema(self.ema_fast, price, self.ema_fast_period)
        self.ema_slow = self.calculate_ema(self.ema_slow, price, self.ema_slow_period)

        self.macd = self.ema_fast - self.ema_slow
        self.signal = self.calculate_ema(self.signal, self.macd, self.signal_period)

        if not self.position:
            if self.macd > self.signal:
                self.order = self.buy()
        else:
            if self.macd < self.signal:
                self.order = self.sell()