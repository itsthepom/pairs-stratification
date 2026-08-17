###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# Abstract base classes
###############################################################################
from abc import ABC, abstractmethod

AppName="Pairs Stratification Program"
AppVersion="1.06"

class baseUIClass(ABC):
    @abstractmethod
    def construct(self, background:str) -> None:
        pass

    @abstractmethod
    def clearContent(self) -> None:
        pass

class resultsReader:
    class travellerBase(ABC):
        class travellerLineBase(ABC):
            @abstractmethod
            def __init__(self, line, boardNum, resultsMatrix):
                pass

        @abstractmethod
        def __init__(self, board, pairData, resultsMatrix):
            pass

    class resultLineBase(ABC):
        @abstractmethod
        def __init__(self, pair):
            pass
        
        @abstractmethod
        def setScore(self, total, topScore):
            pass