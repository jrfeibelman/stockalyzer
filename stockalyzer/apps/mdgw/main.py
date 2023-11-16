#!python

from stockalyzer.engine.StockalyzerService import StockalyzerService

if __name__ == "__main__":
    print("Initializing Stockalyzer Framework - MDGW")
    config = "config/mdgw1.yaml"
    service = StockalyzerService(config)
    service.on_init()
    service.on_start()
    # service.on_stop() TODO 