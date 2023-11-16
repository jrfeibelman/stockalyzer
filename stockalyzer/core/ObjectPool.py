from numpy import uint32
from typing import TypeVar, Generic

T = TypeVar('T')

# TODO be careful with this file XXX - may make more sense to implement in Mojo
class ObjectPool(Generic[T]):
    _count : uint32 = 0
    _maxCount : uint32 = 0
    _numItems : uint32 = 0
    _useLock : bool = False
    _name : str = ""
    #_lock : SpinLock
    _pool : list[T] = list() # FIXME replace with SingleLinkedList (like C++ forwardList)
    _useTracking : bool = False
    _tracking : set[T] = set()

    def __init__(self, initNumItems : uint32, numItems : uint32, shouldUseLock : bool, name : str):
       self._count = 0
       self._maxCount = 0
       self._numItems = numItems
       self._useLock = shouldUseLock
       self._name = name
       self._useTracking = False

       self.replenish(initNumItems)

    def __del__(self):
        if not self._useLock:
            self.clear()
        else:
            # guard = SpinLockGuard(self._lock) # TODO aquire lock
            self.clear();

    def __clear__(self) -> None:
        # pools can be chained so let OS cleanup
        pass

    def replenish(self, numItems : uint32) -> None:
        print("Memory replenish starting for %s : adding num-max %s-%s" % (self._name, numItems, self._maxCount))
        for i in range(numItems):
            item = T()
            if self._useTracking:
                self._tracking.add(item)
            self._pool.add(item) # FIXME add to front of pool with single linked list
            self._count += 1

        if self._count >= self._maxCount:
            self._maxCount = self._count
        print("Memory replenish finished for %s : added num-max %s-%s" % (self._name, numItems, self._maxCount))

    def alloc(self) -> T:
        if not self._useLock:
            item = self.allocNoLock()
        else:
            # guard = SpinLockGuard(self._lock) # TODO aquire lock
            item = self.allocNoLock()

        if self._useTracking:
            self._tracking.remove(item)

        return item
    
    def allocNoLock(self) -> T:
        if len(self._pool) == 0:
            self.replenish(self._numItems)

        item = self._pool[0]
        self._pool.remove(0)
        self._count -= 1
        return item
    
    def get(self) -> T: # FIXME in future should return shared pointer in Mojo
        pass

    def free(self, item : T) -> bool:
        T.Clear()
        if not self._useLock:
            return self.freeNoLock(T)
        else:
            # guard = SpinLockGuard(self._lock) # TODO aquire lock
            return self.freeNoLock(T)

    def freeNoLock(self, item : T) -> bool:
        if self._useTracking:
            if item in self._tracking:
                return False
            self._tracking.add(item)

        self._pool.add(item) # FIXME in future add to front
        self._count += 1
        if self._count >= self._maxCount:
            self._maxCount = self._count
        return True

    def setTracking(self, flag : bool) -> None:
        self._useTracking = flag

    def size(self) -> uint32:
        return self._count
    
    def reserve(self, numItems : uint32) -> None:
        # guard = SpinLockGuard(self._lock) # TODO aquire lock
        for i in range(numItems - self._numItems):
            item = T()
            if self._useTracking:
                self._tracking.add(item)
            self._pool.add(item) # FIXME in future add to front
            self._count += 1

        if self._count >= self._maxCount:
            self._maxCount = self._count

        self._numItems = numItems