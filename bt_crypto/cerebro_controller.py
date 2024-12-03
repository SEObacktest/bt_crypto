from strategies import get_strategy
import backtrader as bt
from config import Config
from api_manager import ApiManager
from datetime import datetime
from config import Config
from utils import load_configs
class CerebroController():
    def __init__(self):
        self.config=Config()
        self.cerebro=bt.Cerebro()
        self.client=ApiManager(self.config)
        self.bt_config=load_configs()
    def cerebro_init(self)->bt.Cerebro:
        cerebro=bt.Cerebro()
        cerebro.broker.setcash(float(self.config.INIT_BAL))
        cerebro.broker.setcommission(commission=float(self.config.COMMISSION))
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        return cerebro
    def cerebro_starter(self,strategy:bt.Strategy=None):
        str_strategy=self.config.CURR_STRATEGY
        strategy=get_strategy(self.config.CURR_STRATEGY)
        self.cerebro.addstrategy(strategy,position_to_balance=float(self.config.POSITION_TO_BALANCE))
        self.cerebro.run()
    def single_strategy_runner(self):
        pass
    def multiple_strategy_runner(self):
    def all_strategy_runner(self):
        pairs=self.bt_config.get_pairs()
        strategies=self.bt_config.get_strategies()
        for pair in pairs:
            pair_info=self.bt_config.get_pair_config(pair)
            start_date=pair_info['start_date']
            end_date=pair_info['end_date']
            interval=pair_info['interval']
            df=self.client.get_kline(
                symbol=pair,
                interval=interval,
                start_time=start_date,
                end_time=end_date,
            )
            start_date=datetime.strptime(pair_info['start_date'],'%Y%m%d')
            end_date=datetime.strptime(pair_info['end_date'],'%Y%m%d')
            data=bt.feeds.PandasData(dataname=df,datetime=None,open=-1,close=-1,low=-1,high=-1)
            for strategy in strategies:
                
                strategy_info=self.bt_config.get_strategy_config(strategy)
                origin_param=[param_config['start'] for param_config in strategy_info['parameters'].values()] 
                cerebro=self.cerebro_init()
                cerebro.adddata(data)
                strategy_module=get_strategy(strategy)
                if not strategy_info['opt_param']:
                    cerebro.addstrategy(strategy_module)
                    cerebro.run()
                else:
                    param_names = list(strategy_info['parameters'].keys())
                    param_values = [param_config['start'] for param_config in strategy_info['parameters'].values()]
                    params_dict = dict(zip(param_names, param_values))
#                    print(strategy_info)
#                    for param_config in strategy_info['parameters'].values():
#                        print(param_config)
                    param=self._create_strategy_params(strategy_info)
                    opt_strategy=cerebro.optstrategy(strategy_module,**param) 
                    cerebro.run(maxcpu=1)            
    def _create_strategy_params(self,strategy_info):
        params = {}
        for param_name, param_config in strategy_info['parameters'].items():
            # 对于浮点数参数，保持浮点数形式
            params[param_name] = range(
                param_config['start'], 
                param_config['end'] + param_config['step'],  # 加 step 是因为 range 是半开区间
                param_config['step']
            )
        return params
