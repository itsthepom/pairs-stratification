###############################################################################
# Pairs Stratification Utility.
# Copyright Steve Pomeroy 2026
#
# Entry point and main menu
###############################################################################
import tkinter
from tkinter import *
import ttkbootstrap as tb
from baseclasses import baseUIClass, AppName, AppVersion
import os
import sys
from uiparts import UIParts
import options
import selectTournament
import stratify
import tournament
import pdfresults
import webpage
import masterpoints
import helpserver
import USEBIO
import argparse
from pathlib import Path
import ctypes
from filehandling import readPlayersDB

# 1. Enable Per-Monitor V2 DPI awareness in Windows before creating Tk
if sys.platform == "win32":
    try:
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except AttributeError:
        # Fallback for older Windows 10 versions
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
        except AttributeError:
            ctypes.windll.user32.SetProcessDPIAware()

# Colors
menubgnd = "#dddddd"
tourneybgnd = "#bccbf8"
pagebgnd = "#fcfcfc"
menucolor = "blue"
menuhilite = "#ee942e"
menuDisabledcolor = "#808080"
menuSelectedcolor = "#6b1616"

class ScalableApp(tb.Window):
    """ Runs the UI for interactive mode. Derived from tkinter.
    """
    def __init__(self, uiparts: UIParts):
        super().__init__(themename="litera")

        global root
        root = self
        self.uiparts = uiparts

        # Track the last reported scaling to avoid infinite redraw loops
        self.current_dpi = None

        self.title(AppName + " " + AppVersion)
        self.geometry("980x750")

        # Split the window up into two horizontally arranged panes
        panedWindow = PanedWindow(self, orient=HORIZONTAL, bg=menubgnd)
        panedWindow.pack(side=LEFT, fill=BOTH, expand=True)

        # Create a frame for the left-hand menu pane
        menuFrame = Frame(panedWindow, bg=menubgnd)
        menuFrame.grid(row=0, column=0, rowspan=2, sticky=N)

        # Create a frame for the selected tournament window
        tournamentFrame = Frame(panedWindow, bg=tourneybgnd)
        tournamentFrame.grid(row=0, column=1, sticky=NW)

        # Create a frame for the right-hand content window
        contentFrame = Frame(panedWindow, bg=pagebgnd)
        contentFrame.grid(row=1, column=1, sticky=NW)

        # Create the parts of the UI window and construct them
        uiparts.mainMenu = menu(menuFrame)
        uiparts.tournamentDisplay = tournament.tournamentContent(tournamentFrame, memberDict)
        uiparts.mainDisplay = mainContent(contentFrame)
        uiparts.mainMenu.construct()
        uiparts.mainDisplay.construct(pagebgnd)
        uiparts.tournamentDisplay.construct(tourneybgnd)

        # Remember the last used display
        self.lastDisplay = uiparts.mainDisplay
        self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), True)

        # Create an options instance. We need this to pass in to the other UI components
        options.options(contentFrame, baseDir, uiparts)

        # Create the tournament class instance that holds the event data
        tournamentData = tournament.tournament(uiparts.tournamentDisplay, uiparts)

        # Create the remaining UI components
        selectTournament.selectTournament(contentFrame, tournamentData, uiparts)
        stratify.stratify(contentFrame, tournamentData, uiparts)
        webpage.webpage(contentFrame, tournamentData, uiparts)
        pdfresults.pdfresults(contentFrame, tournamentData, uiparts)
        masterpoints.masterpoints(contentFrame, tournamentData, uiparts)

        # Start the help server
        self.helpserver = helpserver.helpserver()

        # Set the window icon
        self.iconbitmap("resources\\PairsStratificationAppIco.ico")

        # Fall into a loop, processing user actions through the UI
        self.mainloop()

    def on_window_change(self, event):
        # Query the actual physical pixels per inch currently assigned to this window
        # 96 pixels per inch = 100% scale in Windows.
        current_pixels_per_inch = self.winfo_fpixels('1i')

        if self.current_dpi != current_pixels_per_inch:
            self.current_dpi = current_pixels_per_inch

            # Dynamically update Tk's internal font and asset renderer target
            scale_factor = current_pixels_per_inch / 96.0
            self.tk.call('tk', 'scaling', scale_factor)

    # Helper to highlight a link in the menu when the user hovers over it
    def highlightLink(self, event, widget, color):
        widget.config(fg=color)

    # Set of action functions that clears the main content and switches to another
    def showHome(self, event):
        self.lastDisplay.clearContent()
        self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), False)
        self.uiparts.mainDisplay.construct(pagebgnd)
        self.lastDisplay = self.uiparts.mainDisplay
        self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), True)

    def showSelect(self, event):
        self.lastDisplay.clearContent()
        self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), False)
        self.uiparts.selectTournamentDisplay.construct(pagebgnd)
        self.lastDisplay = self.uiparts.selectTournamentDisplay
        self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), True)

    def showStratify(self, event):
        if self.uiparts.mainMenu.linksEnabled:
            self.lastDisplay.clearContent()
            self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), False)
            self.uiparts.stratifyDisplay.construct(pagebgnd)
            self.lastDisplay = self.uiparts.stratifyDisplay
            self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), True)

    def showPrint(self, event):
        if self.uiparts.mainMenu.linksEnabled:
            self.lastDisplay.clearContent()
            self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), False)
            self.uiparts.pdfResultsDisplay.construct(pagebgnd)
            self.lastDisplay = self.uiparts.pdfResultsDisplay
            self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), True)

    def showMPFile(self, event):
        if self.uiparts.mainMenu.mpfileEnabled:
            self.lastDisplay.clearContent()
            self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), False)
            self.uiparts.masterpointsResultsDisplay.construct(pagebgnd)
            self.lastDisplay = self.uiparts.masterpointsResultsDisplay
            self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), True)

    def showWebpage(self, event):
        if self.uiparts.mainMenu.linksEnabled:
            self.lastDisplay.clearContent()
            self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), False)
            self.uiparts.webpageDisplay.construct(pagebgnd)
            self.lastDisplay = self.uiparts.webpageDisplay
            self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), True)

    def showOptions(self, event):
        self.lastDisplay.clearContent()
        self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), False)
        self.uiparts.options.construct(pagebgnd)
        self.lastDisplay = self.uiparts.options
        self.uiparts.mainMenu.setSelected(self.lastDisplay.getName(), True)

    def showHelp(self, event):
        self.helpserver.serveHelp()

class menu:
    """ Runs the menu UI.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
    """
    def __init__(self, frame: Frame):
        self.frame = frame
        self.homeMenuColor = self.selectMenuColor = self.optionsMenuColor = self.helpMenuColor = menucolor
        self.stratifyMenuColor = self.printMenuColor = self.writeFileMenuColor = self.webpageMenuColor = menuDisabledcolor
        self.linkHiliteColor = self.writeFileHiliteColor =  menuDisabledcolor
        self.mpfileEnabled = False
        self.linksEnabled = False

    def construct(self):
        global root
        self.spacerLabel = Label(self.frame, text="", bg=menubgnd)
        self.spacerLabel.grid(row=0, column=0, sticky=N, pady=2)
        self.homeLabel = Label(self.frame, text="Home", font=("Arial", 10, "underline", "bold"), justify='left', fg=self.homeMenuColor, bg=menubgnd)
        self.homeLabel.grid(row=1, column=0, sticky=W, padx=15, pady=5)
        self.selectLabel = Label(self.frame, text="Select Tournament", font=("Arial", 10, "underline", "bold"), justify='left', fg=self.selectMenuColor, bg=menubgnd)
        self.selectLabel.grid(row=2, column=0, sticky=W, padx=15, pady=5)
        self.stratifyLabel = Label(self.frame, text="Stratify Tournament", font=("Arial", 10, "underline", "bold"), justify='left', fg=self.stratifyMenuColor, bg=menubgnd)
        self.stratifyLabel.grid(row=3, column=0, sticky=W, padx=15, pady=5)
        self.printLabel = Label(self.frame, text="Print Results", font=("Arial", 10, "underline", "bold"), justify='left', fg=self.printMenuColor, bg=menubgnd)
        self.printLabel.grid(row=4, column=0, sticky=W, padx=15, pady=5)
        self.mpfileLabel = Label(self.frame, text="Write Results File", font=("Arial", 10, "underline", "bold"), justify='left', fg=self.writeFileMenuColor, bg=menubgnd)
        self.mpfileLabel.grid(row=5, column=0, sticky=W, padx=15, pady=5)
        self.webpageLabel = Label(self.frame, text="Stand-alone Webpage", font=("Arial", 10, "underline", "bold"), justify='left', fg=self.webpageMenuColor, bg=menubgnd)
        self.webpageLabel.grid(row=6, column=0, sticky=W, padx=15, pady=5)
        self.optionsLabel = Label(self.frame, text="Options", font=("Arial", 10, "underline", "bold"), justify='left', fg=self.optionsMenuColor, bg=menubgnd)
        self.optionsLabel.grid(row=7, column=0, sticky=W, padx=15, pady=5)
        self.helpLabel = Label(self.frame, text="Help", font=("Arial", 10, "underline", "bold"), justify='left', fg=self.helpMenuColor, bg=menubgnd)
        self.helpLabel.grid(row=8, column=0, sticky=W, padx=15, pady=25)
        self.homeLabel.bind("<Button-1>", root.showHome)
        self.homeLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.homeLabel, menuhilite)})
        self.homeLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.homeLabel, self.homeMenuColor)})
        self.selectLabel.bind("<Button-1>", root.showSelect)
        self.selectLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.selectLabel, menuhilite)})
        self.selectLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.selectLabel, self.selectMenuColor)})
        self.stratifyLabel.bind("<Button-1>", root.showStratify)
        self.stratifyLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.stratifyLabel, self.linkHiliteColor)})
        self.stratifyLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.stratifyLabel, self.stratifyMenuColor)})
        self.printLabel.bind("<Button-1>", root.showPrint)
        self.printLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.printLabel, self.linkHiliteColor)})
        self.printLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.printLabel, self.printMenuColor)})
        self.mpfileLabel.bind("<Button-1>", root.showMPFile)
        self.mpfileLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.mpfileLabel, self.writeFileHiliteColor)})
        self.mpfileLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.mpfileLabel, self.writeFileMenuColor)})
        self.webpageLabel.bind("<Button-1>", root.showWebpage)
        self.webpageLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.webpageLabel, self.linkHiliteColor)})
        self.webpageLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.webpageLabel, self.webpageMenuColor)})
        self.optionsLabel.bind("<Button-1>", root.showOptions)
        self.optionsLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.optionsLabel, menuhilite)})
        self.optionsLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.optionsLabel, self.optionsMenuColor)})
        self.helpLabel.bind("<Button-1>", root.showHelp)
        self.helpLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.helpLabel, menuhilite)})
        self.helpLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.helpLabel, self.helpMenuColor)})

    def enableMPFile(self, enable: bool):
        self.mpfileEnabled = enable
        if enable:
            self.writeFileMenuColor = menucolor
            self.writeFileHiliteColor = menuhilite
        else:
            self.writeFileMenuColor = menuDisabledcolor
            self.writeFileHiliteColor = menuDisabledcolor
        self.mpfileLabel.config(fg=self.writeFileMenuColor)

    def enableMenuItems(self, enable: bool):
        self.linksEnabled = enable
        if enable:
            self.stratifyMenuColor = self.printMenuColor = self.webpageMenuColor = menucolor
            self.linkHiliteColor = menuhilite
        else:
            self.stratifyMenuColor = self.printMenuColor = self.webpageMenuColor = menuDisabledcolor
            self.linkHiliteColor = menuDisabledcolor
        self.stratifyLabel.config(fg=self.stratifyMenuColor)
        self.printLabel.config(fg=self.printMenuColor)
        self.webpageLabel.config(fg=self.webpageMenuColor)

    def setSelected(self, menuItem:str, enabled: bool):
        if menuItem == 'home':
            self.homeMenuColor = menuSelectedcolor if enabled else menucolor
            self.homeLabel.config(fg=self.homeMenuColor)
        elif menuItem == 'select':
            self.selectMenuColor = menuSelectedcolor if enabled else menucolor
            self.selectLabel.config(fg=self.selectMenuColor)
        elif menuItem == 'stratify':
            self.stratifyMenuColor = menuSelectedcolor if enabled else menucolor
            self.stratifyLabel.config(fg=self.stratifyMenuColor)
        elif menuItem == 'print':
            self.printMenuColor = menuSelectedcolor if enabled else menucolor
            self.printLabel.config(fg=self.printMenuColor)
        elif menuItem == 'write':
            self.writeFileMenuColor = menuSelectedcolor if enabled else menucolor
            self.mpfileLabel.config(fg=self.writeFileMenuColor)
        elif menuItem == 'webpage':
            self.webpageMenuColor = menuSelectedcolor if enabled else menucolor
            self.webpageLabel.config(fg=self.webpageMenuColor)
        elif menuItem == 'options':
            self.optionsMenuColor = menuSelectedcolor if enabled else menucolor
            self.optionsLabel.config(fg=self.optionsMenuColor)

class mainContent(baseUIClass):
    """ Runs the Home UI.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
    """
    def __init__(self, frame: Frame):
        self.frame = frame

    def getName(self):
        return 'home'
    
    def construct(self, pagebgnd):
        self.spacerLabel1 = Label(self.frame, text="", bg=pagebgnd)
        self.spacerLabel1.grid(row=0, column=0, sticky=N, pady=2)
        self.homeLabel = Label(self.frame, text="Use Home to return to this page", font=("Arial", 10, "bold"), justify='left', bg=pagebgnd)
        self.homeLabel.grid(row=1, column=0, sticky=W, padx=20)
        self.spacerLabel2 = Label(self.frame, text="", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.spacerLabel2.grid(row=2, column=0, sticky=NW)
        self.selectLabel1 = Label(self.frame, text="Use Select Tournament to pick an already-scored tournament", font=("Arial", 10, "bold"), justify='left', bg=pagebgnd)
        self.selectLabel1.grid(row=3, column=0, sticky=W, padx=20)
        self.selectLabel2 = Label(self.frame, text="This program ONLY operates with PAIRS tournaments", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.selectLabel2.grid(row=4, column=0, sticky=W, padx=20)
        self.selectLabel3 = Label(self.frame, text="It operates on a USEBIO file created by your scoring program", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.selectLabel3.grid(row=5, column=0, sticky=W, padx=20)
        self.spacerLabel3 = Label(self.frame, text="", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.spacerLabel3.grid(row=6, column=0, sticky=NW)
        self.stratifyLabel1 = Label(self.frame, text="Use Stratify Tournament to stratify a tournament", font=("Arial", 10, "bold"), justify='left', bg=pagebgnd)
        self.stratifyLabel1.grid(row=7, column=0, sticky=SW, padx=20)
        self.stratifyLabel2 = Label(self.frame, text="This creates masterpoint awards for pairs below a certain ranking", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.stratifyLabel2.grid(row=8, column=0, sticky=W, padx=20)
        self.spacerLabel4 = Label(self.frame, text="", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.spacerLabel4.grid(row=9, column=0, sticky=NW)
        self.printLabel = Label(self.frame, text="Use Print Results to create a PDF of the results", font=("Arial", 10, "bold"), justify='left', bg=pagebgnd)
        self.printLabel.grid(row=10, column=0, sticky=SW, padx=20)
        self.spacerLabel5 = Label(self.frame, text="", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.spacerLabel5.grid(row=11, column=0, sticky=NW)
        self.writeLabel1 = Label(self.frame, text="Use Write Results File to create a new USEBIO file", font=("Arial", 10, "bold"), justify='left', bg=pagebgnd)
        self.writeLabel1.grid(row=12, column=0, sticky=SW, padx=20)
        self.writeLabel2 = Label(self.frame, text="This contains the stratified results in an uploadable format", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.writeLabel2.grid(row=13, column=0, sticky=SW, padx=20)
        self.spacerLabel6 = Label(self.frame, text="", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.spacerLabel6.grid(row=14, column=0, sticky=NW)
        self.webpageLabel1 = Label(self.frame, text="Use Stand-alone Webpage to create a results webpage", font=("Arial", 10, "bold"), justify='left', bg=pagebgnd)
        self.webpageLabel1.grid(row=15, column=0, sticky=W, padx=20)
        self.webpageLabel2 = Label(self.frame, text="This is useful if you do not upload to Bridgewebs or similar.", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.webpageLabel2.grid(row=16, column=0, sticky=W, padx=20)
        self.spacerLabel7 = Label(self.frame, text="", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.spacerLabel7.grid(row=17, column=0, sticky=NW)
        self.optionsLabel1 = Label(self.frame, text="Use Options to configure the utility", font=("Arial", 10, "bold"), justify='left', bg=pagebgnd)
        self.optionsLabel1.grid(row=18, column=0, sticky=W, padx=20)
        self.optionsLabel2 = Label(self.frame, text="You can set the default directories and stratification levels here.", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.optionsLabel2.grid(row=19, column=0, sticky=W, padx=20)
        self.spacerLabel8 = Label(self.frame, text="", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.spacerLabel8.grid(row=20, column=0, sticky=NW)
        self.helpLabel1 = Label(self.frame, text="Use Help to access the utility help", font=("Arial", 10, "bold"), justify='left', bg=pagebgnd)
        self.helpLabel1.grid(row=21, column=0, sticky=W, padx=20)
        self.helpLabel2 = Label(self.frame, text="We recommend you read the Home page of the help BEFORE starting.", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.helpLabel2.grid(row=22, column=0, sticky=W, padx=20)
        self.spacerLabel9 = Label(self.frame, text="", font=("Arial", 10), justify='left', bg=pagebgnd)
        self.spacerLabel9.grid(row=23, column=0, sticky=NW, padx=420, pady=200)
        
    def clearContent(self):
        self.spacerLabel9.destroy()
        self.helpLabel2.destroy()
        self.helpLabel1.destroy()
        self.spacerLabel8.destroy()
        self.optionsLabel2.destroy()
        self.optionsLabel1.destroy()
        self.spacerLabel7.destroy()
        self.webpageLabel2.destroy()
        self.webpageLabel1.destroy()
        self.spacerLabel6.destroy()
        self.writeLabel2.destroy()
        self.writeLabel1.destroy()
        self.spacerLabel5.destroy()
        self.printLabel.destroy()
        self.spacerLabel4.destroy()
        self.stratifyLabel2.destroy()
        self.stratifyLabel1.destroy()
        self.spacerLabel3.destroy()
        self.selectLabel3.destroy()
        self.selectLabel2.destroy()
        self.selectLabel1.destroy()
        self.spacerLabel2.destroy()
        self.homeLabel.destroy()
        self.spacerLabel1.destroy()

# Remember our CWD
baseDir = os.getcwd()

# Prevent failures due to the HTTP server logging to console
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

# Initialize argument parser
parser = argparse.ArgumentParser(description='Pairs Stratification Utility')
parser.add_argument('--dir', type=str, required=False,
                    help='Directory containing input USEBIO files for batch processing')
parser.add_argument('--out', type=str, required=False,
                    help='Directory to write output USEBIO files to when batch processing')
parser.add_argument('--pdf', type=str, required = False,
                    help='Directory to write PDF print file to when batch processing')
parser.add_argument('--strat1', type=str, required=False,
                    help='Masterpoints rank name for stratum 1')
parser.add_argument('--strat2', type=str, required=False,
                    help='Masterpoints rank name for stratum 2')
args = parser.parse_args()

# Create an options instance so we can load the MEMPAD data
optionsInstance = options.options(None, baseDir, None)
# Get the current mamber ranking from MEMPAD / cache
memberDict = readPlayersDB(True, optionsInstance)

def has_console():
    # If running inside VS Code, treat as NOT console
    if "VSCODE_PID" in os.environ or os.environ.get("TERM_PROGRAM") == "vscode":
        return False
    return ctypes.windll.kernel32.GetConsoleWindow() != 0

if has_console():
    inputDirectory = args.dir
    if inputDirectory is not None:
        inputDirectory = inputDirectory.rstrip('\\')
        outputDirectory = args.out
        if outputDirectory is not None:
            outputDirectory = outputDirectory.rstrip('\\')
        pdfDirectory = args.pdf
        if pdfDirectory is not None:
            pdfDirectory = pdfDirectory.rstrip('\\')
        strat1Level = args.strat1
        if strat1Level == None:
            strat1Level = 'None'
        strat2Level = args.strat2
        if strat2Level == None:
            strat2Level = 'None'

        # Create output directories, if needed
        if outputDirectory is not None and not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        if pdfDirectory is not None and not os.path.exists(pdfDirectory):
            os.makedirs(pdfDirectory)

        # Even though we're in batch mode, we need a UI parts holder.
        uiparts = UIParts()

        if strat1Level != 'None':
            stratInstance = stratify.stratify(None, None, uiparts)
            if not stratInstance.isValidLevel(strat1Level):
                print('Invalid stratum 1 level')
                quit()
            if strat2Level != 'None' and not stratInstance.isValidLevel(strat2Level):
                print('Invalid stratum 2 level')
                quit()

        usebioIn = Path(inputDirectory)
        for file in usebioIn.iterdir():
            if file.is_file():
                print(f'Processing {file}')
                tournamentData = tournament.tournament(tournament.tournamentContent(None, memberDict), uiparts)
                masterpoints.masterpoints(None, tournamentData, uiparts)
                stratInstance = stratify.stratify(None, tournamentData, uiparts)
                tournamentData.readerClass = USEBIO.USEBIO(tournamentData, None)
                try:
                    tournamentData.readerClass.read(file)
                    if strat1Level != 'None':
                        stratInstance.stratifyResults(True, strat1Level, strat2Level)
                    if outputDirectory is not None:
                        tournamentData.readerClass.write(outputDirectory + '\\' + tournamentData.getOutputFilename() + '.xml')
                    if pdfDirectory is not None:
                        pdfresults.pdfresults(None, tournamentData, uiparts).createPDF(pdfDirectory + '\\' + tournamentData.getOutputFilename() + '.pdf')
                except:
                    pass
        pass
    else:
        parser.print_help()
else:
    # Working interactively. Initialize the UI
    ScalableApp(UIParts())
    root.mainloop()
