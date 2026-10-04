###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# The Options UI and loading/saving the user options
###############################################################################
import json
import tkinter as tk
import ttkbootstrap as tb
import os
import filehandling
from baseclasses import baseUIClass
from uiparts import UIParts
from stratify import UIMPLevels
from autoscroll import AutoScrollbar
from mousewheel import MouseWheel
from appcolours import *

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
        
        self._config = {}
        self.resultsPathVar = tb.StringVar()
        self.outputsPathVar = tb.StringVar()
        self.PDFsPathVar = tb.StringVar()
        self.webpagesPathVar = tb.StringVar()
        self.hrecPathVar = tb.StringVar()
        self.webpTmplVar = tb.StringVar()
        self.stratum1ThresholdVar = tb.StringVar()
        self.stratum2ThresholdVar = tb.StringVar()

        try:
            # Open and read the JSON config file
            with open(os.path.join(self.baseDir, 'config.json'), 'r') as file:
                self._config = json.load(file)
        except:
            pass

        # Default the config if it's not valid
        config_good = True
        def _test_config_member(member: str) -> bool:
            nonlocal config_good
            if not member in self._config:
                self._config[member] = ''
                config_good = False

        _test_config_member('resultsdir')
        _test_config_member('masterpointsdir')
        _test_config_member('pdfsdir')
        _test_config_member('webpagesdir')
        _test_config_member('handrecordsdir')
        _test_config_member('webfiletemplate')
        _test_config_member('stratum1threshold')
        _test_config_member('stratum2threshold')

        if not config_good:
            self._save_json()
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

        # Enable vertical and horizontal expansion on row 0 / col 0
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1, minsize=0)
        self.frame.grid_columnconfigure(1, weight=0)

        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self.frame, highlightthickness=0, bg=self.pagebgnd)
        self.scrollbar = AutoScrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.pagebgnd)
        self.mousewheel = MouseWheel(self.frame, self.scrollable_frame, self.canvas)

        # Register scrollbar with MouseWheel manager
        self.mousewheel.register_scrollbar(self.scrollbar)

        # Create window inside canvas
        canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Standard Scroll Region Update
        def _update_scroll_region(event=None):
            self.scrollable_frame.update_idletasks()
            # Get the natural height required by the contents inside the green frame
            req_height = self.scrollable_frame.winfo_reqheight()
            
            # Cap the canvas height to either the content height or the maximum allowed limit
            capped_height = min(req_height, self.uiparts.scale_factor * 600)
            self.canvas.configure(height=capped_height, scrollregion=self.canvas.bbox("all"))

        # Stretch scrollable frame to match canvas width
        def _on_canvas_configure(event):
            self.canvas.itemconfig(canvas_window, width=event.width)

        # Bindings
        self.scrollable_frame.bind("<Configure>", _update_scroll_region)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Grid placement: Canvas in col 0, Scrollbar in col 1 (prevents overlap)
        self.canvas.grid(row=0, column=0, sticky="new")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        tk.Widget.lift(self.scrollbar)
        self.scrollable_frame.grid_columnconfigure(0, weight=1, minsize=self.uiparts.entry_width)

        self.labels = []

        self.saveButton = tb.Button(self.frame, text="Save", bootstyle="primary", width=10, state="disabled", command=self.SavePressed)
        self.resetButton = tb.Button(self.frame, text="Reset", bootstyle="primary", width=10, state="disabled", command=self.ResetPressed)
        self.labels.append(self.saveButton)
        self.labels.append(self.resetButton)

        label = tb.Label(self.scrollable_frame, text="Select the default input USEBIO results directory.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=1, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(self.uiparts.scaling["20"], 0))
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="This is where your scoring program outputs USEBIO XML files.", font=("Segoe UI", 10), justify='left')
        label.grid(row=2, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)
        label = tb.Button(self.scrollable_frame, text="Browse", bootstyle="primary", command=self.pickDefaultResultsDir)
        label.grid(row=3, column=0, sticky="w", padx=self.uiparts.scaling["20"], pady=self.uiparts.scaling["10"])
        self.labels.append(label)
        self.resultsPathVar.set(self._config['resultsdir'])
        self.resultsPathVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.scrollable_frame, textvariable=self.resultsPathVar, font=("Segoe UI", 10))
        label.grid(row=3, column=0, sticky="ew", padx=self.uiparts.scaling["100"])
        self.labels.append(label)

        label = tb.Label(self.scrollable_frame, text="Select the default output directory.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=4, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(self.uiparts.scaling["10"], 0))
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="Stratified USEBIO XML files are written here.", font=("Segoe UI", 10), justify='left')
        label.grid(row=5, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)
        label = tb.Button(self.scrollable_frame, text="Browse", bootstyle="primary", command=self.pickOutputsDir)
        label.grid(row=6, column=0, sticky="w", padx=self.uiparts.scaling["20"], pady=self.uiparts.scaling["10"])
        self.labels.append(label)
        self.outputsPathVar.set(self._config['masterpointsdir'])
        self.outputsPathVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.scrollable_frame, textvariable=self.outputsPathVar, font=("Segoe UI", 10))
        label.grid(row=6, column=0, sticky="ew", padx=self.uiparts.scaling["100"])
        self.labels.append(label)

        label = tb.Label(self.scrollable_frame, text="Select the default print file output directory.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=7, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(self.uiparts.scaling["10"], 0))
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="Printable PDF rankings files are written here.", font=("Segoe UI", 10), justify='left')
        label.grid(row=8, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)
        label = tb.Button(self.scrollable_frame, text="Browse", bootstyle="primary", command=self.pickPDFsDir)
        label.grid(row=9, column=0, sticky="w", padx=self.uiparts.scaling["20"], pady=self.uiparts.scaling["10"])
        self.labels.append(label)
        self.PDFsPathVar.set(self._config['pdfsdir'])
        self.PDFsPathVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.scrollable_frame, textvariable=self.PDFsPathVar, font=("Segoe UI", 10))
        label.grid(row=9, column=0, sticky="ew", padx=self.uiparts.scaling["100"])
        self.labels.append(label)

        label = tb.Label(self.scrollable_frame, text="Select the default web pages file output directory.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=10, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(self.uiparts.scaling["10"], 0))
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="Web page files are written here.", font=("Segoe UI", 10), justify='left')
        label.grid(row=11, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)
        label = tb.Button(self.scrollable_frame, text="Browse", bootstyle="primary", command=self.pickWebpagesDir)
        label.grid(row=12, column=0, sticky="w", padx=self.uiparts.scaling["20"], pady=self.uiparts.scaling["10"])
        self.labels.append(label)
        self.webpagesPathVar.set(self._config['webpagesdir'])
        self.webpagesPathVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.scrollable_frame, textvariable=self.webpagesPathVar, font=("Segoe UI", 10))
        label.grid(row=12, column=0, sticky="ew", padx=self.uiparts.scaling["100"])
        self.labels.append(label)

        label = tb.Label(self.scrollable_frame, text="Select the default hand records directory.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=13, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(self.uiparts.scaling["10"], 0))
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="This is where .PBN deal files are located (only used for web pages).", font=("Segoe UI", 10), justify='left')
        label.grid(row=14, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)
        label = tb.Button(self.scrollable_frame, text="Browse", bootstyle="primary", command=self.pickHandRecDir)
        label.grid(row=15, column=0, sticky="w", padx=self.uiparts.scaling["20"], pady=self.uiparts.scaling["10"])
        self.labels.append(label)
        self.hrecPathVar.set(self._config['handrecordsdir'])
        self.hrecPathVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.scrollable_frame, textvariable=self.hrecPathVar, font=("Segoe UI", 10))
        label.grid(row=15, column=0, sticky="ew", padx=self.uiparts.scaling["100"])
        self.labels.append(label)

        label = tb.Label(self.scrollable_frame, text="Select the webpage template to use.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=16, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(self.uiparts.scaling["10"], 0))
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="This allows you to customise the web page.", font=("Segoe UI", 10), justify='left')
        label.grid(row=17, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(0, self.uiparts.scaling["5"]))
        self.labels.append(label)
        label = tb.Button(self.scrollable_frame, text="Browse", bootstyle="primary", command=self.pickTemplate)
        label.grid(row=18, column=0, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)
        self.webpTmplVar.set(self._config['webfiletemplate'])
        self.webpTmplVar.trace_add("write", self.onParmChange)
        label = tb.Entry(self.scrollable_frame, textvariable=self.webpTmplVar, font=("Segoe UI", 10))
        label.grid(row=18, column=0, sticky="ew", padx=self.uiparts.scaling["100"])
        self.labels.append(label)

        label = tb.Label(self.scrollable_frame, text="Select the default stratification levels below.", font=("Segoe UI", 11, "bold"), justify='left')
        label.grid(row=19, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(self.uiparts.scaling["15"], 0))
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="You can supply different ones while stratifying a tournament", font=("Segoe UI", 10), justify='left')
        label.grid(row=20, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"], pady=(0, self.uiparts.scaling["5"]))
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="Stratum A is the overall rankings (all pairs).", font=("Segoe UI", 10), justify='left')
        label.grid(row=21, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="Stratum B is all pairs at or below the selected B rank.", font=("Segoe UI", 10), justify='left')
        label.grid(row=22, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)
        label = tb.Label(self.scrollable_frame, text="Stratum C is the subset of B at or below the selected C rank (\"None\" for just 1 stratum).", font=("Segoe UI", 10), justify='left')
        label.grid(row=23, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["20"])
        self.labels.append(label)

        label = tb.Label(self.scrollable_frame, text="Highest rank in Stratum B", font=("Segoe UI", 10), justify='right')
        label.grid(row=24, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["25"], pady=(self.uiparts.scaling["10"], 0))
        self.labels.append(label)
        self.stratum1ThresholdVar.set(self._config['stratum1threshold'])
        self.stratum1ThresholdVar.trace_add("write", self.onParmChange)
        self.cb1 = tb.Combobox(self.scrollable_frame, state="readonly", width=25, justify='left', textvariable=self.stratum1ThresholdVar)
        self.cb1['values'] = UIMPLevels[::-1]
        self.cb1.grid(row=24, column=0, padx=self.uiparts.scaling["200"], sticky="w", pady=(self.uiparts.scaling["10"], 0))
        self.labels.append(self.cb1)
        
        label = tb.Label(self.scrollable_frame, text="Highest rank in Stratum C", font=("Segoe UI", 10), justify='right')
        label.grid(row=25, column=0, columnspan=2, sticky="w", padx=self.uiparts.scaling["25"])
        self.labels.append(label)
        self.stratum2ThresholdVar.set(self._config['stratum2threshold'])
        self.stratum2ThresholdVar.trace_add("write", self.onParmChange)
        self.cb2 = tb.Combobox(self.scrollable_frame, state="readonly", width=25, justify='left', textvariable=self.stratum2ThresholdVar)
        self.cb2['values'] = UIMPLevels[::-1]
        self.cb2.grid(row=25, column=0, padx=self.uiparts.scaling["200"], sticky="w")
        self.labels.append(self.cb2)
        
        self.cb1.bind("<<ComboboxSelected>>", lambda e: self.setStratum2List())
        self.cb2.bind("<<ComboboxSelected>>", lambda e: self.setStratum1List())

        self.completeLabel = tb.Label(self.frame, text="", foreground=msg_completeColor, font=("Segoe UI", 10, "bold"), justify='left')
        self.completeLabel.place(x=self.uiparts.scale_factor * 300, y=self.uiparts.scale_factor * 670)

        self.saveButton.place(x=self.uiparts.scale_factor * 630, y=self.uiparts.scale_factor * 650)
        self.resetButton.place(x=self.uiparts.scale_factor * 730, y=self.uiparts.scale_factor * 650)

        self.setStratum2List()
        self.setStratum1List()

    def clearContent(self):
        """Safely tears down the options view, unbinds combobox events, and clears references."""
        # Unbind global application events
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.unbind_all("<MouseWheel>")

        # Destroy the traces
        if hasattr(self, "traces"):
            for var, mode, trace_id in self.traces:
                try:
                    # Remove the observer callback from Tcl/Tk
                    var.trace_remove(mode, trace_id)
                except tk.TclError:
                    # Catch error if variable/interp was already destroyed
                    pass
            self.traces.clear()

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

        # Destroy the scrollable frame contents
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.scrollable_frame.destroy()
        self.scrollbar.destroy()
        self.canvas.destroy()

        # Reset grid weights
        cols, rows = self.frame.grid_size()
        for i in range(cols):
            self.frame.grid_columnconfigure(i, weight=0)
        for i in range(rows):
            self.frame.grid_rowconfigure(i, weight=0)

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

    def pickPDFsDir(self):
        dirname = filehandling.findPDFsFileDirectory()
        if len(dirname) > 0:
            self.PDFsPathVar.set(dirname)

    def pickWebpagesDir(self):
        dirname = filehandling.findWebpagesFileDirectory()
        if len(dirname) > 0:
            self.webpagesPathVar.set(dirname)

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
        if not os.path.exists(self.config['webpagesdir']):
            os.makedirs(self.config['webpagesdir'])
        if not os.path.exists(self.config['masterpointsdir']):
            os.makedirs(self.config['masterpointsdir'])
        if not os.path.exists(self.config['pdfsdir']):
            os.makedirs(self.config['pdfsdir'])

    def onParmChange(self, *args):
        self.saveButton.configure(state="normal")
        self.resetButton.configure(state="normal")

    def SavePressed(self):
        # Disable the save/reset buttons
        self.saveButton.configure(state="disabled")
        self.resetButton.configure(state="disabled")

        # Populate our config from the form data
        self._config['resultsdir'] = self.resultsPathVar.get()
        self._config['masterpointsdir'] = self.outputsPathVar.get()
        self._config['pdfsdir'] = self.PDFsPathVar.get()
        self._config['webpagesdir'] = self.webpagesPathVar.get()
        self._config['handrecordsdir'] = self.hrecPathVar.get()
        self._config['webfiletemplate'] = self.webpTmplVar.get()
        self._config['stratum1threshold'] = self.stratum1ThresholdVar.get()
        self._config['stratum2threshold'] = self.stratum2ThresholdVar.get()

        self._save_json()
        self.completeLabel.config(text="Options saved.")

    def _save_json(self):
        # Write the modified configuration
        with open(os.path.join(self.baseDir, 'config.json'), 'w') as file:
            json.dump(self._config, file, indent=4)
        self.createOutputDirs()
    
    def ResetPressed(self):
        # Reread the JSON config file to effect the cancel
        with open(os.path.join(self.baseDir, 'config.json'), 'r') as file:
            self._config = json.load(file)
        self.clearContent()
        self.construct(self.pagebgnd)
