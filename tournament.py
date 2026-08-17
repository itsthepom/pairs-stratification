###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# A set of classes to hold tournament data
###############################################################################
from __future__ import annotations
from tkinter import *
from datetime import datetime
from baseclasses import baseUIClass
from uiparts import UIParts
from stratify import getMasterpointRankIndex

class tournamentContent(baseUIClass):
    """ Runs that part of the UI that displays the currently selected tournament.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
    """
    def __init__(self, frame: Frame, memberDict: dict):
        self.frame = frame
        self.memberDict = memberDict
        if self.frame != None:
            self.resultsDescVar = StringVar()

    def construct(self, tourneybgnd: str):
        self.resultssInfoLabel1 = Label(self.frame, text="Selected Tournament:", font=("Segoe UI", 10), justify='left', bg=tourneybgnd)
        self.resultssInfoLabel1.grid(row=0, column=0, sticky=W, padx=10)
        self.resultsDescEntry = Entry(self.frame, textvariable=self.resultsDescVar, width=96, font=("Segoe UI", 10), bg=tourneybgnd)
        self.resultsDescEntry.config(state="readonly")
        self.resultsDescEntry.grid(row=0, column=1, sticky=W, pady=8)

    def clearContent(self):
        self.resultsDescEntry.destroy()
        self.resultssInfoLabel1.destroy()
    
    def setDescription(self, description: str):
        if self.frame != None:
            self.resultsDescVar.set(description)
    
    def getDescription(self):
        return self.resultsDescVar.get()

class matrixLine:
    """ A single line of a matrix

        Args:
            numBoards(int): Total number of boards in the tournament
    """
    def __init__(self, numBoards: int):
        self.score = [None for _ in range(numBoards)]
        self.total = 0

    def addResult(self, board: int, score: int):
        self.score[board - 1] = score
        self.total = self.total + score

class matrix:
    """ Board/Pair matrix. A collection of matrixLine instances

        Args:
            numBoards(int): Total number of boards in the tournament
    """
    def __init__(self, numBoards: int):
        self.numBoards = numBoards
        self.matrixLine = {}

    def addResult(self, pair: int, board: int, score: int):
        if pair not in self.matrixLine:
            self.matrixLine[pair] = matrixLine(self.numBoards)
        self.matrixLine[pair].addResult(board, score)
    
    def getMatrixLine(self, pair: int) -> matrixLine:
        if pair not in self.matrixLine:
            return None
        else:
            return self.matrixLine[pair]
    
class travellers:
    """ A collection of the travellers

        Args:
            tournamentData(tournament): tournamentData instance holding the event data.
            numBoards(int): Total number of boards in the tournament
    """
    def __init__(self, tournamentData: tournament, numBoards: int):
        self.travellers = [None for _ in range(numBoards)]
        self.tournament = tournamentData
        pass

    def addTraveller(self, eventType, board: any, pairData: any, resultsMatrix: matrix):
        newTraveller = self.tournament.readerClass.traveller(eventType, board, pairData, resultsMatrix)
        self.travellers[newTraveller.boardNum - 1] = newTraveller
        return newTraveller

class pairData:
    """ A pair playing in the event

        Args:
            isNS(bool): True for single winner events. False if E/W in two winner tournaments
    """
    def __init__(self, newresult, isNS: bool, masterpointsRankIndex: int):
        self.masterpoints = 0
        self.isNS = isNS
        self.awardedStratum = None
        self.stratPosition = None
        self.boardsPlayed = 0
        self.maxScore = 0
        self.sslams = 0
        self.gslams = 0
        self.scorecard = {}
        self.origmasterpointsRankIndex = self.masterpointsRankIndex = masterpointsRankIndex
        self.strat = 0
        self.result = newresult
    
    class scorecardLine:
        """ A line on the scorecard for a pair
        """
        def __init__(self):
            pass
        
        def add(self, eventType, topScore, isNS, newTravellerLine):
            self.isNS = isNS
            if isNS:
                self.versus = newTravellerLine.EWPair
                self.pts = newTravellerLine.score if eventType == 2 else newTravellerLine.NSScore
            else:
                self.versus = newTravellerLine.NSPair
                self.pts = newTravellerLine.score if eventType == 2 else newTravellerLine.EWScore
            if eventType == 0:
                self.percent = self.pts / topScore * 100.0
            self.contract = newTravellerLine.contract
            self.by = newTravellerLine.by
            self.lead = newTravellerLine.lead
            self.tricks = newTravellerLine.tricks
            if isinstance(newTravellerLine.score, int):
                if newTravellerLine.score >= 0:
                    self.plus = newTravellerLine.score
                    self.minus = ''
                else:
                    self.minus = newTravellerLine.score
                    self.plus = ''
            else:
                self.plus = newTravellerLine.score
                self.minus = ''

    def add(self, eventType, boardNum, topScore, isNS, newTravellerLine):
        if not boardNum in self.scorecard:
            self.scorecard[boardNum] = self.scorecardLine()
        self.scorecard[boardNum].add(eventType, topScore, isNS, newTravellerLine)
        self.maxScore = self.maxScore + topScore

class results:
    """ The event results. Binds together the rankings, pair data, travellers, results matrix and stratification levels.

        Args:
            tournamentData(tournament): tournamentData instance holding the event data.
    """
    def __init__(self, tournamentData: tournament):
        self.tournament = tournamentData
        self.overallRankings = [[ list(), list() ], [ list(), list() ], [ list(), list() ]]
        self.resultsMatrix = matrix(self.tournament.numBoards)
        self.travellerSet = travellers(tournamentData, tournamentData.numBoards)
        self.pairData = {}
        self.stratumLabels = [ None, None ]

    def addResult(self, pair: any):
        newResult = self.tournament.readerClass.resultLine(pair)
        orientation = 0
        if self.tournament.numWinners == 2 and newResult.orientation == 'EW':
            orientation = 1
        self.overallRankings[0][orientation].append(newResult)
        if newResult.pairNumber not in self.pairData:
            self.pairData[newResult.pairNumber] = pairData(newResult, 0 if orientation == 1 else 1, getMasterpointRankIndex(self.tournament.tournamentContentInst.memberDict, newResult.player1SBUNum, newResult.player2SBUNum))

    def addTraveller(self, eventType, board: any):
        newTraveller = self.travellerSet.addTraveller(self.tournament.eventType, board, self.pairData, self.resultsMatrix)
        for line in newTraveller.travellerLines:
            topScore = 0
            if eventType != 2:
                topScore = line.EWScore + line.NSScore
            if line.NSPair not in self.pairData:
                self.pairData[line.NSPair] = pairData(0)
            self.pairData[line.NSPair].add(eventType, newTraveller.boardNum, topScore, True, line)
            if line.EWPair not in self.pairData:
                self.pairData[line.EWPair] = pairData(1)
            self.pairData[line.EWPair].add(eventType, newTraveller.boardNum, topScore, False, line)
        return newTraveller

    def setPositions(self, eventType, direction: list):
        position = 1
        numEquals = 0
        for i in range(len(direction)):
            direction[i].positionNum = position
            if (i < (len(direction) - 1)):
                thisScore = direction[i].percentscore if eventType == 0 else direction[i].rawscore
                nextScore = direction[i + 1].percentscore if eventType == 0 else direction[i + 1].rawscore
            if (i < (len(direction) - 1)) and (thisScore == nextScore):
                direction[i].position = str(position) + "="
                numEquals = numEquals + 1
            else:
                if numEquals > 0:
                    direction[i].position = str(position) + "="
                else:
                    direction[i].position = str(position)
                position = position + numEquals + 1
                numEquals = 0

    def processResults(self, eventType):
        for direction in self.overallRankings[0]:
            for pairResult in direction:
                pairMatrixLine = self.resultsMatrix.getMatrixLine(pairResult.pairNumber)
                if pairMatrixLine == None:
                    pairResult.setScore(eventType, 0, 1)
                else:
                    pairResult.setScore(eventType, pairMatrixLine.total, self.pairData[pairResult.pairNumber].maxScore)
            direction.sort(reverse=True, key=lambda x : x.percentscore if eventType == 0 else x.rawscore)
            self.setPositions(eventType, direction)
        self.tournament.masterpointsObject.calculateMasterpoints(False)

class tournament:
    """ The tournament data. Commonly passed by reference into other classes.
        Holds non-score related information about the tournament and a results instance.

        Args:
            tournamentContentInst(tournamentContent): Tournament UI component instance.
            uiparts(UIParts): Holds the UI components.
    """
    def __init__(self, tournamentContentInst: tournamentContent, uiparts: UIParts):
        self.tournamentContentInst = tournamentContentInst
        self.readerClass = None
        self.clubName = None
        self.uiparts = uiparts
        self.lastPair = [ 0, 0 ]
        self.boardsPlayedUpdate = 0
        self.boardsPerRound = 0
        self.numLoads = 0

    def clearTournament(self):
        if self.uiparts.mainMenu != None:
            self.uiparts.mainMenu.enableMPFile(False)
            self.uiparts.mainMenu.enableMenuItems(False)
        self.clubName = self.clubID = self.eventID = self.eventType = None
        self.tournamentName = self.tournamentDate = self.eventRating = self.numPairs = None
        self.numEWPairs = self.numBoards = self.numWinners = None
        self.tournamentContentInst.setDescription('')

    def reset(self, clubName: str, clubID: str, eventID: str,
              eventType: str, description: str, date: str, eventRating: str,
              numPairs: int, numEWPairs: int, numBoards: int,
              numWinners: int, stratum1Label: str,
              stratum2Label: str):
        if self.uiparts.mainMenu != None:
            self.uiparts.mainMenu.enableMPFile(False)
            self.uiparts.mainMenu.enableMenuItems(True)

        # Store the fixed info about the tourney
        self.clubName = clubName
        self.clubID = clubID
        self.eventID = eventID
        self.eventType = eventType
        self.tournamentName = description
        self.tournamentDate = date
        self.eventRating = eventRating
        self.numPairs = numPairs
        self.numEWPairs = numEWPairs
        self.numBoards = numBoards
        self.numWinners = numWinners
        self.lastPair = [ 0, 0 ]
        self.boardsPlayedUpdate = 0
        self.boardsPerRound = 0
        self.numLoads = self.numLoads + 1
        # Create a results class instance to store the results in
        self.resultSet = results(self)
        if self.uiparts.options != None:
            self.resultSet.stratumLabels[0] = self.uiparts.options.config['stratum1threshold']
            self.resultSet.stratumLabels[1] = self.uiparts.options.config['stratum2threshold']
            # Push the stratum labels into the result set if already stratified
            self.preStratified = False
            if stratum1Label != None:
                self.preStratified = True
                self.resultSet.stratumLabels[0] = stratum1Label
                if stratum2Label != None:
                    self.resultSet.stratumLabels[1] = stratum2Label
                else:
                    self.resultSet.stratumLabels[1] = 'None'

    def addTraveller(self, board: any):
        newTraveller = self.resultSet.addTraveller(self.eventType, board)
        if (self.boardsPlayedUpdate == 0) or (self.boardsPlayedUpdate == 1 and (self.lastPair[0] == newTraveller.travellerLines[0].NSPair) and (self.lastPair[1] == newTraveller.travellerLines[0].EWPair)):
            self.boardsPlayedUpdate = 1
            self.boardsPerRound = self.boardsPerRound + 1
            self.lastPair = [newTraveller.travellerLines[0].NSPair, newTraveller.travellerLines[0].EWPair]
        else:
            self.boardsPlayedUpdate = 2

    def addResult(self, pair: any):
        self.resultSet.addResult(pair)

    def processResults(self):
        self.resultSet.processResults(self.eventType)
        if self.tournamentContentInst is not None:
            self.tournamentContentInst.setDescription(self.clubName + ' - ' + self.tournamentName + ' - ' + self.tournamentDate)

    def writeMPFile(self):
        self.readerClass.write(self.eventType, self.masterpointsObject.outputFileVar.get())

    def getOutputFilename(self):
        if self.clubName != None:
            dt = datetime.strptime(self.tournamentDate, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d") + '!' + self.tournamentName
        else:
            return ""
        
    def setMasterpointsObject(self, masterpointsObject):
        self.masterpointsObject = masterpointsObject