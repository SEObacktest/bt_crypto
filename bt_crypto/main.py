from cerebro_controller import CerebroController
def main():
    cerebro_core=CerebroController()
    cerebro_core.cerebro_init()
    #cerebro_core.cerebro_starter()
    cerebro_core.all_strategy_runner()
main()
    

