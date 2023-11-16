# from abc import abstractmethod, ABCMeta
# from threading import Thread as PyThread
# from stockalyzer.core.Logger import Logger
# from os import getpid

# class Thread(PyThread, metaclass=ABCMeta):
    
#     def __init__(self):
#         super().__init__()

#     @abstractmethod
#     def join(self):
#         pass

#     @abstractmethod
#     def run(self):
#         Logger().info("Starting %s" % self)

#     def __str__(self):2
#         return "(%s) Process %s" % (self.__class__.__name__, getpid())