###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# User interface to allow change of auto-assigned ranks
###############################################################################
from tkinter import ttk

from baseclasses import baseUIClass
from uiparts import UIParts
import tkinter as tk
import ttkbootstrap as tb
from stratify import UIMPLevels
from autoscroll import AutoScrollbar
from itertools import chain
from mousewheel import MouseWheel
from coloredcombo import ColoredCombo

class changeRanks(baseUIClass):
    """ Runs a UI to allow the user to change player ranks.

        Args:
            frame(Frame): tkinter Frame to display the UI in.
            tournamentData(tournament): tournamentData instance holding the event data.
            uiparts(UIParts): Holds the UI components.
    """
    def __init__(self, frame: tb.Frame, tournamentData, uiparts: UIParts):
        self.frame = frame
        self.tournamentData = tournamentData
        self.uiparts = uiparts
        uiparts.changeRanksDisplay = self

    def getName(self):
        return 'changeranks'

    def construct(self, pagebgnd):
        self.pagebgnd = pagebgnd

        # Configure main container grid columns & rows
        self.frame.grid_rowconfigure(0, weight=1)      # Both fill full height
        self.frame.grid_columnconfigure(0, weight=1)   # Canvas expands horizontally
        self.frame.grid_columnconfigure(1, weight=0)   # Scrollbar stays fixed width
        self.frame.grid_columnconfigure(2, weight=0)   # Fixed frame stays fixed width

        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self.frame, highlightthickness=0, bg=self.pagebgnd)
        self.scrollbar = AutoScrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.pagebgnd)
        self.mousewheel = MouseWheel(self.frame, self.scrollable_frame, self.canvas)
        self.coloredCombo = ColoredCombo(self.scrollable_frame)

        # Create a window inside the canvas to hold the scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure canvas scroll region based on inner frame's natural bounding box
        def _update_scroll_region(event=None):
            # Force Tkinter to calculate current frame dimensions
            self.scrollable_frame.update_idletasks()

            # Get the bounding box of the frame contents
            bbox = self.canvas.bbox("all")
            if bbox:
                # Measure heights
                content_height = self.scrollable_frame.winfo_reqheight()
                canvas_height = self.canvas.winfo_height()

                if content_height <= canvas_height:
                    # Content fits! Lock scroll region to top (y=0) so scrolling is disabled
                    self.canvas.configure(scrollregion=(0, 0, bbox[2], canvas_height))
                    self.canvas.yview_moveto(0)  # Snap back to top
                else:
                    # Content exceeds window! Allow vertical scrolling, but clamp top to 0
                    self.canvas.configure(scrollregion=(0, 0, bbox[2], bbox[3]+200))

        # Bind the inner frame changes to update the scroll region of the canvas
        self.scrollable_frame.bind("<Configure>", _update_scroll_region)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Grid placement on the left (Columns 0 & 1)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=0, sticky="nse")

        # Fixed area on the right
        self.fixed_frame = tk.Frame(self.frame, bg=self.pagebgnd)
        self.fixed_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Triggered when a combox selection changes
        def on_selection_change(row_name, var):
            """Triggered whenever any dropdown value changes."""
            print(f"Updated '{row_name}' -> New Status: {var.get()}")
            self.tournamentData.resultSet.pairData[row_name].masterpointsRankIndex = UIMPLevels.index(var.get())

        self.labels = []

        # Header
        label = tk.Label(self.scrollable_frame, text="Pair #", font=("Arial", 10, "bold"), bg=self.pagebgnd)
        label.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        self.labels.append(label)
        label = tk.Label(self.scrollable_frame, text="Pair", font=("Arial", 10, "bold"), bg=self.pagebgnd)
        label.grid(row=0, column=1, padx=15, pady=12, sticky="w")
        self.labels.append(label)
        label = tk.Label(self.scrollable_frame, text="Pair Rank", font=("Arial", 10, "bold"), bg=self.pagebgnd)
        label.grid(row=0, column=2, padx=5, pady=12, sticky="w")
        self.labels.append(label)

        # Populate Table Rows
        selections = {}

        # Flatten the 3-level nested list into a single stream of items
        rankings = self.tournamentData.resultSet.overallRankings[0]
        all_items = chain.from_iterable(rankings)

        self.traces = []  # Store trace IDs for cleanup

        # Enumerate, starting at 1 to have row numbers automatically
        for row_number, k in enumerate(all_items, start=1):
            pair_data = self.tournamentData.resultSet.pairData[k.pairNumber]

            # Define cell contents for columns 0 and 1
            labels_text = [str(k.pairNumber), f"{k.player1Name} & {k.player2Name}"]
            
            # Build standard labels for the first two columns
            for col, text in enumerate(labels_text):
                lbl = tk.Label(self.scrollable_frame, text=text, anchor="w", bg=self.pagebgnd)
                lbl.grid(row=row_number, column=col, padx=15, pady=4, sticky="w")
                self.labels.append(lbl)

            # Setup variable & selection tracker
            initial_val = UIMPLevels[pair_data.masterpointsRankIndex]
            var = tk.StringVar(value=initial_val)
            selections[row_number] = var
            
            # Right Dropdown
            combobox = self.coloredCombo.create(var, UIMPLevels[::-1],
                                                 UIMPLevels[self.tournamentData.resultSet.pairData[k.pairNumber].masterpointsRankIndex],
                                                 UIMPLevels[self.tournamentData.resultSet.pairData[k.pairNumber].origmasterpointsRankIndex])
            self.mousewheel.register_combobox_popdown(combobox)
            combobox.grid(row=row_number, column=2, padx=5, sticky="e")
            self.labels.append(combobox)

            # Set trigger on value change
            trace_id = var.trace_add("write", lambda *args, p_num=k.pairNumber, v=var: on_selection_change(p_num, v))
            self.traces.append((var, "write", trace_id))

        # Right hand column instructions
        label = tk.Label(self.fixed_frame, text="Change Player Ranks", font=("Arial", 10, "bold"), anchor="w", bg=self.pagebgnd)
        label.grid(row=0, column=3, padx=25, pady=8, sticky="w")
        self.labels.append(label)

        label = tk.Label(self.fixed_frame, wraplength=300, justify="left",text="The list on the left shows the current rank assigned to each pair for stratification.", anchor="w", bg=self.pagebgnd)
        label.grid(row=1, column=3, padx=25, sticky="w")
        self.labels.append(label)
        label = tk.Label(self.fixed_frame, wraplength=300, justify="left",text="You can override the ranks by selecting a different rank for any pair.", anchor="w", bg=self.pagebgnd)
        label.grid(row=2, column=3, padx=25, sticky="w")
        self.labels.append(label)

    def clearContent(self):
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

        # Destroy the scrollable frame contents
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.scrollable_frame.destroy()
        self.scrollbar.destroy()
        self.canvas.destroy()

        # Destroy the fixed frame contents
        for widget in self.fixed_frame.winfo_children():
            widget.destroy()
        self.fixed_frame.destroy()

        # Reset grid weights
        cols, rows = self.frame.grid_size()
        for i in range(cols):
            self.frame.grid_columnconfigure(i, weight=0)
        for i in range(rows):
            self.frame.grid_rowconfigure(i, weight=0)

        # Clear list of widget references
        for label in self.labels:
            label.destroy()
        self.labels.clear()

        # Clean up the ColoredCombo instance
        self.coloredCombo = None
