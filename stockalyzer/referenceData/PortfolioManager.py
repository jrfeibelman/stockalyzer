

from stockalyzer.common.Position import Position, PositionsDict, Side
from stockalyzer.core.Logger import Logger
from stockalyzer.engine.Module import Module, ModuleEnum
class PortfolioManager(Module):
    __slots__ = '_positionsPerAccount', '_printStatsActs', '_accountIdToCompIdDict', '_initialized'

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance._positionsPerAccount = dict()
            cls._instance._accountIdToCompIdDict = dict()
            cls._instance._printStatsActs = set()
        return cls._instance

    def __init__(self):
        super().__init__(ModuleEnum.PortfolioManager)

    def initialize(self, config):
        Logger().info("Initializing PortfolioManager")

        users_config = config.expand('Users')

        for e in users_config.getDict():
            portfolio_config = users_config.expand(e)
            accountId = portfolio_config.get_value('AccountId', '')

            if accountId == '':
                Logger().warn("Invalid Portfolio %s. Skipping" % (portfolio_config))
                continue

            Logger().debug("Adding Portfolio %s" % (portfolio_config))

            # TODO fetch current position data from ref data
            self._positionsPerAccount[accountId] = PositionsDict()

            self._accountIdToCompIdDict[accountId] = e

            if str(portfolio_config.get_value('PrintStats','false')).lower() == 'true':
                self._printStatsActs.add(accountId)

        self._initialized = True
        return self._initialized

    def start(self):
        if self._initialized:
            for accId in self._printStatsActs:
                Logger().debug("Initiating Print Timer for Account %s" % self._accountIdToCompIdDict[accId])
                # TODO leverage 60 second timer to print current state of portfolio

    def updatePosition(self, accountId, symbol: str, qty, price, side: Side):
        if accountId in self._positionsPerAccount:
            self._positionsPerAccount[accountId].updatePosition(symbol, qty, price, side)
        else:
            self._positionsPerAccount[accountId] = PositionsDict([Position(symbol, qty, price * qty, side)])

    def getPositionsPerAccountDict(self):
        return self._positionsPerAccount

    def getPositionsForAccount(self, accountId):
        return self._positionsPerAccount[accountId]

    def getPositionForSymbolWithAccount(self, accountId, symbol: str):
        return self._positionsPerAccount[accountId].getPositionForSymbol(symbol)