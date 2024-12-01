from config import Config
from cerebro_controller import CerebroController
def main():
    config=Config()
    cerebro_core=CerebroController(config)
    cerebro_core.cerebro_starter()
main()
    

