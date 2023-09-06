from asyncio.log import logger
from re import I
from stockalyzer.core.Logger import Logger
from csv import reader
from stockalyzer.referenceData.SecurityDefinition import InstrumentData, SecurityExchangeInfo
from inspect import signature
from numpy import array, uint32
from ordered_set import OrderedSet
from stockalyzer.engine.Module import Module, ModuleEnum
from stockalyzer.core.Singleton import AbstractSingletonMeta

class ReferenceDataManager(Module):

    __slots__ = '_insDataSetSortedOnLocalID', '_insDataDictBySymbol', '_insDataDictByCusip', '_isDynUniverse', '_staticUniverse', '_symbolsPerMarket', '_secExchInfoSetSortedOnLocalId', '_secExchInfoMicToInsDataSetDict', '_marketMicToSecExchInfoDict'
# '_secExchInfoSortedOnLocalId', '_secExchInfoToInsDataVecDict', '_marketMicToSecExchInfoDict'
    def __new__(cls):
        if cls.hasInstance(): # Experimented with new form of Singleton, Need something that can be inherited
            return cls._instance

        instance = super(ReferenceDataManager, cls).__new__(cls)
        instance._isDynUniverse = True
        instance._insDataSetSortedOnLocalID = OrderedSet() # TODO wanted OrderedSet but it had no sorting/reindexing ability
        instance._insDataDictByCusip = dict()
        instance._insDataDictBySymbol = dict()
        instance._secExchInfoSetSortedOnLocalId = OrderedSet()
        instance._marketMicToSecExchInfoDict = dict()
        instance._secExchInfoMicToInsDataSetDict = dict()
        instance._symbolsPerMarket = dict()
        instance._staticUniverse = [str]
        return instance

    def __init__(self):
        if self.hasInstance():
            return
    
        ReferenceDataManager._instance = self

        if super().__init__(ModuleEnum.ReferenceDataManager):
            return


    @classmethod
    def hasInstance(cls) -> bool:
        return hasattr(cls, '_instance')
   
    def initialize(self, config):
        markets_config = config.expand('Markets')
        self._staticUniverse = config.get_value('Universe', 'INVALID').split(',')

        if markets_config.isEmpty():
            Logger().error("No markets configured. Exiting.")
            return False

        for mkt in markets_config.getDict():
            Logger().info("Initializing market [%s]" % mkt)
            current_config = markets_config.expand(mkt)
            sec_def_file_str = current_config.get_value('SecurityDefinition', 'INVALID')

            if sec_def_file_str == 'INVALID':
                Logger().error("Unable to initialize Reference Data. No security definition file passed. Please use SecurityDefinition field in markets yaml.")
                return False

            self.readAndProcessSecDefCSV(sec_def_file_str, mkt)
            # set up feed ? mdm ?

        # TODO sort _insDataSetSortedOnLocalID by localID

        Logger().debug("Initializing ReferenceDataManager with isDynUniverse=[%s] and universe=%s" % (self._isDynUniverse, self._insDataSetSortedOnLocalID))
        return True

    def readAndProcessSecDefCSV(self, sec_def_file_str, assoc_mkt):
        self._symbolsPerMarket[assoc_mkt] = []
        # read sec def csv and populate cache
        with open(sec_def_file_str, 'r') as sec_def:
            csv_reader = reader(sec_def)
            header = next(csv_reader)
            for row in csv_reader:
                Logger().debug("Received Row %s for: %s" % (row[0], row))
                data_dict = dict(zip(header,row))
                symbol = data_dict["SYMBOL"]
                if self._isDynUniverse or symbol in self._staticUniverse:
                    Logger().info("Adding instrument %s : %s" % (assoc_mkt, symbol))
                    self.processInsRecord(data_dict, assoc_mkt)
                    self._symbolsPerMarket[assoc_mkt].append(symbol)

    def processInsRecord(self, data_dict, assoc_mkt):
        ins = InstrumentData.from_dict(data_dict)
        ins.setAssociatedMarket(assoc_mkt)

        secExchInfo = self.getSecExchInfoForMarketMic(ins._marketMic)
        if secExchInfo == None:
            secExchInfo = SecurityExchangeInfo(ins._marketMic)
            self._secExchInfoSetSortedOnLocalId.add(secExchInfo)
            self._marketMicToSecExchInfoDict[ins._marketMic] = secExchInfo

            if ins._marketMic not in self._secExchInfoMicToInsDataSetDict:
                self._secExchInfoMicToInsDataSetDict[ins._marketMic] = set()

            self._secExchInfoMicToInsDataSetDict[ins._marketMic].add(ins)
            
            Logger().info("Created SecExchInfo %s" % secExchInfo)
        else:
            self._secExchInfoMicToInsDataSetDict[ins._marketMic].add(ins)

        ins.setSecurityExchInfo(secExchInfo)
        self._insDataDictBySymbol[ins.getSymbol()] = ins
        self._insDataDictByCusip[ins.getCusip()] = ins
        self._insDataSetSortedOnLocalID.add(ins)

        Logger().info("Created InstrumentData %s" % ins)

    def getSecExchInfoForMarketMic(self, mic):
        if mic not in self._marketMicToSecExchInfoDict:
            return None
        return self._marketMicToSecExchInfoDict[mic]

    def getSecExchInfoSetSortedOnLocalID(self):
        return self._secExchInfoSetSortedOnLocalId

    def getSecExchInfoMicToInsDataSetDict(self):
        return self._secExchInfoMicToInsDataSetDict

    def getMarketMicToSecExchInfoDict(self):
        return self._marketMicToSecExchInfoDict

    def getInstrumentDataSetSortedOnLocalID(self):
        return self._insDataSetSortedOnLocalID

    def getInstrumentDataDictBySymbol(self):
        return self._insDataDictBySymbol

    def getInstrumentDataDictByCusip(self):
        return self._insDataDictByCusip

    def getSymbolList(self):
        #FIXME should store this result since frequently queried?
        return [ins_data.getSymbol() for ins_data in self.getInstrumentDataSetSortedOnLocalID()]

    def getSymbolListForAssociatedMarket(self, mkt):
        return self._symbolsPerMarket[mkt]
