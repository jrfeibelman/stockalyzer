from abc import abstractmethod, ABCMeta
from enum import Enum

class ModuleEnum(Enum):
    """
        - Class for registering valid components (modules) that can be added to a service (app)
        - Modules can force hard constraints that certain other components must also be loaded for it to work.
    """
    ModuleEnumStart = 0,
    StatsManager = ModuleEnumStart,
    ReferenceDataManager = 1,
    PortfolioManager = 2,
    Controls = 3,
    StrategyManager = 4,
    MDFeedManager = 5,
    MDFetcherManager = 6,
    ParameterManager = 7,
    Undefined = 8,
    ModuleEnumSize = 9

    @classmethod
    def getModuleEnum(cls, secType: str):
        if secType == "ReferenceDataManager": return ModuleEnum.ReferenceDataManager
        if secType == "PortfolioManager": return ModuleEnum.PortfolioManager
        if secType == "Controls": return ModuleEnum.Controls
        if secType == "StrategyManager": return ModuleEnum.StrategyManager
        if secType == "MDFeedManager": return ModuleEnum.MDFeedManager
        if secType == "MDFetcherManager": return ModuleEnum.MDFetcherManager
        if secType == "ParameterManager": return ModuleEnum.ParameterManager
        else: return ModuleEnum.Undefined

    @classmethod
    def getModuleEnumStr(cls, secType) -> str:
        if secType == ModuleEnum.ReferenceDataManager: return "ReferenceDataManager"
        if secType == ModuleEnum.PortfolioManager: return "PortfolioManager"
        if secType == ModuleEnum.Controls: return "Controls"
        if secType == ModuleEnum.StrategyManager: return "StrategyManager"
        if secType == ModuleEnum.MDFeedManager: return "MDFeedManager"
        if secType == ModuleEnum.MDFetcherManager: return "MDFetcherManager"
        if secType == ModuleEnum.ParameterManager: return "ParameterManager"
        else: return "Undefined"

    def __str__(self):
        return ModuleEnum.getModuleEnumStr(self)

class Module(metaclass=ABCMeta):

    __slots__ = '_module'

    def __init__(self, module):
        self._module = module

    @classmethod
    def new_instance(cls, module):
        mod = super().__new__(cls)
        mod._module = module
        return mod
        
    @abstractmethod
    def initialize(self): # TODO change naming to on_init
        pass
        
    # @abstractmethod
    # def on_start(self):
    #     pass

    # @abstractmethod
    # def on_stop(self):
    #     pass

    def get_module(self) -> ModuleEnum:
        return self._module


class InvalidModule(Module):

    def __init__(self):
        self._module = ModuleEnum.Undefined

    def initialize(self):
        raise Exception("Attempted to initialize an Undefined Enum")
        
    # def on_start(self):
    #     raise Exception("Attempted to start an Undefined Enum")

    # def on_stop(self):
    #     raise Exception("Attempted to stop an Undefined Enum")

class ModuleManager:

    __slots__ = '_dict', '_idx'

    def __init__(self):
        self._dict = dict()
        self._idx = -1

    def add(self, moduleEnum: ModuleEnum, module: Module) -> Module:
        if self.contains(moduleEnum):
            raise Exception("Module %s already exists" % moduleEnum)

        self._dict[moduleEnum] = module
        return module

    def get(self, module: ModuleEnum) -> Module: # Throws KeyError if module doesn't exist in dict
        return self._dict[module]

    def contains(self, module: ModuleEnum) -> bool:
        return module in self._dict

    def __iter__(self):
        self._idx = -1
        return iter(self._dict)

    def __next__(self):
        self._idx += 1
        if self._idx < len(self._dict):
            return self._dict[self._idx]
        else:
            raise StopIteration

    def __getitem__(self, key):
        if key in self._dict:
            return self._dict[key]
        else:
            errStr = "Key [%s] not found in %s@[%s]." % (key, self.__class__, hex(id(self)))
            raise KeyError(errStr)

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __contains__(self, key):
        return key in self._dict

    def __str__(self):
        return str(self._dict)