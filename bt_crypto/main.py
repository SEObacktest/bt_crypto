from cerebro_controller import CerebroController
from api_manager import ApiManager,Side
from config import Config
def main():
    cerebro_core=CerebroController()
    cerebro_core.cerebro_init()
    #cerebro_core.all_strategy_runner()
    cerebro_core.single_strategy_runner(curr_strategy='macd')
main()
    

