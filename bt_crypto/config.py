import configparser
import os 
import sys
CFG_FL="user.cfg"
ACCOUNT_SECTION="sub_account"
CEREBRO_SECTION="cerebro"
TURTLE_SECTION="turtle_strategy"

class Config:
    def __init__(self):
        config=configparser.ConfigParser()
        if not os.path.exists(CFG_FL):
            print('No user.cfg file found under current dictionary')
            sys.exit(1)
        else:
            config.read(CFG_FL)
        self.API_KEY=config.get(ACCOUNT_SECTION,"API_KEY")
        secret_path=config.get(ACCOUNT_SECTION,"SECRET_KEY")
        try:
            with open (secret_path,'r') as f:
                self.API_SECRET=f.read().strip()
        except FileNotFoundError:
            print('Private file path is not accessable, set private key to null')
            self.API_SECRET=''
        self.INIT_BAL=config.get(CEREBRO_SECTION,"init_cash")
        self.START_DATE=config.get(CEREBRO_SECTION,"start_date")
        self.END_DATE=config.get(CEREBRO_SECTION,"end_date")
        self.TOPEN_PERIOD=config.get(TURTLE_SECTION,"open_period")
        self.TCLOSE_PERIOD=config.get(TURTLE_SECTION,'close_period')
        self.CURR_PAIR=config.get(CEREBRO_SECTION,"trading_pair")

