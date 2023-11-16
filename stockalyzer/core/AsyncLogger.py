
# TODO 2/22/23 Async Logger so main process not blocked by synchonous logger
# THIS IS NOT WORKING

class LogMessage:
    __slots__ = 'message', 'level'

    def __init__(self, msg, level):
        self.message = msg
        self.level = level

class AsyncLoggerThread(Thread):

    def __init__(self, logger, queue):
        print("GOT TYPE: %s "% type(logger))
        # print("GOT TYPE: %s "% type(queue))
        self.logger = logger
        self.queue = queue

    def run(self):
        while 1: # TODO instead of pushing LogMessage obj, use tuples !!!
            msg = self._queue.get()
            print("JRF received")
            if msg is None:
                print('ERROR - AsyncLogger exiting.')
                self._queue.task_done()
                break

            self.log(msg.message, msg.level)
            self._queue.task_done()

    def log(self, msg, level):
        if level == Logger.INFO:
            self.logger._info(msg)
        elif level == Logger.DEBUG:
            self.logger._debug(msg)
        elif level == Logger.WARN:
            self.logger._warn(msg)
        elif level == Logger.ERROR:
            self.logger._error(msg)
    
class AsyncLogger:
    # TODO make multiprocesser logger - info, debug, etc, funcs should write to a queue instead of directly to logs
    DEBUG = DEBUG
    INFO = INFO
    ERROR = ERROR
    WARN = WARN

    def __new__(cls, config=None, to_stdout=False):
        if not hasattr(cls, '_instance'):
            if config is None:
                print("ERROR: passed no config during initialization.")
                return None

            cls._instance = super().__new__(cls)
            from logging import getLogger
            cls.logger = getLogger()
            cls.formatter = Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt=("%Y%m%d %H:%M:%S.%f"))
            
            if to_stdout:
                cls.handler = StreamHandler(stdout)
            else:
                file = config.get_value('OutputFile', '%s/stockalyzer.log' % getcwd())
                cls.handler = FileHandler(file, mode='a')
                
            cls.level = get_log_level(config.get_value('Level', 'INFO'))
            cls.logger.setLevel(cls.level)
            cls.handler.setLevel(cls.level)
            cls.handler.setFormatter(cls.formatter)
            cls.logger.addHandler(cls.handler)
            cls.logQueue = Queue()
            cls.thread = AsyncLoggerThread(cls._instance, cls.logQueue)
            cls.info(cls, 'Initializing AsyncLogger')
     
        return cls._instance
    
    @classmethod
    def get_caller_details(self):
        call_stack = stack()
        try:
            calling_class = call_stack[2][0].f_locals["self"].__class__.__name__
        except KeyError:
            calling_class = call_stack[2][1].split('/')[-1]
            
        calling_method = call_stack[2][0].f_code.co_name
        line_number = call_stack[2][2]
        return "%s::%s::%s" % (calling_class, calling_method, line_number)
    
    def info(self, msg):
        self.logQueue.put(LogMessage(msg, Logger.INFO))

    def _info(self, msg):
        line = "[%s] - %s" % (self.get_caller_details(), msg)
        self.logger.info(line)
        # if self.level is Logger.DEBUG:
        #     print(line)
        #     stdout.flush()
    
    def debug(self, msg):
        self.logQueue.put(LogMessage(msg, Logger.DEBUG))

    def _debug(self, msg):
        line = "[%s] [%s] - %s" % (getpid(), self.get_caller_details(), msg)
        self.logger.debug(line)
        if self.level is Logger.DEBUG:
            print(line)
            stdout.flush()
            
    def warn(self, msg):
        self.logQueue.put(LogMessage(msg, Logger.WARN))

    def _warn(self, msg):
        line = "[%s] - %s" % (self.get_caller_details(), msg)
        self.logger.warning(line)
        if self.level is Logger.WARN or self.level is Logger.DEBUG:
            print(line)
            stdout.flush()
            
    def error(self, msg):
        self.logQueue.put(LogMessage(msg, Logger.ERROR))

def get_log_level(lvl: str):
    lvl = lvl.upper()
    if lvl == "INFO":
        return Logger.INFO
    elif lvl == "DEBUG":
        return Logger.DEBUG
    elif lvl == "WARN":
        return Logger.WARN
    elif lvl == "ERROR":
        return Logger.ERROR