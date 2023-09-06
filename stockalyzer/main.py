#!python

from stockalyzer.engine.StockalyzerService import StockalyzerService
from sys import argv, exit

if __name__ == "__main__":
    print("Initializing Stockalyzer Framework")

    if len(argv) > 2:
        print("Invalid program arguments. Use command: python -m stockalyzer.main <path/to/config>")
        exit(1)

    if len(argv) == 1:
        print("No config specified. Defaulting to config/stockalyzer1.yaml")
        config = 'config/stockalyzer1.yaml'
    else:
        config = argv[1]

    service = StockalyzerService(config)
    service.on_init()
    service.on_start()
    # service.on_stop() TODO 

