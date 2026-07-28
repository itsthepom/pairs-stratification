###############################################################################
# Pairs Stratification Utility.
# Copyright Steve Pomeroy 2026
#
# Class to perform stratification
###############################################################################
import ttkbootstrap as tb
import copy
from baseclasses import baseUIClass
from uiparts import UIParts

# These are the text names for the UI of the various MP ranks
UIMPLevels = ("None", "New Member", "Novice", "Club Master",
            "Local Master", "District Master", "Master", "1 Star Master",
            "2 Star Master", "3 Star Master", "4 Star Master", "5 Star Master",
            "Senior Master", "1 Star Senior Master", "2 Star Senior Master", "3 Star Senior Master",
            "4 Star Senior Master", "5 Star Senior Master", "Regional Master", "Scottish Master",
            "National Master", "Life Master", "Senior Life Master", "Grand Master")
# These are the text names of the various MP ranks lowercased, for comparison
MPLevels = None
# These are the rank codes of the various MP rans, as listed on Mempad
MPCode = (0, 5, 10, 20,
          30, 40, 50, 60,
          70, 80, 90, 100,
          110, 120, 130, 140,
          150, 160, 165, 170,
          180, 190, 200, 210)

StratAColor = "#000000"
StratBColor = "#CC1000"
StratCColor = "#379600"
WarningColor = "#FF8800"
CompleteColor = "#44880C"

def getMasterpointRankIndex(memberDict: dict, player1SBUNum: str, player2SBUNum: str) -> int:
    rank1 = rank2 = 'new member'
    try:
        rank1 = memberDict[player1SBUNum].lower()
    except:
        pass
    if rank1 == 'other nbo member':
        rank1 = 'grand master'
    try:
        rank2 = memberDict[player2SBUNum].lower()
    except:
        pass
    if rank2 == 'other nbo member':
        rank2 = 'grand master'
    return max(MPLevels.index(rank1), MPLevels.index(rank2))

class stratify(baseUIClass):
    """ Runs the stratification UI and stratifies an event.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
            tournamentData(tournament): tournamentData instance holding the event data.
            uiparts(UIParts): Holds the UI components.
    """
    def __init__(self, frame, tournamentData, uiparts: UIParts):
        global MPLevels, UIMPLevels
        self.frame = frame
        self.tournamentData = tournamentData
        self.uiparts = uiparts
        uiparts.stratifyDisplay = self
        if MPLevels == None:
            MPLevels = tuple(s.lower() for s in UIMPLevels)
        if frame != None:
            if tournamentData != None and tournamentData.tournamentContentInst != None:
                self.last = tournamentData.tournamentContentInst.getDescription()
            self.overallNSPairs = tb.StringVar()
            self.overallEWPairs = tb.StringVar()
            self.strat1NSPairs = tb.StringVar()
            self.strat1EWPairs = tb.StringVar()
            self.strat2NSPairs = tb.StringVar()
            self.strat2EWPairs = tb.StringVar()
            self.overallNSStringLabel = tb.StringVar()
            self.overallEWStringLabel = tb.StringVar()
            self.strat1NSStringLabel = tb.StringVar()
            self.overallNSStringLabel.set('Overall N/S Pairs:')
            self.overallEWStringLabel.set('Overall E/W Pairs:')
            self.strat1NSStringLabel.set('Strat B N/S Pairs:')
            self.resultsAmps = tb.StringVar()
            self.resultsBmps = tb.StringVar()
            self.resultsCmps = tb.StringVar()
            self.statusText = tb.StringVar()
            self.awardMPs = tb.BooleanVar()
            self.awardMPs.set(True)
            self.BSliderVar = tb.DoubleVar()
            self.CSliderVar = tb.DoubleVar()
            self.indexB = None
            self.indexC = None
            self.sliderStepSize = 1
            self.minRankText = tb.StringVar()
            self.maxRankText = tb.StringVar()
            self.slider_height = 552
            self.step_size = self.slider_height / (len(UIMPLevels) - 1)
        self.numLoads = 0
        self.minRankIndex = 0
        self.maxRankIndex = len(UIMPLevels)

    def getName(self):
        return 'stratify'
    
    def setStratStrings(self):
        """ Updates the stratification details for display on the UI.
        """
        self.minRankText.set(UIMPLevels[self.minRankIndex])
        self.maxRankText.set(UIMPLevels[self.maxRankIndex])
        if len(self.tournamentData.resultSet.overallRankings[0][1]) > 0:
            self.overallNSPairs.set(str(self.buckets[0]) + ' (' + str(self.buckets[0]+self.buckets[2]) + ' overall)')
            self.overallEWPairs.set(str(self.buckets[1]) + ' (' + str(self.buckets[1]+self.buckets[3]) + ' overall)')
            self.strat1NSPairs.set(str(self.buckets[2]-self.buckets[4]) + ' (' + str(self.buckets[2]) + ' in stratum)')
            self.strat1EWPairs.set(str(self.buckets[3]-self.buckets[5]) + ' (' + str(self.buckets[3]) + ' in stratum)')
            self.strat2NSPairs.set(str(self.buckets[4]))
            self.strat2EWPairs.set(str(self.buckets[5]))
            self.overallNSStringLabel.set('Strat A N/S Pairs:')
            self.overallEWStringLabel.set('Strat A E/W Pairs:')
            self.strat1NSStringLabel.set('Strat B N/S Pairs:')
            self.strat1EWLabel.config(text='Strat B E/W Pairs')
            self.strat2NSLabel.config(text='Strat C N/S Pairs:')
            self.strat2EWLabel.config(text='Strat C E/W Pairs:')
        else:
            self.overallNSPairs.set(str(self.buckets[0]) + ' (' + str(self.buckets[0]+self.buckets[2]) + ' overall)')
            self.overallEWPairs.set(str(self.buckets[2]-self.buckets[4]) + ' (' + str(self.buckets[2]) + ' in stratum)')
            self.strat1NSPairs.set(str(self.buckets[4]))
            self.strat1EWPairs.set('')
            self.strat2NSPairs.set('')
            self.strat2EWPairs.set('')
            self.overallNSStringLabel.set('Strat A Pairs:')
            self.overallEWStringLabel.set('Strat B Pairs:')
            self.strat1NSStringLabel.set('Strat C Pairs:')
            self.strat1EWLabel.config(text='')
            self.strat2NSLabel.config(text='')
            self.strat2EWLabel.config(text='')

    def resetStratStrings(self):
        """ Clears the tournament details strings.
        """
        self.overallNSStringLabel.set('Strat A N/S Pairs:')
        self.overallEWStringLabel.set('Strat A E/W Pairs:')
        self.strat1NSStringLabel.set('Strat B N/S Pairs:')
        self.strat1EWLabel.config(text='Strat B E/W Pairs:')
        self.strat2NSLabel.config(text='Strat C N/S Pairs:')
        self.strat2EWLabel.config(text='Strat C E/W Pairs:')
        self.overallNSPairs.set('')
        self.overallEWPairs.set('')
        self.strat1NSPairs.set('')
        self.strat1EWPairs.set('')
        self.strat2NSPairs.set('')
        self.strat2EWPairs.set('')

    def coloriseLabels(self):
        for i, lbl in enumerate(self.label_widgets):
            if i < self.minRankIndex:
                lbl.config(foreground="grey")
            elif i > self.maxRankIndex:
                lbl.config(foreground="grey")
            else:
                lbl.config(foreground=StratAColor if i > self.indexB else StratCColor if i <= self.indexC and self.indexC != 0 else StratBColor)

    def snap_and_clamp(self, val, sliderB=None):
        """Snaps value to step 'n' and clamps between MIN and MAX limits."""
        snapped = round(val / self.step_size)
        clamped = max(self.minRankIndex - 1, min(self.maxRankIndex - 1, snapped))
        if sliderB:
            self.indexB = max(self.minRankIndex - 1, min(self.maxRankIndex - 1, clamped))
            if self.indexB <= self.indexC:
                if self.indexC > self.minRankIndex:
                    self.indexB = max(self.minRankIndex - 1, self.indexC + 1)
            self.stratum1Level = self.indexB
            clamped = self.indexB
        else:
            self.indexC = max(self.minRankIndex - 1, min(self.maxRankIndex - 1, clamped))
            if self.indexC >= self.indexB:
               self.indexC = max(self.minRankIndex - 1, self.indexB - 1)
            self.stratum2Level = self.indexC
            clamped = self.indexC
        self.coloriseLabels()
        self.calcNumInStratum()
        return clamped * self.step_size - 3

    def enforce_limits(self, event=None, slider_var=None, sliderB=None):
        """Keeps the value snapped and clamped while dragging."""
        slider_var.set(self.snap_and_clamp(slider_var.get(), sliderB))

    def handle_trough_click(self, event, slider_var, sliderB=None):
        scale = event.widget
        height = scale.winfo_height()
        if height <= 1:
            return

        from_val = float(scale.cget("from"))
        to_val = float(scale.cget("to"))

        # Determine where the slider handle currently is (in pixels)
        current_val = slider_var.get()
        handle_x = ((current_val - from_val) / (from_val - to_val)) * height

        # Check if click hit the handle
        element = scale.identify(event.x, event.y)
        if "slider" in element or "thumb" in element or abs(event.x - handle_x) <= 15:
            return  # Pass through to default handling so dragging works!

        # Click landed on empty trough
        clicked_val = height - (event.y / height) * (from_val - to_val)
        slider_var.set(self.snap_and_clamp(clicked_val, sliderB))
        return "break"

    def set_slider_target(self, target, slider_var):
        """Utility function to safely snap/clamp any value before assigning it."""
        slider_var.set(self.snap_and_clamp(target))

    def construct(self, pagebgnd):
        self.pagebgnd = pagebgnd
        if self.last != self.tournamentData.tournamentContentInst.getDescription():
            self.last = self.tournamentData.tournamentContentInst.getDescription()

        if self.numLoads != self.tournamentData.numLoads:
            self.numLoads = self.tournamentData.numLoads
            self.stratum1Level = UIMPLevels.index(self.uiparts.options.config['stratum1threshold'])
            self.stratum2Level = UIMPLevels.index(self.uiparts.options.config['stratum2threshold'])
            if hasattr(self.tournamentData.resultSet, 'stratumLabels'):
                self.stratum1Level = UIMPLevels.index(self.tournamentData.resultSet.stratumLabels[0])
                self.stratum2Level = UIMPLevels.index(self.tournamentData.resultSet.stratumLabels[1])
            self.indexB = self.stratum1Level
            self.indexC = self.stratum2Level
            self.clearResult()

        self.spacerLabel = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel.grid(row=0, column=0, columnspan=2, sticky="nw")

        self.label_widgets = []
        # Create labels aligned with scale
        for i, text in enumerate(UIMPLevels):
            lbl = tb.Label(self.frame, text=text, anchor="w")
            lbl.grid(row=len(UIMPLevels) + 1 - i, column=0, sticky="w", padx=0)
            self.label_widgets.append(lbl)
        # Make rows expand evenly
        for i in range(len(UIMPLevels)):
            self.frame.rowconfigure(i, weight=1)

        self.scaleB = tb.Scale(self.frame,
                               from_=self.slider_height,   # reverse so top = highest
                               to=0,
                               orient="vertical",
                               variable=self.BSliderVar,
                               length=self.slider_height,
                               bootstyle="danger",
                               command=lambda event: self.enforce_limits(None, self.BSliderVar, True)) # Uses Bootstrap theme styling directly
        self.scaleB.grid(row=2, column=1, columnspan=1, rowspan=len(UIMPLevels), sticky="w", padx=20)
        self.scaleB.bind("<Button-1>", lambda event: self.handle_trough_click(event, self.BSliderVar, True))
        self.scaleB.bind("<B1-Motion>", lambda event: self.enforce_limits(event, self.BSliderVar, True))

        self.scaleC = tb.Scale(self.frame,
                               from_=self.slider_height,   # reverse so top = highest
                               to=0,
                               orient="vertical",
                               variable=self.CSliderVar,
                               length=self.slider_height,
                               bootstyle="success",
                               command=lambda event: self.enforce_limits(None, self.CSliderVar, False)) # Uses Bootstrap theme styling directly
        self.scaleC.grid(row=2, column=2, columnspan=1, rowspan=len(UIMPLevels), sticky="w", padx=10)
        self.scaleC.bind("<Button-1>", lambda event: self.handle_trough_click(event, self.CSliderVar, False))
        self.scaleC.bind("<B1-Motion>", lambda event: self.enforce_limits(event, self.CSliderVar, False))

        self.strataLabel1 = tb.Label(self.frame, text="Select the strata levels", font=("Arial", 10, "bold"), justify='left')
        self.strataLabel1.grid(row=0, column=0, columnspan=3, pady=10)
        self.stratLevelsLabel1 = tb.Label(self.frame, text="A", font=("Arial", 10, "bold"), justify='left')
        self.stratLevelsLabel1.grid(row=1, column=0, sticky="w", padx=20)
        self.stratLevelsLabel2 = tb.Label(self.frame, text="B", font=("Arial", 10, "bold"), justify='left', foreground=StratBColor)
        self.stratLevelsLabel2.grid(row=1, column=1, sticky="w", padx=24)
        self.stratLevelsLabel3 = tb.Label(self.frame, text="C", font=("Arial", 10, "bold"), justify='left', foreground=StratCColor)
        self.stratLevelsLabel3.grid(row=1, column=2, sticky="w", padx=14)

        self.spacerLabel1 = tb.Label(self.frame, text="", font=("Arial", 1), justify='left')
        self.spacerLabel1.grid(row=8, column=3, sticky="nw", padx=20)

        self.ranksLabel = tb.Label(self.frame, text="Min/Max Ranks in event", font=("Arial", 10, "bold"), justify='left')
        self.ranksLabel.grid(row=0, column=4, sticky="w", padx=20, pady=5)
        self.maxRankLabel = tb.Label(self.frame, text="Highest Rank", font=("Arial", 10), justify='left')
        self.maxRankLabel.grid(row=1, column=4, sticky="w", padx=20)
        self.maxRankContentLabel = tb.Label(self.frame, textvariable=self.maxRankText, font=("Arial", 10), justify='left')
        self.maxRankContentLabel.grid(row=1, column=4, sticky="w", padx=150)
        self.minRankLabel = tb.Label(self.frame, text="Lowest Rank", font=("Arial", 10), justify='left')
        self.minRankLabel.grid(row=2, column=4, sticky="w", padx=20)
        self.minRankContentLabel = tb.Label(self.frame, textvariable=self.minRankText, font=("Arial", 10), justify='left')
        self.minRankContentLabel.grid(row=2, column=4, sticky="w", padx=150)

        self.stratDetailLabel = tb.Label(self.frame, text="Stratification Split", font=("Arial", 10, "bold"), justify='left')
        self.stratDetailLabel.grid(row=4, column=4, sticky="w", padx=20)
        self.overallNSLabel = tb.Label(self.frame, textvariable=self.overallNSStringLabel, font=("Arial", 10), justify='left')
        self.overallNSLabel.grid(row=5, column=4, sticky="w", padx=20)
        self.overallNSContentLabel = tb.Label(self.frame, textvariable=self.overallNSPairs, font=("Arial", 10), justify='left')
        self.overallNSContentLabel.grid(row=5, column=4, sticky="w", padx=150)
        self.overallEWLabel = tb.Label(self.frame, textvariable=self.overallEWStringLabel, font=("Arial", 10), justify='left')
        self.overallEWLabel.grid(row=6, column=4, sticky="w", padx=20)
        self.overallEWContentLabel = tb.Label(self.frame, textvariable=self.overallEWPairs, font=("Arial", 10), justify='left')
        self.overallEWContentLabel.grid(row=6, column=4, sticky="w", padx=150)
        self.strat1NSLabel = tb.Label(self.frame, textvariable=self.strat1NSStringLabel, font=("Arial", 10), justify='left')
        self.strat1NSLabel.grid(row=7, column=4, sticky="w", padx=20)
        self.strat1NSContentLabel = tb.Label(self.frame, textvariable=self.strat1NSPairs, font=("Arial", 10), justify='left')
        self.strat1NSContentLabel.grid(row=7, column=4, sticky="w", padx=150)
        self.strat1EWLabel = tb.Label(self.frame, text='', font=("Arial", 10), justify='left')
        self.strat1EWLabel.grid(row=8, column=4, sticky="w", padx=20)
        self.strat1EWContentLabel = tb.Label(self.frame, textvariable=self.strat1EWPairs, font=("Arial", 10), justify='left')
        self.strat1EWContentLabel.grid(row=8, column=4, sticky="w", padx=150)
        self.strat2NSLabel = tb.Label(self.frame, text='', font=("Arial", 10), justify='left')
        self.strat2NSLabel.grid(row=9, column=4, sticky="w", padx=20)
        self.strat2NSContentLabel = tb.Label(self.frame, textvariable=self.strat2NSPairs, font=("Arial", 10), justify='left')
        self.strat2NSContentLabel.grid(row=9, column=4, sticky="w", padx=150)
        self.strat2EWLabel = tb.Label(self.frame, text='', font=("Arial", 10), justify='left')
        self.strat2EWLabel.grid(row=10, column=4, sticky="w", padx=20)
        self.strat2EWContentLabel = tb.Label(self.frame, textvariable=self.strat2EWPairs, font=("Arial", 10), justify='left')
        self.strat2EWContentLabel.grid(row=10, column=4, sticky="w", padx=150)

        self.stratResultsLabel = tb.Label(self.frame, text="Stratification Results", font=("Arial", 10, "bold"), justify='left')
        self.stratResultsLabel.grid(row=12, column=4, sticky="w", padx=20)
        self.stratResultsALabel = tb.Label(self.frame, text='Stratum A Masterpoints:', font=("Arial", 10), justify='left')
        self.stratResultsALabel.grid(row=13, column=4, sticky="w", padx=20)
        self.stratResultsAContentLabel = tb.Label(self.frame, textvariable=self.resultsAmps, font=("Arial", 10), justify='left')
        self.stratResultsAContentLabel.grid(row=13, column=4, sticky="w", padx=180)
        self.stratResultsBLabel = tb.Label(self.frame, text='Stratum B Masterpoints:', font=("Arial", 10), justify='left')
        self.stratResultsBLabel.grid(row=14, column=4, sticky="w", padx=20)
        self.stratResultsBContentLabel = tb.Label(self.frame, textvariable=self.resultsBmps, font=("Arial", 10), justify='left')
        self.stratResultsBContentLabel.grid(row=14, column=4, sticky="w", padx=180)
        self.stratResultsCLabel = tb.Label(self.frame, text='Stratum C Masterpoints:', font=("Arial", 10), justify='left')
        self.stratResultsCLabel.grid(row=15, column=4, sticky="w", padx=20)
        self.stratResultsCContentLabel = tb.Label(self.frame, textvariable=self.resultsCmps, font=("Arial", 10), justify='left')
        self.stratResultsCContentLabel.grid(row=15, column=4, sticky="w", padx=180)

        self.statusLabel = tb.Label(self.frame, textvariable=self.statusText, font=("Arial", 10, "bold"), justify='left')
        self.statusLabel.grid(row=17, column=4, columnspan=2, sticky="w", padx=20)

        self.strataLabel2 = tb.Label(self.frame, text="Click Stratify to apply this stratification.", font=("Arial", 10, "bold"), justify='left')
        self.strataLabel2.grid(row=27, column=4, sticky="w")

        self.stratifyButton = tb.Button(self.frame, text="Stratify", bootstyle="primary", width=10, command=lambda: self.stratifyResults())
        self.stratifyButton.place(x=340, y=650)

        self.spacerLabel2 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel2.grid(row=0, column=5, sticky="nw", padx=220)
        self.spacerLabel3 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel3.grid(row=30, column=0, columnspan=5, sticky="nw", padx=220, pady=100)

        # Init the labels
        self.setRange()
        self.BSliderVar.set(self.indexB * self.step_size)
        self.CSliderVar.set(self.indexC * self.step_size)
        self.enforce_limits(None, self.BSliderVar, True)
        self.enforce_limits(None, self.CSliderVar, False)
        self.coloriseLabels()

    def clearContent(self):
        self.spacerLabel3.destroy()
        self.spacerLabel2.destroy()
        self.stratifyButton.destroy()
        self.strataLabel2.destroy()
        self.statusLabel.destroy()
        self.stratResultsCContentLabel.destroy()
        self.stratResultsCLabel.destroy()
        self.stratResultsBContentLabel.destroy()
        self.stratResultsBLabel.destroy()
        self.stratResultsAContentLabel.destroy()
        self.stratResultsALabel.destroy()
        self.stratResultsLabel.destroy()
        self.strat2EWContentLabel.destroy()
        self.strat2EWLabel.destroy()
        self.strat2NSContentLabel.destroy()
        self.strat2NSLabel.destroy()
        self.strat1EWContentLabel.destroy()
        self.strat1EWLabel.destroy()
        self.strat1NSContentLabel.destroy()
        self.strat1NSLabel.destroy()
        self.overallEWContentLabel.destroy()
        self.overallEWLabel.destroy()
        self.overallNSContentLabel.destroy()
        self.overallNSLabel.destroy()
        self.minRankContentLabel.destroy()
        self.minRankLabel.destroy()
        self.maxRankContentLabel.destroy()
        self.maxRankLabel.destroy()
        self.stratDetailLabel.destroy()
        self.spacerLabel1.destroy()
        self.stratLevelsLabel3.destroy()
        self.stratLevelsLabel2.destroy()
        self.stratLevelsLabel1.destroy()
        self.ranksLabel.destroy()
        self.strataLabel1.destroy()
        self.scaleC.destroy()
        self.scaleB.destroy()
        for lbl in self.label_widgets:
            lbl.destroy()
        self.spacerLabel.destroy()

    def setResult(self, message: str, warning: bool, mpsawarded: list=None):
        self.statusText.set(message)
        self.statusLabel.config(foreground=WarningColor if warning else CompleteColor)
        if mpsawarded != None:
            self.resultsAmps.set(str(mpsawarded[0]))
            self.resultsBmps.set(str(mpsawarded[1]))
            self.resultsCmps.set(str(mpsawarded[2]))
    
    def clearResult(self):
        self.statusText.set('')
        self.resultsAmps.set('')
        self.resultsBmps.set('')
        self.resultsCmps.set('')

    def calcNumInStratum(self):
        buckets = [0, 0, 0, 0, 0, 0]
        try:
            for pair in self.tournamentData.resultSet.pairData.values():
                if pair.masterpointsRankIndex > self.stratum1Level:
                    buckets[0 + 1 - pair.isNS] = buckets[0 + 1 - pair.isNS] + 1
                else:
                    buckets[2 + 1 - pair.isNS] = buckets[2 + 1 - pair.isNS] + 1
                    if pair.masterpointsRankIndex <= self.stratum2Level:
                        buckets[4 + 1 - pair.isNS] = buckets[4 + 1 - pair.isNS] + 1
            self.buckets = buckets
            self.setStratStrings()
            self.clearResult()
            enableState = "normal" if not self.insufficientBoards else "disabled"
            if enableState == "disabled":
                self.setResult("Cannot stratify - Insufficient boards played by some pairs.", True)
            else:
                isTwoWinner = self.tournamentData.numWinners == 2
                minPairs = 3 if isTwoWinner else 6
                stratEnabled = buckets[2] + buckets[3] + buckets[4] + buckets[5]
                if stratEnabled and (buckets[2] < minPairs or (isTwoWinner and buckets[3] < minPairs)):
                    enableState = "disabled"
                stratEnabled = buckets[4] + buckets[5]
                if stratEnabled and (buckets[4] < minPairs or (isTwoWinner and buckets[5] < minPairs)):
                    enableState = "disabled"
                if enableState == "disabled":
                    self.setResult("Cannot stratify - Insufficient pairs in the lowest stratum.", True)
            if enableState == "normal":
                self.statusLabel.config(text='')
            if (buckets[2] + buckets[3] + buckets[4] + buckets[5]) == 0:
                enableState = "disabled"
            self.stratifyButton.config(state=enableState)
        except:
            pass

    def setRange(self):
        self.minRankIndex = len(UIMPLevels)
        self.maxRankIndex = 0
        try:
            for pair in self.tournamentData.resultSet.pairData.values():
                if pair.masterpointsRankIndex < self.minRankIndex:
                    self.minRankIndex = pair.masterpointsRankIndex
                if pair.masterpointsRankIndex > self.maxRankIndex:
                    self.maxRankIndex = pair.masterpointsRankIndex
        except:
            self.minRankIndex = 0
            self.maxRankIndex = len(UIMPLevels) - 1
        # Check that all pairs play at least 18 boards
        self.insufficientBoards = False
        for pair in self.tournamentData.resultSet.pairData.values():
            if pair.boardsPlayed < 18:
                self.insufficientBoards = True
    
    def stratifyOnce(self, memberDict:dict, stratumNumber:int, stratumUpperLevel:int, stratumLowerLevel:int):
        """ Scans the overall rankings and assigns players to the stratum rankings who are
            between the supplied upper and lower rankings.

            Args:
                memberDict(dict): Dictionary of player rankings extracted from MEMPAD
                stratumNumber(int): Stratum number being processed
                stratumUpperLevel(str): Name of the upper masterpoints level for this stratum
                stratumLowerLevel(str): Name of the lower masterpoints level for this stratum
        """
        # We iterate over the overall rankings and any pair whose masterpoint rankings
        # are below the stratum cut-offs are copied into the given lists.
        if stratumUpperLevel > self.minRankIndex:
            for direction in range(len(self.tournamentData.resultSet.overallRankings[0])):
                for pair in self.tournamentData.resultSet.overallRankings[0][direction]:
                    # This iterates the N/S and E/W results for 2 winner results and the overall for 1 winner results
                    # Use an exception catcher as we could have other NBO members without SBU MP numbers
                    try:
                        inStratum = self.tournamentData.resultSet.pairData[pair.pairNumber].masterpointsRankIndex <= stratumUpperLevel
                        inStratum = inStratum and self.tournamentData.resultSet.pairData[pair.pairNumber].masterpointsRankIndex > stratumLowerLevel
                        if inStratum:
                            self.tournamentData.resultSet.pairData[pair.pairNumber].strat = stratumNumber
                            self.tournamentData.resultSet.overallRankings[stratumNumber][direction].append(copy.copy(pair))
                    except Exception as e:
                        pass
    
    def isValidLevel(self, string:str):
        return string.lower() in MPLevels
    
    def stratifyResults(self, isBatchMode: bool=False, stratum1Threshold:str=None, stratum2Threshold:str=None):
        """ Stratifies the event

            Args:
                isBatchMode(bool): True for batch mode (no UI output).
                mempadCache(io.StringIO): Cache holding freshly retrieved MEMPAD players CSV DB.
                stratum1Threshold(str): Name of the maximum masterpoints level for stratum 1.
                stratum2Threshold(str): Name of the maximum masterpoints level for stratum 2.
        """
        if not isBatchMode:
            self.clearStratify()
            self.statusLabel.config(text='')
        
        # Where the players in the pair have different rankings, stratification is done
        # using either the HIGHEST ranking or the AVERAGE ranking - depending what is selected
        # in the options. For AVERAGE, this means we need to know the current masterpoints value
        # for each player. Mempad only gives us the current ranking and not the points value, so
        # to do an AVERAGE would only be an approximation and possibly unfair. Therefore, at the
        # present, we only do the HIGHEST selection.
        stratOK = False
        try:
            # Clear the current stratification results
            self.tournamentData.resultSet.overallRankings[1] = [list(), list()]
            self.tournamentData.resultSet.overallRankings[2] = [list(), list()]

            # Process the results into the strata. The overall results are already in
            # self.tournamentData.resultSet.overallRankings. That is a list of 3 lists.
            # The [0] list is the overall rankings, produced when we read the file.
            if isBatchMode:
                self.indexB = UIMPLevels.index(stratum1Threshold)
                self.indexC = UIMPLevels.index(stratum2Threshold)
            self.tournamentData.resultSet.stratumLabels[0] = UIMPLevels[self.indexB]
            self.tournamentData.resultSet.stratumLabels[1] = UIMPLevels[self.indexC]
            for direction in range(len(self.tournamentData.resultSet.overallRankings[0])):
                for pair in self.tournamentData.resultSet.overallRankings[0][direction]:
                    self.tournamentData.resultSet.pairData[pair.pairNumber].strat = 0

            self.stratifyOnce(self.tournamentData.tournamentContentInst.memberDict, 1, self.indexB, 0)
            self.stratifyOnce(self.tournamentData.tournamentContentInst.memberDict, 2, self.indexC, 0)

            self.retainedRankings1 = None
            self.retainedRankings2 = None

            # Set the pair rankings for each stratum
            self.tournamentData.resultSet.setPositions(self.tournamentData.resultSet.overallRankings[1][0])
            self.tournamentData.resultSet.setPositions(self.tournamentData.resultSet.overallRankings[1][1])
            self.tournamentData.resultSet.setPositions(self.tournamentData.resultSet.overallRankings[2][0])
            self.tournamentData.resultSet.setPositions(self.tournamentData.resultSet.overallRankings[2][1])

            stratOK = True
            if isBatchMode or self.awardMPs.get():
                # If no stratification was done, display an appropriate message
                if not isBatchMode and len(self.tournamentData.resultSet.overallRankings[1][0]) == 0:
                    self.setResult("No stratification done. Original masterpoints stand.", True)
                    stratOK = False
                else:
                    # Calculate the MPs so we can tell if masterpoints were awarded in all strata
                    self.tournamentData.masterpointsObject.calculateMPs(True)
                    # Make a pass over the pair data and if no awards have been made in any sub-stratum, revert
                    StratumFound = [ False, False ]
                    for pair in self.tournamentData.resultSet.pairData.values():
                        if pair.awardedStratum != None and pair.awardedStratum > 1:
                            StratumFound[pair.awardedStratum - 2] = True

                    Stratum1Good = self.indexB >= self.minRankIndex and StratumFound[0]
                    Stratum2Good = self.indexC >= self.minRankIndex and StratumFound[1]
                    if not(Stratum1Good or Stratum2Good):
                        stratOK = False
                        # No masterpoints awarded in at least one stratum. Recalculate the MPs without stratification
                        self.tournamentData.masterpointsObject.calculateMPs(False)
                        if not isBatchMode:
                            self.setResult("No masterpoints gained in secondary strata. Original masterpoints stand.", True)
            if stratOK and not isBatchMode:
                awardedStrata = [ 0, 0, 0 ]
                for pair in self.tournamentData.resultSet.pairData.values():
                    if pair.awardedStratum != None:
                        awardedStrata[pair.awardedStratum - 1] = awardedStrata[pair.awardedStratum - 1] + pair.masterpoints
                self.setResult("Stratification Complete.", False, awardedStrata)

        except:
            pass
        
        if not isBatchMode:
            self.uiparts.mainMenu.enableMPFile(stratOK)

        return 1

    def clearStratify(self):
        self.statusLabel.config(text='')
        
        try:
            self.tournamentData.resultSet.overallRankings[1] = [list(), list()]
            self.tournamentData.resultSet.overallRankings[2] = [list(), list()]
            # Recalculate the MPs
            self.tournamentData.masterpointsObject.calculateMPs(False)
        except:
            pass
