###############################################################################
# Pairs Stratification Program.
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

        self.labels = []
        label = tb.Label(self.frame, text="Select a USEBIO results file for processing.", font=("Arial", 10, "bold"), justify='left')
        label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 5))
        self.labels.append(label)
        label = tb.Label(self.frame, text="Your scoring program generates these.", font=("Arial", 10), justify='left')
        label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))
        self.labels.append(label)
        label = tb.Button(self.frame, text="Browse", bootstyle="primary", command=lambda: self.pickInputFile())
        label.grid(row=3, column=0, pady=10, padx=20, sticky="w")
        self.labels.append(label)
        label = tb.Entry(self.frame, textvariable=self.inputFileVar, width=102, font=("Arial", 10))
        label.grid(row=3, column=0, sticky="w", padx=100)
        self.labels.append(label)

        label = tb.Label(self.frame, text="Tournament Details:", font=("Arial", 10, "bold"), justify='left')
        label.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=(25,0))
        self.labels.append(label)

        self.clubNameVar = tb.StringVar()
        label = tb.Label(self.frame, text='Club:', font=("Arial", 10), justify='left')
        label.grid(row=5, column=0, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, textvariable=self.clubNameVar, font=("Arial", 10), justify='left')
        label.grid(row=5, column=0, sticky="w", padx=175)
        self.labels.append(label)

        self.tournamentNameVar = tb.StringVar()
        label = tb.Label(self.frame, text='Tournament', font=("Arial", 10), justify='left')
        label.grid(row=6, column=0, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, textvariable=self.tournamentNameVar, font=("Arial", 10), justify='left')
        label.grid(row=6, column=0, sticky="w", padx=175)
        self.labels.append(label)

        self.dateVar = tb.StringVar()
        label = tb.Label(self.frame, text='Date:', font=("Arial", 10), justify='left')
        label.grid(row=7, column=0, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, textvariable=self.dateVar, font=("Arial", 10), justify='left')
        label.grid(row=7, column=0, sticky="w", padx=175)
        self.labels.append(label)

        self.awardsTypeVar = tb.StringVar()
        label = tb.Label(self.frame, text='Masterpoints Type:', font=("Arial", 10), justify='left')
        label.grid(row=8, column=0, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, textvariable=self.awardsTypeVar, font=("Arial", 10), justify='left')
        label.grid(row=8, column=0, sticky="w", padx=175)
        self.labels.append(label)

        self.scoreTypeVar = tb.StringVar()
        label = tb.Label(self.frame, text='Scoring Method:', font=("Arial", 10), justify='left')
        label.grid(row=9, column=0, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, textvariable=self.scoreTypeVar, font=("Arial", 10), justify='left')
        label.grid(row=9, column=0, sticky="w", padx=175)
        self.labels.append(label)

        self.numPairsVar = tb.StringVar()
        label = tb.Label(self.frame, text='Number of pairs:', font=("Arial", 10), justify='left')
        label.grid(row=10, column=0, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, textvariable=self.numPairsVar, font=("Arial", 10), justify='left')
        label.grid(row=10, column=0, sticky="w", padx=175)
        self.labels.append(label)

        self.numBoardsVar = tb.StringVar()
        label = tb.Label(self.frame, text='Number of boards:', font=("Arial", 10), justify='left')
        label.grid(row=11, column=0, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, textvariable=self.numBoardsVar, font=("Arial", 10), justify='left')
        label.grid(row=11, column=0, sticky="w", padx=175)
        self.labels.append(label)

        self.numWinnersVar = tb.StringVar()
        label = tb.Label(self.frame, text='Number of winners:', font=("Arial", 10), justify='left')
        label.grid(row=12, column=0, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, textvariable=self.numWinnersVar, font=("Arial", 10), justify='left')
        label.grid(row=12, column=0, sticky="w", padx=175)
        self.labels.append(label)

        self.errorLabel = tb.Label(self.frame, text="", font=("Arial", 10, "bold"), justify='left', bootstyle="Danger", background=self.pagebgnd)
        self.errorLabel.grid(row=13, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 5))
        self.labels.append(self.errorLabel)

        self.preStratLabel = tb.Label(self.frame, text="", font=("Arial", 10, "bold"), justify='left', bootstyle="Warning", background=self.pagebgnd)
        self.preStratLabel.grid(row=14, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(self.preStratLabel)

        label = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        label.grid(row=15, column=0, columnspan=2, sticky="nw", padx=420, pady=250)
        self.labels.append(label)

        self.backButton = tb.Button(self.frame, text="< Back", bootstyle="primary", state="disabled", width=10)
        self.nextButton = tb.Button(self.frame, text="Next >", bootstyle="primary", state="disabled", width=10, command=self.nextPressed)
        self.labels.append(self.backButton)
        self.labels.append(self.nextButton)

        self.backButton.place(x=630, y=650)
        self.nextButton.place(x=730, y=650)

        self.inputFileVar.trace_add('write', self.entryChange)
        self.entryChange()
        
        self.showDetail()

    def entryChange(self, *args):
        if len(self.inputFileVar.get()) > 0 and len(self.clubNameVar.get()) > 0:
            self.nextButton.config(state="normal")
        else:
            self.nextButton.config(state="disabled")
            self.tournamentData.clearTournament()
            self.clubNameVar.set('')
            self.tournamentNameVar.set('')
            self.dateVar.set('')
            self.awardsTypeVar.set('')
            self.scoreTypeVar.set('')
            self.numPairsVar.set('')
            self.numBoardsVar.set('')
            self.numWinnersVar.set('')

    def nextPressed(self):
        self.uiparts.root.showPage('changeranks')

    def clearContent(self):
        """Safely destroys all file selection & metadata widgets, unbinds callbacks, and breaks references."""
        # Unbind command callbacks from any buttons inside self.labels
        if hasattr(self, 'labels') and self.labels:
            for widget in self.labels:
                if isinstance(widget, tb.Button):
                    try:
                        widget.configure(command="")
                    except Exception:
                        pass

        # Destroy the frame child entries, buttons, labels
        if hasattr(self, 'frame') and self.frame:
            for widget in self.frame.winfo_children():
                widget.destroy()

        # Reset list reference
        self.labels = []

        # Clear widget instance variables
        self.errorLabel = None
        self.preStratLabel = None

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
                self.nextButton.config(state="normal")
            except:
                self.errorLabel.config(text="Error - Not a pairs event.")

            self.showDetail()

    def showDetail(self):
        if self.tournamentData.clubName != None:
            self.clubNameVar.set(self.tournamentData.clubName)
            self.tournamentNameVar.set(self.tournamentData.tournamentName)
            self.dateVar.set(self.tournamentData.tournamentDate)
            self.awardsTypeVar.set(self.tournamentData.eventRating)
            self.scoreTypeVar.set('Matchpoints' if self.tournamentData.eventType == 0 else 'X-IMPs' if self.tournamentData.eventType == 1 else 'Aggregate')
            self.numPairsVar.set(self.tournamentData.numPairs)
            self.numBoardsVar.set(self.tournamentData.numBoards)
            self.numWinnersVar.set(self.tournamentData.numWinners)
