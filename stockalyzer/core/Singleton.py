
from abc import ABCMeta


class SingletonMeta(object): # TODO use this / a variation of this to prevent __init__ from being repeatedly called when retrieving singleton instances
  _instances = {}
  def __new__(class_, *args, **kwargs):
    if class_ not in class_._instances:
        class_._instances[class_] = super(SingletonMeta, class_).__new__(class_, *args, **kwargs)
    return class_._instances[class_]

# class SingletonMeta(type):
#     def __init__(self, name, bases, mmbs):
#         super(SingletonMeta, self).__init__(name, bases, mmbs)
#         self._instance = super(SingletonMeta, self).__call__()

AbstractSingletonMeta = type('AbstractSingletonMeta', (ABCMeta, SingletonMeta), {})
