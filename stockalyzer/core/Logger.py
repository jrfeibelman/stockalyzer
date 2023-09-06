from logging import StreamHandler, FileHandler, Formatter, INFO, DEBUG, WARN, ERROR
from sys import stdout
from inspect import stack
from datetime import datetime
from pytz import reference, timezone
from os import getcwd, getpid

class Formatter(Formatter):
    timezone_mappings = {
        "CST" : "America/Chicago",
        "EST" : "America/New_York",
        "CDT" : "America/Chicago",
        "EDT" : "America/New_York",
    }
    
    def converter(self, timestamp):
        naive_dt = datetime.fromtimestamp(timestamp)
        local_tz = reference.LocalTimezone().tzname(naive_dt)
        tz = timezone(self.timezone_mappings[local_tz])
        return naive_dt.astimezone(tz)
    
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s
    
class Logger:
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
                data_file = config.get_value('DataFile', 'NONE')
                cls.handler = FileHandler(file, mode='a')
                
            cls.level = get_log_level(config.get_value('Level', 'INFO'))
            cls.logger.setLevel(cls.level)
            cls.handler.setLevel(cls.level)
            cls.handler.setFormatter(cls.formatter)
            cls.logger.addHandler(cls.handler)
            cls.info(cls, 'Initializing Logger')

            if data_file != 'NONE' and cls.level is DEBUG:
                cls.data_logger = getLogger()
                cls.data_handler = FileHandler(data_file, mode='w')
                cls.data_handler.setLevel(cls.level)
                cls.data_handler.setFormatter(cls.formatter)
                cls.data_logger.addHandler(cls.data_handler)
                cls.data_logger.setLevel(cls.level)

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
    
    def log_data(self, msg):
        line = "[%s] [%s] - %s" % (getpid(), self.get_caller_details(), msg)
        self.data_logger.info(line)

    def info(self, msg):
        line = "[%s] - %s" % (self.get_caller_details(), msg)
        self.logger.info(line)
        # if self.level is Logger.DEBUG:
        #     print(line)
        #     stdout.flush()
    
    def debug(self, msg):
        line = "[%s] [%s] - %s" % (getpid(), self.get_caller_details(), msg)
        self.logger.debug(line)
        if self.level is Logger.DEBUG:
            print(line)
            stdout.flush()
            
    def warn(self, msg):
        line = "[%s] - %s" % (self.get_caller_details(), msg)
        self.logger.warning(line)
        if self.level is Logger.WARN or self.level is Logger.DEBUG:
            print(line)
            stdout.flush()
            
    def error(self, msg):
        line = "[%s] - %s" % (self.get_caller_details(), msg)
        self.logger.error(line)
        if self.level is not Logger.INFO:
            print(line)
            stdout.flush()

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