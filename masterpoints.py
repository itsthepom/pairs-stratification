###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# Class to assign masterpoints and provide the UI for creating a new USEBIO
###############################################################################
import ttkbootstrap as tb
from baseclasses import baseUIClass
from uiparts import UIParts
import filehandling
import math

# From the SBU MP handbook. These are the lower limits of pairs for one and two winner events
# and the top award for that number of pairs
OneWinnerPairsNumbers =     (  6,  9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48 )
LocalOneWinnerPairsPoints = ( 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96 )
TwoWinnerTableNumbers =     (  3,  6,  9, 12, 15, 18, 21, 24, 27, 30 )
LocalTwoWinnerTablePoints = ( 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 )

CompleteColor = "#44880C"

class masterpoints(baseUIClass):
    """ Runs the UI for creating a new USEBIO and assigns masterpoints to pairs in an event

        Args:
            frame(Frame): tkinter Frame to display the UI in.
            tournamentData(tournament): tournamentData instance holding the event data.
            uiparts(UIParts): Holds the UI components.
    """
    def __init__(self, frame: tb.Frame, tournamentData, uiparts: UIParts):
        self.frame = frame
        self.tournamentData = tournamentData
        tournamentData.setMasterpointsObject(self)
        self.uiparts = uiparts
        uiparts.masterpointsResultsDisplay = self
        self.numLoads = 0
        if frame is not None:
            self.outputFileVar = tb.StringVar()
            self.outputFileVar.trace_add("write", self.fileSelected)
            self.outputMatrix = tb.BooleanVar()

    def getName(self):
        return 'write'
    
    def construct(self, pagebgnd: str):
        self.pagebgnd = pagebgnd
        if self.numLoads != self.tournamentData.numLoads:
            self.numLoads = self.tournamentData.numLoads
            outputFilename = self.tournamentData.getOutputFilename()
            if len(outputFilename) > 0:
                self.outputFileVar.set(self.uiparts.options.getDirectory('outputsdir') + self.uiparts.options.getDirectory('masterpointsdir') + self.tournamentData.getOutputFilename() + ".xml")
            else:
                self.outputFileVar.set("")

        self.labels = []
        label = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        label.grid(row=0, column=0, columnspan=2, sticky="nw")
        self.labels.append(label)

        label = tb.Label(self.frame, text="Select the new USEBIO format results file to be created.", font=("Arial", 10, "bold"), justify='left')
        label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)

        label = tb.Label(self.frame, text="This file can be uploaded to MEMPAD.", font=("Arial", 10), justify='left')
        label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)

        label = tb.Button(self.frame, text="Browse", bootstyle="primary", command=lambda: self.pickInputFile())
        label.grid(row=3, column=0, pady=10, padx=20, sticky="w")
        self.labels.append(label)

        label = tb.Entry(self.frame, textvariable=self.outputFileVar, width=95, font=("Arial", 10))
        label.grid(row=3, column=0, sticky="w", padx=100)
        self.labels.append(label)

        label = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        label.grid(row=4, column=0, columnspan=2, sticky="nw")
        self.labels.append(label)

        self.createButton = tb.Button(self.frame, text="Create", bootstyle="primary", state="disabled", command=lambda: self.writeMasterpointsFile())
        self.createButton.grid(row=7, column=0, sticky="w", padx=20, pady=10)
        self.labels.append(self.createButton)

        label = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        label.grid(row=8, column=0, columnspan=2, sticky="nw")
        self.labels.append(label)

        self.completeLabel = tb.Label(self.frame, text="", font=("Arial", 10, "bold"), foreground=CompleteColor, justify='left')
        self.completeLabel.grid(row=9, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(self.completeLabel)

        label = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        label.grid(row=10, column=0, columnspan=2, sticky="nw", padx=420, pady=250)
        self.labels.append(label)

        self.fileSelected('', '', '')
        
    def clearContent(self):
        """Clears all widgets inside self.frame without destroying self.frame itself."""
        if hasattr(self, 'frame') and self.frame:
            for widget in self.frame.winfo_children():
                widget.destroy()
        self.labels = []

    def pickInputFile(self):
        filename = filehandling.openResultsFile(self.uiparts.options.getDirectory("outputsdir") + self.uiparts.options.config["masterpointsdir"], True)
        if len(filename) > 0:
            self.outputFileVar.set(filename)

    def fileSelected(self, name, index, mode):
        try:
            self.completeLabel.config(text="")
            if len(self.outputFileVar.get()) > 0:
                self.createButton.config(state="normal")
            else:
                self.createButton.config(state="disabled")
        except:
            pass
   
    def writeMasterpointsFile(self):
        self.tournamentData.writeMPFile()
        self.completeLabel.config(text="USEBIO file generation complete.")
        pass

    def calculateMPs(self, StratificationGood: bool):
        """ Awards masterpoints to an event.

            Args:
                NSstratificationGood(bool): True if the NS results stratified OK.
                EWstratificationGood(bool): True if the EW results stratified OK.
        """

        # Calculate the masterpoints for a particular stratum.
        def awardMPs(stratumNumber: int, numStrata: int):
            """ Helper to awards masterpoints to a stratum.

                Args:
                    stratumNumber(int): Stratum number (zero based) to process.
                    numStrata(int): Total number of strata in the results.
            """

            # Helper used for both one and two winner events
            def calcMPs(stratumRankings, maxAward, numAwards):
                # Loop through the results and overwrite the masterpoints with the new values.
                # Once we run out of awards, the masterpoints get set to zero for the remainder
                award = maxAward
                awardDelta = max(int(maxAward / numAwards), 0)
                i = 0
                while i < len(stratumRankings):
                    # How many masterpoints to award depends on whether this is a tie
                    numShared = 1
                    thisAward = award
                    for j in range(i, len(stratumRankings) - 1):
                        if stratumRankings[j].position == stratumRankings[j + 1].position:
                            if award - awardDelta > 0:
                                # Not the last award
                                thisAward = thisAward + max(int(thisAward - numShared * awardDelta), 0)
                            numShared = numShared + 1
                        else:
                            break
                    if award - awardDelta > 0:
                        thisAward = math.ceil(thisAward / numShared)
                    # thisAward is the award for this pair and any tied pairs
                    for j in range(numShared):
                        maxMPs = self.tournamentData.resultSet.pairData[stratumRankings[i + j].pairNumber].masterpoints
                        if thisAward > maxMPs:
                            stratumRankings[i + j].masterpoints = thisAward
                        else:
                            stratumRankings[i + j].masterpoints = maxMPs
                        if numStrata > 0 and thisAward > maxMPs:
                            self.tournamentData.resultSet.pairData[stratumRankings[i + j].pairNumber].awardedStratum = stratumNumber + 1
                        self.tournamentData.resultSet.pairData[stratumRankings[i + j].pairNumber].masterpoints = stratumRankings[i + j].masterpoints
                        self.tournamentData.resultSet.pairData[stratumRankings[i + j].pairNumber].stratPosition = stratumRankings[i + j].positionNum
                    award = max(award - (awardDelta * numShared), 0)
                    i = i + numShared

            # Helper to calculate the awards for an event
            def calcWinnerAwards(stratumRanking, PairsTable, PointsTable):
                awardDivisor = 1
                # Calculate the number of awards based on the minimum number of boards played by any pair
                numAwards = int((len(stratumRanking) + 2) / 3)
                for pairData in self.tournamentData.resultSet.pairData.values():
                    if pairData.boardsPlayed < 18:
                        # Awards are halved if any pair played less than 18 boards
                        awardDivisor = 2
                        numAwards = int((len(stratumRanking) + 3) / 4)
                        break
                numPairs = len(stratumRanking)
                # Calculate the maximum award based on the number of tables/pairs
                if numPairs < PairsTable[0]:
                    # Not enough tables/pairs, no-one is getting masterpoints
                    maxAward = 0
                else:
                    # Enough tables/pairs, find the max award from the PointsTable
                    for index in range(numPairs):
                        if PairsTable[index] >= numPairs:
                            break
                    maxAward = int(PointsTable[index] / awardDivisor)
                return (maxAward, numAwards)

            # To make the code less verbose, acquire a reference to the rankings for the stratum we're processing
            stratumRankings = self.tournamentData.resultSet.overallRankings[stratumNumber]
            # Figure out what the awards should be
            if self.tournamentData.numWinners == 2:
                # Verify that we have at least 4 full tables
                if len(stratumRankings[0]) > 3 and len(stratumRankings[1]) > 3:
                    # Calculate the awards for N/S and E/W
                    awards1 = calcWinnerAwards(stratumRankings[0], TwoWinnerTableNumbers, LocalTwoWinnerTablePoints)
                    awards2 = calcWinnerAwards(stratumRankings[1], TwoWinnerTableNumbers, LocalTwoWinnerTablePoints)
                    # Stratification can reduce the masterpoints for each stratum
                    if numStrata > 0 and StratificationGood:
                        if stratumNumber == 0:
                            awards1 = (awards1[0] - awards1[1], awards1[1])
                            awards2 = (awards2[0] - awards2[1], awards2[1])
                        elif stratumNumber == 1:
                            awards1 = (awards1[0] - 3 * awards1[1], awards1[1])
                            awards2 = (awards2[0] - 3 * awards2[1], awards2[1])
                        else:
                            awards1 = (awards1[0] - 5 * awards1[1], awards1[1])
                            awards2 = (awards2[0] - 5 * awards2[1], awards2[1])
                    # Calculate the masterpoints now
                    calcMPs(stratumRankings[0], awards1[0], awards1[1])
                    calcMPs(stratumRankings[1], awards2[0], awards2[1])
            else:
                # Verify that we have at least 3 full tables
                if len(stratumRankings[0]) > 5:
                    awards = calcWinnerAwards(stratumRankings[0], OneWinnerPairsNumbers, LocalOneWinnerPairsPoints)
                    # Stratification can reduce the masterpoints for each stratum
                    if numStrata > 0 and StratificationGood:
                        if stratumNumber == 0:
                            awards = (awards[0] - awards[1], awards[1])
                        elif stratumNumber == 1:
                            awards = (awards[0] - 2 * awards[1], awards[1])
                        else:
                            awards = (awards[0] - 3 * awards[1], awards[1])
                    # Calculate the masterpoints now
                    calcMPs(stratumRankings[0], awards[0], awards[1])
            return

        # Clear out the current set of masterpoints
        for pair in self.tournamentData.resultSet.pairData:
            self.tournamentData.resultSet.pairData[pair].masterpoints = 0
            self.tournamentData.resultSet.pairData[pair].awardedStratum = None

        # Award masterpoints to the overall rankings and the strata
        numStrata = 0
        if len(self.tournamentData.resultSet.overallRankings[2][0]) > 0:
            numStrata = 2
        elif len(self.tournamentData.resultSet.overallRankings[1][0]) > 0:
            numStrata = 1
        awardMPs(0, numStrata)
        if StratificationGood:
            awardMPs(1, numStrata)
            awardMPs(2, numStrata)
