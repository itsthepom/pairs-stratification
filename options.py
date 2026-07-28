###############################################################################
# Pairs Stratification Utility.
# Copyright Steve Pomeroy 2026
#
# The Options UI and loading/saving the user options
###############################################################################
import json
import ttkbootstrap as tb
import os
import filehandling
from baseclasses import baseUIClass
from uiparts import UIParts
from stratify import UIMPLevels

CompleteColor = "#44880C"

class options(baseUIClass):
    """ Runs the UI to allow configuration of options and loads/saves the options.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
            baseDir(str): directory where the config.json options settings is.
    """
    def __init__(self, frame, baseDir, uiparts: UIParts):
        self.frame = frame
        self.baseDir = baseDir
        self.uiparts = uiparts
        if uiparts != None:
            uiparts.options = self
        # Open and read the JSON config file
        with open(os.path.join(self.baseDir, 'config.json'), 'r') as file:
          self._config = json.load(file)
        # Set up the outputs dir
        self.outputsdir = self._config['outputsdir']
        if not self.outputsdir is None:
            if not self.outputsdir.endswith('/') or not self.outputsdir.endswith('\\'):
                self.outputsdir = self.outputsdir + '/'

    def getName(self):
        return 'options'
    
    @property
    def config(self):
        return self._config
    
    def getDirectory(self, configKey):
        """ Gets a directory name from the options.

            Args:
                configKey(str): Configuration settings key for the desired directory.
        """
        self.createOutputDirs()
        configDir = self._config[configKey]
        if not configDir is None:
            if not configDir.endswith('/') or not configDir.endswith('\\'):
                configDir = configDir + '/'
        return configDir

    def construct(self, pagebgnd):
        self.pagebgnd = pagebgnd
        self.spacerLabel6 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel6.grid(row=0, column=0, columnspan=2, sticky="nw")

        self.resultsDirLabel1 = tb.Label(self.frame, text="Select the default input USEBIO results directory.", font=("Arial", 10, "bold"), justify='left')
        self.resultsDirLabel1.grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
        self.resultsDirLabel2 = tb.Label(self.frame, text="This is where your scoring program outputs USEBIO XML files.", font=("Arial", 10), justify='left')
        self.resultsDirLabel2.grid(row=2, column=0, columnspan=2, sticky="w", padx=20)
        self.browseButton1 = tb.Button(self.frame, text="Browse", bootstyle="primary", command=self.pickDefaultResultsDir)
        self.browseButton1.grid(row=3, column=0, sticky="w", padx=20, pady=10)
        self.resultsPathVar = tb.StringVar()
        self.resultsPathVar.set(self._config['resultsdir'])
        self.resultsPathEntry = tb.Entry(self.frame, textvariable=self.resultsPathVar, width=95, font=("Arial", 10))
        self.resultsPathEntry.grid(row=3, column=0, sticky="w", padx=100)

        self.spacerLabel5 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel5.grid(row=4, column=0, columnspan=2, sticky="nw")

        self.outputsDirLabel1 = tb.Label(self.frame, text="Select the default output directory.", font=("Arial", 10, "bold"), justify='left')
        self.outputsDirLabel1.grid(row=5, column=0, columnspan=2, sticky="w", padx=20)
        self.outputsDirLabel2 = tb.Label(self.frame, text="Files created by this utility are written here.", font=("Arial", 10), justify='left')
        self.outputsDirLabel2.grid(row=6, column=0, columnspan=2, sticky="w", padx=20)
        self.browseButton2 = tb.Button(self.frame, text="Browse", bootstyle="primary", command=self.pickOutputsDir)
        self.browseButton2.grid(row=7, column=0, sticky="w", padx=20, pady=10)
        self.outputsPathVar = tb.StringVar()
        self.outputsPathVar.set(self._config['outputsdir'])
        self.outputsPathEntry = tb.Entry(self.frame, textvariable=self.outputsPathVar, width=95, font=("Arial", 10))
        self.outputsPathEntry.grid(row=7, column=0, sticky="w", padx=100)

        self.spacerLabel4 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel4.grid(row=8, column=0, columnspan=2, sticky="nw")
        
        self.hRecDirLabel1 = tb.Label(self.frame, text="Select the default hand records directory.", font=("Arial", 10, "bold"), justify='left')
        self.hRecDirLabel1.grid(row=9, column=0, columnspan=2, sticky="w", padx=20)
        self.hRecDirLabel2 = tb.Label(self.frame, text="This is where .PBN files are located.", font=("Arial", 10), justify='left')
        self.hRecDirLabel2.grid(row=10, column=0, columnspan=2, sticky="w", padx=20)
        self.browseButton3 = tb.Button(self.frame, text="Browse", bootstyle="primary", command=self.pickHandRecDir)
        self.browseButton3.grid(row=11, column=0, sticky="w", padx=20, pady=10)
        self.hrecPathVar = tb.StringVar()
        self.hrecPathVar.set(self._config['handrecordsdir'])
        self.hRecPathEntry = tb.Entry(self.frame, textvariable=self.hrecPathVar, width=95, font=("Arial", 10))
        self.hRecPathEntry.grid(row=11, column=0, sticky="w", padx=100)

        self.spacerLabel3 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel3.grid(row=12, column=0, columnspan=2, sticky="nw")
        
        self.webpageLabel1 = tb.Label(self.frame, text="Select the webpage template to use.", font=("Arial", 10, "bold"), justify='left')
        self.webpageLabel1.grid(row=13, column=0, columnspan=2, sticky="w", padx=20)
        self.webpageLabel2 = tb.Label(self.frame, text="This allows you to customise the webpage.", font=("Arial", 10), justify='left')
        self.webpageLabel2.grid(row=14, column=0, columnspan=2, sticky="w", padx=20)
        self.browseButton4 = tb.Button(self.frame, text="Browse", bootstyle="primary", command=self.pickTemplate)
        self.browseButton4.grid(row=15, column=0, sticky="w", padx=20, pady=10)
        self.webpTmplVar = tb.StringVar()
        self.webpTmplVar.set(self._config['webfiletemplate'])
        self.webpTmplEntry = tb.Entry(self.frame, textvariable=self.webpTmplVar, width=95, font=("Arial", 10))
        self.webpTmplEntry.grid(row=15, column=0, sticky="w", padx=100)

        self.spacerLabel2 = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel2.grid(row=16, column=0, columnspan=2, sticky="nw")
        
        self.stratLevelsLabel1 = tb.Label(self.frame, text="Select the default stratification levels below.", font=("Arial", 10, "bold"), justify='left')
        self.stratLevelsLabel1.grid(row=17, column=0, columnspan=2, sticky="w", padx=20)
        self.stratLevelsLabel2 = tb.Label(self.frame, text="You can supply different ones while stratifying a tournament", font=("Arial", 10), justify='left')
        self.stratLevelsLabel2.grid(row=18, column=0, columnspan=2, sticky="w", padx=20)
        self.stratLevelsLabel3 = tb.Label(self.frame, text="Stratum A is the overall rankings (all pairs).", font=("Arial", 10), justify='left')
        self.stratLevelsLabel3.grid(row=19, column=0, columnspan=2, sticky="w", padx=20)
        self.stratLevelsLabel4 = tb.Label(self.frame, text="Stratum B is all pairs at or below the selected B rank.", font=("Arial", 10), justify='left')
        self.stratLevelsLabel4.grid(row=20, column=0, columnspan=2, sticky="w", padx=20)
        self.stratLevelsLabel5 = tb.Label(self.frame, text="Stratum C is the subset of B at or below the selected C rank (\"None\" for just 1 stratum).", font=("Arial", 10), justify='left')
        self.stratLevelsLabel5.grid(row=21, column=0, columnspan=2, sticky="w", padx=20)

        self.spacerLabel1 = tb.Label(self.frame, text="", font=("Arial", 1), justify='left')
        self.spacerLabel1.grid(row=22, column=0, columnspan=2, sticky="nw", pady=0)

        self.stratLevelsLabel6 = tb.Label(self.frame, text="Highest rank in Stratum B", font=("Arial", 10), justify='right')
        self.stratLevelsLabel6.grid(row=23, column=0, columnspan=2, sticky="w", padx=30)
        self.stratum1ThresholdVar = tb.StringVar()
        self.stratum1ThresholdVar.set(self._config['stratum1threshold'])
        self.cb1 = tb.Combobox(self.frame, width=25, justify='left', textvariable=self.stratum1ThresholdVar)
        self.cb1['values'] = UIMPLevels[::-1]
        self.cb1.grid(row=23, column=0, padx=200, sticky="w")

        self.stratLevelsLabel7 = tb.Label(self.frame, text="Highest rank in Stratum C", font=("Arial", 10), justify='right')
        self.stratLevelsLabel7.grid(row=24, column=0, columnspan=2, sticky="w", padx=30)
        self.stratum2ThresholdVar = tb.StringVar()
        self.stratum2ThresholdVar.set(self._config['stratum2threshold'])
        self.cb2 = tb.Combobox(self.frame, width=25, justify='left', textvariable=self.stratum2ThresholdVar)
        self.cb2['values'] = UIMPLevels[::-1]
        self.cb2.grid(row=24, column=0, padx=200, sticky="w")
        self.cb1.bind("<<ComboboxSelected>>", lambda e: self.setStratum2List())
        self.cb2.bind("<<ComboboxSelected>>", lambda e: self.setStratum1List())

        self.completeLabel = tb.Label(self.frame, text="", foreground=CompleteColor, font=("Arial", 10, "bold"), justify='left')
        self.completeLabel.place(x=300, y=650)
    
        self.spacerLabel = tb.Label(self.frame, text="", font=("Arial", 10), justify='left')
        self.spacerLabel.grid(row=26, column=0, columnspan=2, sticky="nw", padx=420, pady=200)
        
        self.saveButton = tb.Button(self.frame, text="Save", bootstyle="primary", width=10, command=self.SavePressed)
        self.cancelButton = tb.Button(self.frame, text="Reset", bootstyle="primary", width=10, command=self.ResetPressed)

        self.saveButton.place(x=590, y=650)
        self.cancelButton.place(x=690, y=650)

        self.setStratum2List()
        self.setStratum1List()

    def clearContent(self):
        self.cancelButton.destroy()
        self.saveButton.destroy()
        self.spacerLabel.destroy()
        self.completeLabel.destroy()
        self.cb2.destroy()
        self.stratLevelsLabel7.destroy()
        self.cb1.destroy()
        self.stratLevelsLabel6.destroy()
        self.spacerLabel1.destroy()
        self.stratLevelsLabel5.destroy()
        self.stratLevelsLabel4.destroy()
        self.stratLevelsLabel3.destroy()
        self.stratLevelsLabel2.destroy()
        self.stratLevelsLabel1.destroy()
        self.spacerLabel2.destroy()
        self.webpTmplEntry.destroy()
        self.browseButton4.destroy()
        self.webpageLabel2.destroy()
        self.webpageLabel1.destroy()
        self.spacerLabel3.destroy()
        self.hRecPathEntry.destroy()
        self.browseButton3.destroy()
        self.hRecDirLabel2.destroy()
        self.hRecDirLabel1.destroy()
        self.spacerLabel4.destroy()
        self.outputsPathEntry.destroy()
        self.browseButton2.destroy()
        self.outputsDirLabel2.destroy()
        self.outputsDirLabel1.destroy()
        self.spacerLabel5.destroy()
        self.resultsPathEntry.destroy()
        self.browseButton1.destroy()
        self.resultsDirLabel2.destroy()
        self.resultsDirLabel1.destroy()
        self.spacerLabel6.destroy()

    def pickDefaultResultsDir(self):
        dirname = filehandling.findResultsFileDirectory()
        self.resultsPathVar.set(dirname)

    def pickOutputsDir(self):
        dirname = filehandling.findOutputsFileDirectory()
        self.outputsPathVar.set(dirname)

    def pickHandRecDir(self):
        dirname = filehandling.findHandRecordsFileDirectory()
        self.hrecPathVar.set(dirname)

    def pickTemplate(self):
        filename = filehandling.openWebfileTemplate(os.getcwd())
        self.webpTmplVar.set(filename)

    def setStratum2List(self):
        # Modify the array used for the stratum 2 combobox so that they can only pick a lower level.
        stratum1Index = UIMPLevels.index(self.stratum1ThresholdVar.get())
        stratum2Levels = UIMPLevels[0:stratum1Index]
        self.cb2['values'] = stratum2Levels[::-1]

    def setStratum1List(self):
        # Modify the array usedfor the stratum 1 combobox so that they can only pick a higher level.
        stratum2Index = UIMPLevels.index(self.stratum2ThresholdVar.get())
        stratum1Levels = UIMPLevels[stratum2Index:]
        self.cb1['values'] = stratum1Levels[::-1]

    def createOutputDirs(self):
        if not self.outputsdir is None:
            if not os.path.exists(self.outputsdir):
                os.makedirs(self.outputsdir)
            if not os.path.exists(self.outputsdir + self.config['webpagesdir']):
                os.makedirs(self.outputsdir + self.config['webpagesdir'])
            if not os.path.exists(self.outputsdir + self.config['masterpointsdir']):
                os.makedirs(self.outputsdir + self.config['masterpointsdir'])
            if not os.path.exists(self.outputsdir + self.config['pdfsdir']):
                os.makedirs(self.outputsdir + self.config['pdfsdir'])

    def SavePressed(self):
        # Populate our config from the form data
        self._config['resultsdir'] = self.resultsPathVar.get()
        self._config['outputsdir'] = self.outputsPathVar.get()
        self._config['handrecordsdir'] = self.hrecPathVar.get()
        self._config['webfiletemplate'] = self.webpTmplVar.get()
        self._config['stratum1threshold'] = self.stratum1ThresholdVar.get()
        self._config['stratum2threshold'] = self.stratum2ThresholdVar.get()

        # Write the modified configuration
        with open(os.path.join(self.baseDir, 'config.json'), 'w') as file:
            json.dump(self._config, file, indent=4)
        # Set up the outputs dir
        self.outputsdir = self._config['outputsdir']
        if not self.outputsdir is None:
            if not self.outputsdir.endswith('/') or not self.outputsdir.endswith('\\'):
                self.outputsdir = self.outputsdir + '/'
        self.createOutputDirs()
        self.completeLabel.config(text="Options saved.")
    
    def ResetPressed(self):
        # Reread the JSON config file to effect the cancel
        with open(os.path.join(self.baseDir, 'config.json'), 'r') as file:
            self._config = json.load(file)
        self.clearContent()
        self.construct(self.pagebgnd)
