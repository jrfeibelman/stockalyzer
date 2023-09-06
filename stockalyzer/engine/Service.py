
from abc import abstractmethod, ABCMeta

class Service(metaclass=ABCMeta):

    def __init__(self, config):
        pass

    @abstractmethod
    def on_init(self):
        pass
        
    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_stop(self):
        pass