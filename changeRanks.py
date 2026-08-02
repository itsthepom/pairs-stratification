###############################################################################
# Pairs Stratification Utility.
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
        pass

    def getName(self):
        return 'changeranks'

    def construct(self, pagebgnd):
        self.pagebgnd = pagebgnd

        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self.frame, highlightthickness=0, bg=self.pagebgnd)
        self.scrollbar = AutoScrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.pagebgnd)

        # Create a window inside the canvas to hold the scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure canvas scrollregion based on inner frame's natural bounding box
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
                    self.canvas.configure(scrollregion=(0, 0, bbox[2], bbox[3]))

                # Keep width dynamic
                req_width = self.scrollable_frame.winfo_reqwidth()
                self.canvas.config(width=req_width)


        # Bind both the inner frame changes AND the canvas resize event
        self.scrollable_frame.bind("<Configure>", _update_scroll_region)
        self.canvas.bind("<Configure>", _update_scroll_region)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="y", padx=(15,0), pady=10)
        self.scrollbar.pack(side="left", fill="y", pady=10)

        # Mousewheel handling
        # Guard mousewheel scrolling so it only scrolls when content exceeds canvas height
        def _on_mousewheel(event):
            content_height = self.scrollable_frame.winfo_reqheight()
            canvas_height = self.canvas.winfo_height()

            # Only scroll if content is taller than the visible canvas area
            if content_height > canvas_height:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


        def _forward_scroll_to_canvas(event):
            content_height = self.scrollable_frame.winfo_reqheight()
            canvas_height = self.canvas.winfo_height()

            if content_height > canvas_height:
                if event.num == 4:  # Linux scroll up
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:  # Linux scroll down
                    self.canvas.yview_scroll(1, "units")
                elif event.delta:  # Windows / macOS
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            return "break"  # Stop combobox value change regardless

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def on_selection_change(row_name, var):
            """Triggered whenever any dropdown value changes."""
            print(f"Updated '{row_name}' -> New Status: {var.get()}")

        # Header
        self.heading1 = tk.Label(self.scrollable_frame, text="Pair Number", font=("Helvetica", 10, "bold"), bg=self.pagebgnd)
        self.heading1.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.heading2 = tk.Label(self.scrollable_frame, text="Rank for stratification", font=("Helvetica", 10, "bold"), bg=self.pagebgnd)
        self.heading2.grid(row=0, column=1, padx=15, pady=8, sticky="w")

        # Populate Table Rows
        selections = {}
        
        # Get the pair names
        self.row_items = [f"Pair {i}:" for i in self.tournamentData.resultSet.pairData]

        for i, item_name in enumerate(self.row_items, start=1):
            # Left Label
            lbl = tk.Label(self.scrollable_frame, text=item_name, anchor="w", bg=self.pagebgnd)
            lbl.grid(row=i, column=0, padx=15, pady=4, sticky="ew")
            
            # StringVar holding selection (defaults to first option in UIMPLevels)
            var = tk.StringVar(value=UIMPLevels[0])
            selections[item_name] = var
            
            # Attach change listener to each variable
            var.trace_add("write", lambda *args, name=item_name, v=var: on_selection_change(name, v))
            
            # Right Dropdown
            combobox = ttk.Combobox(
                self.scrollable_frame, 
                textvariable=var, 
                values=UIMPLevels,
                state="readonly",
                width=15
            )
            combobox.bind("<MouseWheel>", _forward_scroll_to_canvas)
            combobox.grid(row=i, column=1, padx=15, sticky="e")

    def clearContent(self):
        # Unbind global application events
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.unbind_all("<MouseWheel>")

        # Destroy the top-level container (or individual widgets)
        if hasattr(self, 'frame') and self.frame:
            for widget in self.frame.winfo_children():
                widget.destroy()

        # Clear instance variables to break references
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        self.heading1 = None
        self.heading2 = None
