###############################################################################
# Pairs Stratification Utility.
# Copyright Steve Pomeroy 2026
#
# UI for loading a tournament from a USEBIO file
###############################################################################
import ttkbootstrap as tb
from baseclasses import baseUIClass
from uiparts import UIParts
import filehandling
import USEBIO

class selectTournament(baseUIClass):
    """ Runs the UI to choose an event to work with.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
            tournamentData(tournament): tournamentData instance holding the event data.
            uiparts(UIParts): Holds the UI components.
    """
    def __init__(self, frame: tb.Frame, tournamentData, uiparts: UIParts):
        self.frame = frame
        self.tournamentData = tournamentData
        self.inputFileVar = tb.StringVar()
        self.uiparts = uiparts
        uiparts.selectTournamentDisplay = self
    
    def getName(self):
        return 'select'
    
    def construct(self, pagebgnd: str):
        self.pagebgnd = pagebgnd
        self.spacerLabel = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel.grid(row=0, column=0, columnspan=2, sticky="nw")
        self.inputFileLabel1 = tb.Label(self.frame, text="Select a USEBIO results file for processing.", font=("Arial", 10, "bold"), justify='left')
        self.inputFileLabel1.grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
        self.inputFileLabel2 = tb.Label(self.frame, text="Your scoring program generates these.", font=("Arial", 10), justify='left')
        self.inputFileLabel2.grid(row=2, column=0, columnspan=2, sticky="w", padx=20)
        self.browseButton = tb.Button(self.frame, text="Browse", bootstyle="primary", command=lambda: self.pickInputFile())
        self.browseButton.grid(row=3, column=0, pady=10, padx=20, sticky="w")
        self.inputFileEntry = tb.Entry(self.frame, textvariable=self.inputFileVar, width=95, font=("Arial", 10))
        self.inputFileEntry.grid(row=3, column=0, sticky="w", padx=100)

        self.spacerLabel1 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel1.grid(row=4, column=0, columnspan=2, sticky="nw")
        self.detailTitleLabel = tb.Label(self.frame, text="Tournament Details:", font=("Arial", 10, "bold"), justify='left')
        self.detailTitleLabel.grid(row=5, column=0, columnspan=2, sticky="w", padx=20)
        self.clubNameVar = tb.StringVar()
        self.clubNameLabel1 = tb.Label(self.frame, text='Club:', font=("Arial", 10), justify='left')
        self.clubNameLabel1.grid(row=6, column=0, sticky="w", padx=20)
        self.clubNameLabel2 = tb.Label(self.frame, textvariable=self.clubNameVar, font=("Arial", 10), justify='left')
        self.clubNameLabel2.grid(row=6, column=0, sticky="w", padx=175)
        self.tournamentNameVar = tb.StringVar()
        self.tournamentNameLabel1 = tb.Label(self.frame, text='Tournament', font=("Arial", 10), justify='left')
        self.tournamentNameLabel1.grid(row=7, column=0, sticky="w", padx=20)
        self.tournamentNameLabel2 = tb.Label(self.frame, textvariable=self.tournamentNameVar, font=("Arial", 10), justify='left')
        self.tournamentNameLabel2.grid(row=7, column=0, sticky="w", padx=175)
        self.dateVar = tb.StringVar()
        self.dateLabel1 = tb.Label(self.frame, text='Date:', font=("Arial", 10), justify='left')
        self.dateLabel1.grid(row=8, column=0, sticky="w", padx=20)
        self.dateLabel2 = tb.Label(self.frame, textvariable=self.dateVar, font=("Arial", 10), justify='left')
        self.dateLabel2.grid(row=8, column=0, sticky="w", padx=175)
        self.numPairsVar = tb.StringVar()
        self.numPairsLabel1 = tb.Label(self.frame, text='Number of pairs:', font=("Arial", 10), justify='left')
        self.numPairsLabel1.grid(row=9, column=0, sticky="w", padx=20)
        self.numPairsLabel2 = tb.Label(self.frame, textvariable=self.numPairsVar, font=("Arial", 10), justify='left')
        self.numPairsLabel2.grid(row=9, column=0, sticky="w", padx=175)
        self.numBoardsVar = tb.StringVar()
        self.numBoardsLabel1 = tb.Label(self.frame, text='Number of boards:', font=("Arial", 10), justify='left')
        self.numBoardsLabel1.grid(row=10, column=0, sticky="w", padx=20)
        self.numBoardsLabel2 = tb.Label(self.frame, textvariable=self.numBoardsVar, font=("Arial", 10), justify='left')
        self.numBoardsLabel2.grid(row=10, column=0, sticky="w", padx=175)
        self.numWinnersVar = tb.StringVar()
        self.numWinnersLabel1 = tb.Label(self.frame, text='Number of winners:', font=("Arial", 10), justify='left')
        self.numWinnersLabel1.grid(row=11, column=0, sticky="w", padx=20)
        self.numWinnersLabel2 = tb.Label(self.frame, textvariable=self.numWinnersVar, font=("Arial", 10), justify='left')
        self.numWinnersLabel2.grid(row=11, column=0, sticky="w", padx=175)

        self.spacerLabel2 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel2.grid(row=14, column=0, columnspan=2, sticky="nw", padx=420)

        self.errorLabel = tb.Label(self.frame, text="", font=("Arial", 10, "bold"), justify='left', bootstyle="Danger")
        self.errorLabel.grid(row=15, column=0, columnspan=2, sticky="w", padx=20)

        self.preStratLabel = tb.Label(self.frame, text="", font=("Arial", 10, "bold"), justify='left', bootstyle="Warning")
        self.preStratLabel.grid(row=16, column=0, columnspan=2, sticky="w", padx=20)

        self.spacerLabel3 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel3.grid(row=17, column=0, columnspan=2, sticky="nw", padx=420, pady=250)
        self.showDetail()
        
    def clearContent(self):
        self.spacerLabel3.destroy()
        self.preStratLabel.destroy()
        self.errorLabel.destroy()
        self.spacerLabel2.destroy()
        self.numWinnersLabel2.destroy()
        self.numWinnersLabel1.destroy()
        self.numBoardsLabel2.destroy()
        self.numBoardsLabel1.destroy()
        self.numPairsLabel2.destroy()
        self.numPairsLabel1.destroy()
        self.dateLabel2.destroy()
        self.dateLabel1.destroy()
        self.tournamentNameLabel2.destroy()
        self.tournamentNameLabel1.destroy()
        self.clubNameLabel2.destroy()
        self.clubNameLabel1.destroy()
        self.detailTitleLabel.destroy()
        self.spacerLabel1.destroy()
        self.inputFileEntry.destroy()
        self.browseButton.destroy()
        self.inputFileLabel2.destroy()
        self.inputFileLabel1.destroy()
        self.spacerLabel.destroy()

    def pickInputFile(self):
        filename = filehandling.openResultsFile(self.uiparts.options.config["resultsdir"], False)
        if len(filename) > 0:
            self.preStratLabel.config(text="")
            self.errorLabel.config(text="")
            self.inputFileVar.set(filename)
            self.tournamentData.readerClass = USEBIO.USEBIO(self.tournamentData, self.uiparts.options)
            try:
                self.tournamentData.readerClass.read(self.inputFileVar.get())
                if self.tournamentData.preStratified:
                    self.preStratLabel.config(text="Event already stratified. Re-stratify if you wish.")
            except:
                self.errorLabel.config(text="Error - Not a pairs event.")

            self.showDetail()

    def showDetail(self):
        if self.tournamentData.clubName != None:
            self.clubNameVar.set(self.tournamentData.clubName)
            self.tournamentNameVar.set(self.tournamentData.tournamentName)
            self.dateVar.set(self.tournamentData.tournamentDate)
            self.numPairsVar.set(self.tournamentData.numPairs)
            self.numBoardsVar.set(self.tournamentData.numBoards)
            self.numWinnersVar.set(self.tournamentData.numWinners)
