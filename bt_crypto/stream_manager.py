from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from binance.um_futures import UMFutures
from .config import Config
import threading
class StreamManager:
    def __init__(self,config:Config):
        self.client=UMFutures(key=config.API_KEY,private_key=config.API_SECRET)
        self.ws_client=UMFuturesWebsocketClient(on_message=self.message_handler)
    def message_handler(self,_, message):
        print(message)
    def get_user_data(self):
        response=self.client.new_listen_key()
        print(response)
        self.ws_client.user_data(
            listen_key=response['listenKey'],
            id=1,
        )
    def get_price(self,symbol=None):
        self.ws_client.kline(symbol='btcusdt',id=12,interval='1h')
