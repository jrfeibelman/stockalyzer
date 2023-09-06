from pandas import DataFrame
from numpy import uint32

class Account:
    __slots__ = '_name','_data','_localId'

    def __init__(self, name: str, localId: uint32, data: DataFrame):
        self._name = name
        self._data = data
        self._localId = localId
