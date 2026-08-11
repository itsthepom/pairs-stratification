###############################################################################
# Pairs Stratification Program.
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
        self.changed = False

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

        self.labels = []

        label = tb.Label(self.frame, text="Select the default input USEBIO results directory.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 0))
        self.labels.append(label)
        label = tb.Label(self.frame, text="This is where your scoring program outputs USEBIO XML files.", font=("Segoe UI", 10), justify='left')
        label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Button(self.frame, text="Browse", bootstyle="primary", command=self.pickDefaultResultsDir)
        label.grid(row=3, column=0, sticky="w", padx=20, pady=10)
        self.labels.append(label)
        self.resultsPathVar = tb.StringVar()
        self.resultsPathVar.set(self._config['resultsdir'])
        self.resultsPathVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.frame, textvariable=self.resultsPathVar, width=102, font=("Segoe UI", 10))
        label.grid(row=3, column=0, sticky="w", padx=100)
        self.labels.append(label)

        label = tb.Label(self.frame, text="Select the default output directory.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 0))
        self.labels.append(label)
        label = tb.Label(self.frame, text="Files created by this program are written here.", font=("Segoe UI", 10), justify='left')
        label.grid(row=6, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Button(self.frame, text="Browse", bootstyle="primary", command=self.pickOutputsDir)
        label.grid(row=7, column=0, sticky="w", padx=20, pady=10)
        self.labels.append(label)
        self.outputsPathVar = tb.StringVar()
        self.outputsPathVar.set(self._config['outputsdir'])
        self.outputsPathVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.frame, textvariable=self.outputsPathVar, width=102, font=("Segoe UI", 10))
        label.grid(row=7, column=0, sticky="w", padx=100)
        self.labels.append(label)

        label = tb.Label(self.frame, text="Select the default hand records directory.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=9, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 0))
        self.labels.append(label)
        label = tb.Label(self.frame, text="This is where .PBN files are located.", font=("Segoe UI", 10), justify='left')
        label.grid(row=10, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Button(self.frame, text="Browse", bootstyle="primary", command=self.pickHandRecDir)
        label.grid(row=11, column=0, sticky="w", padx=20, pady=10)
        self.labels.append(label)
        self.hrecPathVar = tb.StringVar()
        self.hrecPathVar.set(self._config['handrecordsdir'])
        self.hrecPathVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.frame, textvariable=self.hrecPathVar, width=102, font=("Segoe UI", 10))
        label.grid(row=11, column=0, sticky="w", padx=100)
        self.labels.append(label)

        label = tb.Label(self.frame, text="Select the webpage template to use.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=13, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 0))
        self.labels.append(label)
        label = tb.Label(self.frame, text="This allows you to customise the webpage.", font=("Segoe UI", 10), justify='left')
        label.grid(row=14, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 5))
        self.labels.append(label)
        label = tb.Button(self.frame, text="Browse", bootstyle="primary", command=self.pickTemplate)
        label.grid(row=15, column=0, sticky="w", padx=20)
        self.labels.append(label)
        self.webpTmplVar = tb.StringVar()
        self.webpTmplVar.set(self._config['webfiletemplate'])
        self.webpTmplVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.frame, textvariable=self.webpTmplVar, width=102, font=("Segoe UI", 10))
        label.grid(row=15, column=0, sticky="w", padx=100)
        self.labels.append(label)

        label = tb.Label(self.frame, text="Select the default stratification levels below.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=17, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 0))
        self.labels.append(label)
        label = tb.Label(self.frame, text="You can supply different ones while stratifying a tournament", font=("Segoe UI", 10), justify='left')
        label.grid(row=18, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 5))
        self.labels.append(label)
        label = tb.Label(self.frame, text="Stratum A is the overall rankings (all pairs).", font=("Segoe UI", 10), justify='left')
        label.grid(row=19, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, text="Stratum B is all pairs at or below the selected B rank.", font=("Segoe UI", 10), justify='left')
        label.grid(row=20, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)
        label = tb.Label(self.frame, text="Stratum C is the subset of B at or below the selected C rank (\"None\" for just 1 stratum).", font=("Segoe UI", 10), justify='left')
        label.grid(row=21, column=0, columnspan=2, sticky="w", padx=20)
        self.labels.append(label)

        label = tb.Label(self.frame, text="Highest rank in Stratum B", font=("Segoe UI", 10), justify='right')
        label.grid(row=23, column=0, columnspan=2, sticky="w", padx=30, pady=(10, 0))
        self.labels.append(label)
        self.stratum1ThresholdVar = tb.StringVar()
        self.stratum1ThresholdVar.set(self._config['stratum1threshold'])
        self.stratum1ThresholdVar.trace_add("write", self.onParmChange)
        self.cb1 = tb.Combobox(self.frame, state="readonly", width=25, justify='left', textvariable=self.stratum1ThresholdVar)
        self.cb1['values'] = UIMPLevels[::-1]
        self.cb1.grid(row=23, column=0, padx=200, sticky="w", pady=(10, 0))
        self.labels.append(self.cb1)
        
        label = tb.Label(self.frame, text="Highest rank in Stratum C", font=("Segoe UI", 10), justify='right')
        label.grid(row=24, column=0, columnspan=2, sticky="w", padx=30)
        self.labels.append(label)
        self.stratum2ThresholdVar = tb.StringVar()
        self.stratum2ThresholdVar.set(self._config['stratum2threshold'])
        self.stratum2ThresholdVar.trace_add("write", self.onParmChange)
        self.cb2 = tb.Combobox(self.frame, state="readonly", width=25, justify='left', textvariable=self.stratum2ThresholdVar)
        self.cb2['values'] = UIMPLevels[::-1]
        self.cb2.grid(row=24, column=0, padx=200, sticky="w")
        self.labels.append(self.cb2)
        
        self.cb1.bind("<<ComboboxSelected>>", lambda e: self.setStratum2List())
        self.cb2.bind("<<ComboboxSelected>>", lambda e: self.setStratum1List())

        self.completeLabel = tb.Label(self.frame, text="", foreground=CompleteColor, font=("Segoe UI", 10, "bold"), justify='left')
        self.completeLabel.place(x=300, y=670)
    
        self.saveButton = tb.Button(self.frame, text="Save", bootstyle="primary", width=10, state="disabled", command=self.SavePressed)
        self.resetButton = tb.Button(self.frame, text="Reset", bootstyle="primary", width=10, state="disabled", command=self.ResetPressed)
        self.labels.append(self.saveButton)
        self.labels.append(self.resetButton)

        self.saveButton.place(x=630, y=650)
        self.resetButton.place(x=730, y=650)

        self.setStratum2List()
        self.setStratum1List()

    def clearContent(self):
        """Safely tears down the options view, unbinds combobox events, and clears references."""
        # Unbind combobox virtual events
        if hasattr(self, 'cb1') and self.cb1:
            try:
                self.cb1.unbind("<<ComboboxSelected>>")
            except Exception:
                pass

        if hasattr(self, 'cb2') and self.cb2:
            try:
                self.cb2.unbind("<<ComboboxSelected>>")
            except Exception:
                pass

        # Break button command references
        if hasattr(self, 'saveButton') and self.saveButton:
            try:
                self.saveButton.configure(command="")
            except Exception:
                pass

        if hasattr(self, 'resetButton') and self.resetButton:
            try:
                self.resetButton.configure(command="")
            except Exception:
                pass

        # Destroy the frame child entries, buttons, labels
        if hasattr(self, 'frame') and self.frame:
            for widget in self.frame.winfo_children():
                widget.destroy()

        # Clear list of widget references
        self.labels = []

        # Reset widget variables to None for Garbage Collection
        self.cb1 = None
        self.cb2 = None
        self.completeLabel = None
        self.saveButton = None
        self.resetButton = None

    def pickDefaultResultsDir(self):
        dirname = filehandling.findResultsFileDirectory()
        if len(dirname) > 0:
            self.resultsPathVar.set(dirname)

    def pickOutputsDir(self):
        dirname = filehandling.findOutputsFileDirectory()
        if len(dirname) > 0:
            self.outputsPathVar.set(dirname)

    def pickHandRecDir(self):
        dirname = filehandling.findHandRecordsFileDirectory()
        if len(dirname) > 0:
            self.hrecPathVar.set(dirname)

    def pickTemplate(self):
        filename = filehandling.openWebfileTemplate(os.getcwd())
        if len(filename) > 0:
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

    def onParmChange(self, *args):
        self.saveButton.configure(state="normal")
        self.resetButton.configure(state="normal")

    def SavePressed(self):
        # Disable the save/reset buttons
        self.saveButton.configure(state="disabled")
        self.resetButton.configure(state="disabled")

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
