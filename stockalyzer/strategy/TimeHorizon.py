
from enum import Enum

class TimeHorizon(Enum):
    TimeHorizonStart = 0,
    Year1 = TimeHorizonStart,
    Month1 = 1,
    Day1 = 2,
    Hour1 = 3,
    Min15 = 4,
    Min1 = 5,
    Sec30 = 6,
    Sec10 = 7,
    Sec1 = 8,
    MDEventDriven = 9,
    TDEventDriven = 10,
    Undefined = 11,
    TimeHorizonSize = 12

    @classmethod
    def getTimeHorizon(cls, secType: str):
        if secType == "Year1": return TimeHorizon.Year1
        if secType == "Month1": return TimeHorizon.Month1
        if secType == "Day1": return TimeHorizon.Day1
        if secType == "Hour1": return TimeHorizon.Hour1
        if secType == "Min15": return TimeHorizon.Min15
        if secType == "Min1": return TimeHorizon.Min1
        if secType == "Sec30": return TimeHorizon.Sec30
        if secType == "Sec10": return TimeHorizon.Sec10
        if secType == "Sec1": return TimeHorizon.Sec1
        if secType == "MDEventDriven": return TimeHorizon.MDEventDriven
        if secType == "TDEventDriven": return TimeHorizon.TDEventDriven
        else: return TimeHorizon.Undefined

    @classmethod
    def getTimeHorizonStr(cls, secType) -> str:
        if secType == TimeHorizon.Year1: return "Year1"
        if secType == TimeHorizon.Month1: return "Month1"
        if secType == TimeHorizon.Day1: return "Day1"
        if secType == TimeHorizon.Hour1: return "Hour1"
        if secType == TimeHorizon.Min15: return "Min15"
        if secType == TimeHorizon.Min1: return "Min1"
        if secType == TimeHorizon.Sec30: return "Sec30"
        if secType == TimeHorizon.Sec10: return "Sec10"
        if secType == TimeHorizon.Sec1: return "Sec1"
        if secType == TimeHorizon.MDEventDriven: return "MDEventDriven"
        if secType == TimeHorizon.TDEventDriven: return "TDEventDriven"
        else: return "Undefined"

    @classmethod
    def getTimeHorizonNumInDays(cls, secType):
        if secType == TimeHorizon.Year1: return (365.0)
        if secType == TimeHorizon.Month1: return (12.0)
        if secType == TimeHorizon.Day1: return (1.0)
        if secType == TimeHorizon.Hour1: return (1.0/24.0)
        if secType == TimeHorizon.Min15: return (1.0/(24.0 * 4.0))
        if secType == TimeHorizon.Min1: return (1.0/(24.0 * 60.0))
        if secType == TimeHorizon.Sec30: return (1.0/(24.0 * 60.0 * 2.0))
        if secType == TimeHorizon.Sec10: return (1.0/(24.0 * 60.0 * 6.0))
        if secType == TimeHorizon.Sec1: return (1.0/(24.0 * 60.0 * 60.0))
        if secType == TimeHorizon.MDEventDriven: return (0.0)
        if secType == TimeHorizon.TDEventDriven: return (0.0)
        else: return (0.0)

    @classmethod
    def getTimeHorizonNumInSecs(cls, secType):
        if secType == TimeHorizon.Year1: return 365.0 * 12.0 * 24.0 * 60.0 * 60.0
        if secType == TimeHorizon.Month1: return 12.0 * 24.0 * 60.0 * 60.0
        if secType == TimeHorizon.Day1: return 24.0 * 60.0 * 60.0
        if secType == TimeHorizon.Hour1: return 60.0 * 60.0
        if secType == TimeHorizon.Min15: return 15.0 * 60.0
        if secType == TimeHorizon.Min1: return 60.0
        if secType == TimeHorizon.Sec30: return 30.0
        if secType == TimeHorizon.Sec10: return 10.0
        if secType == TimeHorizon.Sec1: return 1.0
        if secType == TimeHorizon.MDEventDriven: return 0.0
        if secType == TimeHorizon.TDEventDriven: return 0.0
        else: return 0.0
        
    @classmethod
    def getFullTimeHorizonDict(cls) -> dict:
        d = {}
        d[TimeHorizon.Year1] = set()
        d[TimeHorizon.Month1] = set()
        d[TimeHorizon.Day1] = set()
        d[TimeHorizon.Hour1] = set()
        d[TimeHorizon.Min15] = set()
        d[TimeHorizon.Min1] = set()
        d[TimeHorizon.Sec30] = set()
        d[TimeHorizon.Sec10] = set()
        d[TimeHorizon.Sec1] = set()
        d[TimeHorizon.MDEventDriven] = set()
        d[TimeHorizon.TDEventDriven] = set()
        return d