from typing import List,Dict,Optional
from binance.um_futures import UMFutures
import pandas as pd
from .config import Config
from datetime import datetime
from enum import Enum
class Side(Enum):
    BUY:str='BUY'
    SELL:str='SELL'

class ApiManager():
    def __init__(self,config:Config):
    	self.client=UMFutures(key=config.API_KEY,private_key=config.API_SECRET)
    def get_kline(self,symbol:str,interval:str,start_time:str=None,end_time:str=None)->pd.DataFrame:	
        if start_time:
            start_ms=int(datetime.strptime(start_time,"%Y%m%d").timestamp()*1000)
        if end_time:
            end_ms=int(datetime.strptime(end_time,"%Y%m%d").timestamp()*1000)
        result=self.client.klines(symbol=symbol,
        interval=interval,
        startTime=start_ms if start_time is not None else None,
        endTime=end_ms if end_time is not None else None,
        limit=1500)
        df=pd.DataFrame(result)
        df=df.iloc[:,0:6]
        df[0]=pd.to_datetime(df[0],unit='ms')
        for col in [1,2,3,4,5]:
            df[col]=df[col].astype(float)
        df=df.rename(columns={0:"datetime",1:"open",2:"high",3:"low",4:"close",5:"volume"}).set_index('datetime')
        return df
        print(df.header())
    def place_order(self,symbol:str,side:Side,order_type:str,quantity:float,price:float=None)->str:
        order_params={
                "symbol":symbol,
                "side":side.value,
                "quantity":quantity,
                "type":order_type,
                }
        if order_type!='MARKET':
            if price is None:
                raise ValueError('Price should be a valid value')
            order_params['price']=price
        response=self.client.new_order(**order_params)
        print(response)
    def close_all_positions(self):
        positions_amount={}
        all_open_positions:List[Dict]=self.get_open_positions()
        for position in all_open_positions:
            symbol=position['symbol']
            amount=float(position['positionAmt'])
            self.place_order(symbol=symbol,side=Side.BUY  if amount<0 else Side.SELL,order_type='MARKET',quantity=amount)
    def get_open_positions(self)->List[Dict]:
        account_info=self.client.account()
        print(account_info['positions'])
        return account_info['positions']
config=Config()
api_manager=ApiManager(config)
api_manager.get_kline('BTCUSDT','1d')
#api_manager.place_order('DOGEUSDT',Side.BUY,'MARKET',12)
#api_manager.get_open_positions()
#api_manager.close_all_positions()
