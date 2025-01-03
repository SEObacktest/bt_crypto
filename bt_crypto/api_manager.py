from .db import DataBase
from .logger import Logger
from typing import List,Dict,Optional
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from binance.um_futures import UMFutures
import pandas as pd
from .config import Config
from datetime import datetime,timedelta
from enum import Enum
from .utils import load_configs
class Side(Enum):
    BUY:str='BUY'
    SELL:str='SELL'
class ApiManager():
    def __init__(self,config:Config,db:DataBase):
        self.client=UMFutures(key=config.API_KEY,private_key=config.API_SECRET)
        self.bt_config=load_configs()
        self.logger=Logger('api')
        self.db=db
    def get_kline(self,symbol:str,interval:str,start_time:str=None,end_time:str=None)->pd.DataFrame:	
        end_ms=None
        if start_time:
            if not self.bt_config.get_basic_setting()['livetrade']:
                start_ms=int(datetime.strptime(start_time,"%Y%m%d").timestamp()*1000)
            else:
                current_ms=int(datetime.utcnow().timestamp()*1000)
                time_multiplier=1
                if self.bt_config.get_pair_config(symbol)['interval']=='5m':
                    time_multiplier=5
                if self.bt_config.get_pair_config(symbol)['interval']=='1d':
                    time_multiplier=1440
                if self.bt_config.get_pair_config(symbol)['interval']=='1h':
                    time_multiplier=60
                if self.bt_config.get_pair_config(symbol)['interval']=='4h':
                    time_multiplier=240
                start_ms=int((datetime.utcnow()-timedelta(minutes=40*time_multiplier)).timestamp()*1000)
        if end_time:
            if not self.bt_config.get_basic_setting()['livetrade']:
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
    def place_order(self,symbol:str,side:Side,order_type:str,quantity:float,price:float=None,**args)->str:
        order_params={
                "symbol":symbol,
                "side":side.value,
                "quantity":quantity,
                "type":order_type,
                **args
                }
        if order_type!='MARKET':
            if price is None:
                raise ValueError('Price should be a valid value')
            order_params['price']=price
        response=self.client.new_order(**order_params)
        db.add_order(
            order_id=response['orderId'],
            symbol=response['symbol'],
            amount=response['origQty'],order_state='FILLED' if order_type=='MARKET' else response['status'],
            place_time=response['updateTime'] 
            )
        print(response)
        return response
    def close_all_positions(self):
        positions_amount={}
        all_open_positions:List[Dict]=self.get_open_positions()
        for position in all_open_positions:
            symbol=position['symbol']
            amount=float(position['positionAmt'])
            self.place_order(symbol=symbol,side=Side.BUY  if amount<0 else Side.SELL,order_type='MARKET',quantity=amount)
    def close_certain_position(self,symbol:str):
        if self.get_certain_position(symbol) is None:
            print('you dont have any position')
            return
        amount=float(self.get_certain_position(symbol))
        self.place_order(symbol=symbol,side=Side.BUY  if amount<0 else Side.SELL,order_type='MARKET',quantity=abs(amount),reduceOnly='true')
    def close_then_place(self,symbol:str,side:Side,order_type:str,quantity:float,price:float=None)->str:
        position=self.get_certain_position(symbol)
        if position is None:
            print('No position close, put order directly')
            result=self.place_order(symbol=symbol,side=side,order_type='MARKET',quantity=quantity)
        else:
            if position > 0 and side==Side.BUY:
                print('you have already hold long position')
                return
            if position>0 and side==Side.SELL:
                result=self.place_order(symbol=symbol,side=side,order_type='MARKET',quantity=position+quantity)
            if position < 0 and side==Side.SELL:
                print('You have already hold short position')
                return 
            if position <0 and side==Side.BUY:
                result=self.place_order(symbol=symbol,side=side,order_type='MARKET',quantity=abs(position)+quantity)
        return result
    def get_open_positions(self)->List[Dict]:
        account_info=self.client.account()
        #print(account_info['positions'])
        return account_info['positions']
    def get_certain_position(self,symbol:str)->Optional[Dict]:
        positions=self.get_open_positions()
        count=0
        for position in positions:
            if position['symbol'] ==symbol:
                count+=1
                print(position['positionAmt'])
                return float(position['positionAmt'])
        else:
            print('No position for {symbol}')
            return None
    def get_balance(self)->float:
        balance=float(self.client.account()['totalWalletBalance'])
        return balance
    def cancel_order(self,symbol:str):
        #This is the function cancelling order for specific symbol
        response=self.client.cancel_open_orders(symbol)
        return response
    def get_current_order(self,db:DataBase,symbol:str=None):
        response=self.client.get_orders() 
        print(response)
    def get_order(self,orderId:int,symbol:str):
        result=self.client.query_order(symbol,orderId)
        return result
    def order_chaser(self):
        try:
            orders = self.db.get_live_orders()
            for order in orders:
                result=self.get_order(order['symbol'],order['order_id'])
            return orders
        except Exception as e:
            self.logger.error(f"获取订单时发生错误: {str(e)}")
            return []
if __name__=='__main__':
    print('hi')
    config=Config()
    logger=Logger('database')
    db=DataBase(logger)
    client=ApiManager(config,db)
    #client.place_order('DOGEUSDT',Side.SELL,'LIMIT',17,1,timeinforce='GTC')
    #result=client.get_order(61675559014,'DOGEUSDT')
    result=client.order_chaser()
    print(result)