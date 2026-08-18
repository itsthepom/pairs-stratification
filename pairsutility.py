###############################################################################
# Pairs Stratification Program.
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
import changeRanks
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
from appcolours import *
import applogger
import about

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

# Initialze the global logger
applogger.applogger()
applogger.applog.info("Application starting")

class ScalableApp(tb.Window):
    """ Runs the UI for interactive mode. Derived from tkinter.
    """
    def __init__(self, uiparts: UIParts):
        super().__init__(themename="litera")

        # Configure darker background and text for disabled TButton states
        self.style.configure("primary.TButton")
        self.style.map(
            "primary.TButton",
            background=[("disabled", btn_disabled_bg_color)],
            foreground=[("disabled", btn_disabled_fg_color)]
        )
        # Configure canvas frames
        self.style.configure("menu.TFrame", background=app_menubgnd)
        self.style.configure("main.TFrame", background=app_pagebgnd)
        self.style.configure("tourney.TFrame", background=app_tourneybgnd)

        global root
        root = self
        self.uiparts = uiparts
        self.uiparts.root = self

        # Track the last reported scaling to avoid infinite redraw loops
        self.current_dpi = None

        self.title(AppName + " " + AppVersion)
        self.geometry("1030x750")
        self.resizable(False, False)
        
        # Split the window up into two horizontally arranged panes
        panedWindow = PanedWindow(self, orient=HORIZONTAL, bg=app_menubgnd)
        panedWindow.pack(side=LEFT, fill=BOTH, expand=True)

        # Create a frame for the left-hand menu pane
        menuFrame = tb.Frame(panedWindow, style="menu.TFrame")
        panedWindow.add(menuFrame)

        rightContainer = tb.Frame(panedWindow)
        panedWindow.add(rightContainer)
        rightContainer.grid_rowconfigure(0, weight=0)
        rightContainer.grid_rowconfigure(1, weight=1)
        rightContainer.grid_columnconfigure(0, weight=0)
        rightContainer.grid_columnconfigure(1, weight=1)

        # Create a frame for the selected tournament window
        tournamentFrame = tb.Frame(rightContainer, style="tourney.TFrame")
        tournamentFrame.grid(row=0, column=1, sticky=NSEW)

        # Create a frame for the right-hand content window
        contentFrame = tb.Frame(rightContainer, style="main.TFrame")
        contentFrame.grid(row=1, column=1, sticky=NSEW)

        # Create the parts of the UI window and construct them
        uiparts.mainMenu = menu(menuFrame)
        uiparts.tournamentDisplay = tournament.tournamentContent(tournamentFrame, memberDict)
        uiparts.mainDisplay = mainContent(contentFrame)
        uiparts.mainDisplay.construct(app_pagebgnd)
        uiparts.tournamentDisplay.construct(app_tourneybgnd)

        # Create an options instance. We need this to pass in to the other UI components
        options.options(contentFrame, baseDir, uiparts)

        # Create the tournament class instance that holds the event data
        tournamentData = tournament.tournament(uiparts.tournamentDisplay, uiparts)

        # Create the remaining UI components
        selectTournament.selectTournament(contentFrame, tournamentData, uiparts)
        changeRanks.changeRanks(contentFrame, tournamentData, uiparts)
        stratify.stratify(contentFrame, tournamentData, uiparts)
        webpage.webpage(contentFrame, tournamentData, uiparts)
        pdfresults.pdfresults(contentFrame, tournamentData, uiparts)
        masterpoints.masterpoints(contentFrame, tournamentData, uiparts)
        about.about(uiparts)

        # Start up the menu
        uiparts.mainMenu.construct()
        self.uiparts.mainMenu.setSelected(uiparts.mainDisplay.getName(), True)

        # Remember the last used display
        self.uiparts.lastDisplay = uiparts.mainDisplay

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

    # Called to switch a page
    def showPage(self, menuItem: str):
        if self.uiparts.lastDisplay != None:
            if menuItem == 'home':
                self.uiparts.lastDisplay.clearContent()
                self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), False)
                self.uiparts.mainDisplay.construct(app_pagebgnd)
                self.uiparts.lastDisplay = self.uiparts.mainDisplay
                self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), True)
            elif menuItem == 'select':
                self.uiparts.lastDisplay.clearContent()
                self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), False)
                self.uiparts.selectTournamentDisplay.construct(app_pagebgnd)
                self.uiparts.lastDisplay = self.uiparts.selectTournamentDisplay
                self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), True)
            elif menuItem == 'changeranks':
                if self.uiparts.mainMenu.linksEnabled:
                    self.uiparts.lastDisplay.clearContent()
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), False)
                    self.uiparts.changeRanksDisplay.construct(app_pagebgnd)
                    self.uiparts.lastDisplay = self.uiparts.changeRanksDisplay
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), True)
            elif menuItem == 'stratify':
                if self.uiparts.mainMenu.linksEnabled:
                    self.uiparts.lastDisplay.clearContent()
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), False)
                    self.uiparts.stratifyDisplay.construct(app_pagebgnd)
                    self.uiparts.lastDisplay = self.uiparts.stratifyDisplay
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), True)
            elif menuItem == 'print':
                if self.uiparts.mainMenu.linksEnabled:
                    self.uiparts.lastDisplay.clearContent()
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), False)
                    self.uiparts.pdfResultsDisplay.construct(app_pagebgnd)
                    self.uiparts.lastDisplay = self.uiparts.pdfResultsDisplay
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), True)
            elif menuItem == 'write':
                if self.uiparts.mainMenu.mpfileEnabled:
                    self.uiparts.lastDisplay.clearContent()
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), False)
                    self.uiparts.masterpointsResultsDisplay.construct(app_pagebgnd)
                    self.uiparts.lastDisplay = self.uiparts.masterpointsResultsDisplay
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), True)
            elif menuItem == 'webpage':
                if self.uiparts.mainMenu.linksEnabled:
                    self.uiparts.lastDisplay.clearContent()
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), False)
                    self.uiparts.webpageDisplay.construct(app_pagebgnd)
                    self.uiparts.lastDisplay = self.uiparts.webpageDisplay
                    self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), True)
            elif menuItem == 'options':
                self.uiparts.lastDisplay.clearContent()
                self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), False)
                self.uiparts.options.construct(app_pagebgnd)
                self.uiparts.lastDisplay = self.uiparts.options
                self.uiparts.mainMenu.setSelected(self.uiparts.lastDisplay.getName(), True)

    # Display the help pages
    def showHelp(self, event):
        self.helpserver.serveHelp()

    # Show about box
    def showAbout(self, event):
        self.uiparts.about.show()

class menu:
    """ Runs the menu UI.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
    """
    def __init__(self, frame: Frame):
        self.frame = frame
        self.homeMenuColor = self.selectMenuColor = self.optionsMenuColor = self.helpMenuColor = self.aboutMenuColor = app_menucolor
        self.stratifyMenuColor = self.printMenuColor = self.writeFileMenuColor = self.webpageMenuColor = self.changeRanksMenuColor = app_menuDisabledcolor
        self.linkHiliteColor = self.writeFileHiliteColor =  app_menuDisabledcolor
        self.mpfileEnabled = False
        self.linksEnabled = False

    def construct(self):
        global root
        self.spacerLabel = Label(self.frame, text="", bg=app_menubgnd)
        self.spacerLabel.grid(row=0, column=0, sticky=N, pady=2)
        self.homeLabel = Label(self.frame, text="Home", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.homeMenuColor, bg=app_menubgnd)
        self.homeLabel.grid(row=1, column=0, sticky=W, padx=(15, 22), pady=5)
        self.selectLabel = Label(self.frame, text="Select Tournament", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.selectMenuColor, bg=app_menubgnd)
        self.selectLabel.grid(row=2, column=0, sticky=W, padx=(15, 22), pady=5)
        self.changeRanksLabel = Label(self.frame, text="Change Player Ranks", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.changeRanksMenuColor, bg=app_menubgnd)
        self.changeRanksLabel.grid(row=3, column=0, sticky=W, padx=(15, 22), pady=5)
        self.stratifyLabel = Label(self.frame, text="Stratify Tournament", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.stratifyMenuColor, bg=app_menubgnd)
        self.stratifyLabel.grid(row=4, column=0, sticky=W, padx=(15, 22), pady=5)
        self.printLabel = Label(self.frame, text="Print Results", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.printMenuColor, bg=app_menubgnd)
        self.printLabel.grid(row=5, column=0, sticky=W, padx=(15, 22), pady=5)
        self.mpfileLabel = Label(self.frame, text="Write Results File", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.writeFileMenuColor, bg=app_menubgnd)
        self.mpfileLabel.grid(row=6, column=0, sticky=W, padx=(15, 22), pady=5)
        self.webpageLabel = Label(self.frame, text="Stand-alone Webpage", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.webpageMenuColor, bg=app_menubgnd)
        self.webpageLabel.grid(row=7, column=0, sticky=W, padx=(15, 22), pady=5)
        self.optionsLabel = Label(self.frame, text="Options", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.optionsMenuColor, bg=app_menubgnd)
        self.optionsLabel.grid(row=8, column=0, sticky=W, padx=(15, 22), pady=5)
        self.helpLabel = Label(self.frame, text="Help", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.helpMenuColor, bg=app_menubgnd)
        self.helpLabel.grid(row=9, column=0, sticky=W, padx=(15, 22), pady=(350, 5))
        self.aboutLabel = Label(self.frame, text="About", font=("Segoe UI", 10, "underline", "bold"), justify='left', fg=self.helpMenuColor, bg=app_menubgnd)
        self.aboutLabel.grid(row=10, column=0, sticky=W, padx=(15, 22), pady=5)

        self.homeLabel.bind("<Button-1>", lambda e: root.showPage('home'))
        self.homeLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.homeLabel, app_menuhilite)})
        self.homeLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.homeLabel, self.homeMenuColor)})
        self.selectLabel.bind("<Button-1>", lambda e: root.showPage('select'))
        self.selectLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.selectLabel, app_menuhilite)})
        self.selectLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.selectLabel, self.selectMenuColor)})
        self.changeRanksLabel.bind("<Button-1>", lambda e: root.showPage('changeranks'))
        self.changeRanksLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.changeRanksLabel, self.linkHiliteColor)})
        self.changeRanksLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.changeRanksLabel, self.changeRanksMenuColor)})
        self.stratifyLabel.bind("<Button-1>", lambda e: root.showPage('stratify'))
        self.stratifyLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.stratifyLabel, self.linkHiliteColor)})
        self.stratifyLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.stratifyLabel, self.stratifyMenuColor)})
        self.printLabel.bind("<Button-1>", lambda e: root.showPage('print'))
        self.printLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.printLabel, self.linkHiliteColor)})
        self.printLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.printLabel, self.printMenuColor)})
        self.mpfileLabel.bind("<Button-1>", lambda e: root.showPage('write'))
        self.mpfileLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.mpfileLabel, self.writeFileHiliteColor)})
        self.mpfileLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.mpfileLabel, self.writeFileMenuColor)})
        self.webpageLabel.bind("<Button-1>", lambda e: root.showPage('webpage'))
        self.webpageLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.webpageLabel, self.linkHiliteColor)})
        self.webpageLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.webpageLabel, self.webpageMenuColor)})
        self.optionsLabel.bind("<Button-1>", lambda e: root.showPage('options'))
        self.optionsLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.optionsLabel, app_menuhilite)})
        self.optionsLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.optionsLabel, self.optionsMenuColor)})
        self.helpLabel.bind("<Button-1>", root.showHelp)
        self.helpLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.helpLabel, app_menuhilite)})
        self.helpLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.helpLabel, self.helpMenuColor)})
        self.aboutLabel.bind("<Button-1>", root.showAbout)
        self.aboutLabel.bind("<Enter>", lambda e: {root.highlightLink(e, self.aboutLabel, app_menuhilite)})
        self.aboutLabel.bind("<Leave>", lambda e: {root.highlightLink(e, self.aboutLabel, self.aboutMenuColor)})

    def enableMPFile(self, enable: bool):
        self.mpfileEnabled = enable
        if enable:
            self.writeFileMenuColor = app_menucolor
            self.writeFileHiliteColor = app_menuhilite
        else:
            self.writeFileMenuColor = app_menuDisabledcolor
            self.writeFileHiliteColor = app_menuDisabledcolor
        self.mpfileLabel.config(fg=self.writeFileMenuColor)

    def enableMenuItems(self, enable: bool):
        self.linksEnabled = enable
        if enable:
            self.stratifyMenuColor = self.printMenuColor = self.webpageMenuColor = self.changeRanksMenuColor = app_menucolor
            self.linkHiliteColor = app_menuhilite
        else:
            self.changeRanksMenuColor = self.stratifyMenuColor = self.printMenuColor = self.webpageMenuColor = app_menuDisabledcolor
            self.linkHiliteColor = app_menuDisabledcolor
        self.changeRanksLabel.config(fg=self.changeRanksMenuColor)
        self.stratifyLabel.config(fg=self.stratifyMenuColor)
        self.printLabel.config(fg=self.printMenuColor)
        self.webpageLabel.config(fg=self.webpageMenuColor)

    def setSelected(self, menuItem:str, enabled: bool):
        if menuItem == 'home':
            self.homeMenuColor = app_menuSelectedcolor if enabled else app_menucolor
            self.homeLabel.config(fg=self.homeMenuColor)
        elif menuItem == 'select':
            self.selectMenuColor = app_menuSelectedcolor if enabled else app_menucolor
            self.selectLabel.config(fg=self.selectMenuColor)
        elif menuItem == 'changeranks':
            self.changeRanksMenuColor = app_menuSelectedcolor if enabled else app_menucolor
            self.changeRanksLabel.config(fg=self.changeRanksMenuColor)
        elif menuItem == 'stratify':
            self.stratifyMenuColor = app_menuSelectedcolor if enabled else app_menucolor
            self.stratifyLabel.config(fg=self.stratifyMenuColor)
        elif menuItem == 'print':
            self.printMenuColor = app_menuSelectedcolor if enabled else app_menucolor
            self.printLabel.config(fg=self.printMenuColor)
        elif menuItem == 'write':
            self.writeFileMenuColor = app_menuSelectedcolor if enabled else app_menucolor
            self.mpfileLabel.config(fg=self.writeFileMenuColor)
        elif menuItem == 'webpage':
            self.webpageMenuColor = app_menuSelectedcolor if enabled else app_menucolor
            self.webpageLabel.config(fg=self.webpageMenuColor)
        elif menuItem == 'options':
            self.optionsMenuColor = app_menuSelectedcolor if enabled else app_menucolor
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
        self.labels = []
        label = Label(self.frame, text="Use Home to return to this page", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=1, column=0, sticky=W, padx=20, pady=(20, 0))
        self.labels.append(label)

        label = Label(self.frame, text="Use Select Tournament to pick an already-scored tournament", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=2, column=0, sticky=W, padx=20, pady=(15, 0))
        self.labels.append(label)

        label = Label(self.frame, text="This program ONLY operates with PAIRS tournaments.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=3, column=0, sticky=W, padx=20)
        self.labels.append(label)

        label = Label(self.frame, text="It operates on a USEBIO file created by your scoring program.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=4, column=0, sticky=W, padx=20)
        self.labels.append(label)

        label = Label(self.frame, text="Use Change Player Ranks to modify the stratification rank of a pair", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=5, column=0, sticky=SW, padx=20, pady=(15, 0))
        self.labels.append(label)

        label = Label(self.frame, text="This allows you to adjust the rankings of pairs within the stratification.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=6, column=0, sticky=W, padx=20)
        self.labels.append(label)

        label = Label(self.frame, text="Use Stratify Tournament to stratify a tournament", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=7, column=0, sticky=SW, padx=20, pady=(15, 0))
        self.labels.append(label)

        label = Label(self.frame, text="This creates masterpoint awards for pairs below a certain ranking.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=8, column=0, sticky=W, padx=20)
        self.labels.append(label)

        label = Label(self.frame, text="Use Print Results to create a PDF of the results", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=9, column=0, sticky=SW, padx=20, pady=(15, 0))
        self.labels.append(label)

        label = Label(self.frame, text="You can pin this on your club notice board or use it to see the stratification.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=10, column=0, sticky=SW, padx=20)
        self.labels.append(label)

        label = Label(self.frame, text="Use Write Results File to create a new USEBIO file", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=11, column=0, sticky=SW, padx=20, pady=(15, 0))
        self.labels.append(label)

        label = Label(self.frame, text="This contains the stratified results in an uploadable format.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=12, column=0, sticky=SW, padx=20)
        self.labels.append(label)

        label = Label(self.frame, text="Use Stand-alone Webpage to create a results webpage", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=13, column=0, sticky=W, padx=20, pady=(15, 0))
        self.labels.append(label)

        label = Label(self.frame, text="This is useful if you do not upload to Bridgewebs or similar and have your own website.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=14, column=0, sticky=W, padx=20)
        self.labels.append(label)

        label = Label(self.frame, text="Use Options to configure the program", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=15, column=0, sticky=W, padx=20, pady=(15, 0))
        self.labels.append(label)

        label = Label(self.frame, text="You can set the default directories and stratification levels here.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=16, column=0, sticky=W, padx=20)
        self.labels.append(label)

        label = Label(self.frame, text="Use Help to access the program help", font=("Segoe UI", 11, "bold"), justify='left', bg=pagebgnd)
        label.grid(row=17, column=0, sticky=W, padx=20, pady=(15, 0))
        self.labels.append(label)

        label = Label(self.frame, text="We recommend you read the Home page of the help BEFORE starting.", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=18, column=0, sticky=W, padx=20)
        self.labels.append(label)
        
        label = Label(self.frame, text="", font=("Segoe UI", 10), justify='left', bg=pagebgnd)
        label.grid(row=19, column=0, sticky=NW, padx=420, pady=200)
        self.labels.append(label)
        
    def clearContent(self):
        """Destroys all UI widgets and clears python references for the home view."""
        # Destroy all child widgets inside self.frame
        if hasattr(self, 'frame') and self.frame:
            for widget in self.frame.winfo_children():
                widget.destroy()
        self.labels = []

# Remember our CWD
baseDir = os.getcwd()

# Prevent failures due to the HTTP server logging to console
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

# Initialize argument parser
parser = argparse.ArgumentParser(description='Pairs Stratification Program')
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
                        tournamentData.readerClass.write(tournamentData.eventType, outputDirectory + '\\' + tournamentData.getOutputFilename() + '.xml')
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
