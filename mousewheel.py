###############################################################################
# Pairs Stratification Utility.
# Copyright Steve Pomeroy 2026
#
# Global mousewheel scrolling for a canvas with multiple widgets, including comboboxes.
###############################################################################
from tkinter import ttk
import tkinter as tk

class MouseWheel:
    def __init__(self, root, scrollable_frame, canvas):
        """
        Global MouseWheel Manager.
        Ensures smooth canvas scrolling over closed controls while freezing 
        canvas movement completely when any popdown listbox is open.
        """
        self.root = root
        self.scrollable_frame = scrollable_frame
        self.canvas = canvas
        self.active_popdown_listbox = None

        # Bind globally at the application root
        self.root.bind_all("<MouseWheel>", self._on_global_mousewheel)
        self.root.bind_all("<Button-4>", self._on_global_mousewheel)  # Linux scroll up
        self.root.bind_all("<Button-5>", self._on_global_mousewheel)  # Linux scroll down

    def _on_global_mousewheel(self, event):
        # -----------------------------------------------------------------
        # SCENARIO A: A Combobox Dropdown is Currently Open
        # -----------------------------------------------------------------
        if self.active_popdown_listbox:
            # Check if the popdown listbox actually still exists in Tcl
            try:
                exists = self.root.tk.call("winfo", "exists", self.active_popdown_listbox)
                if not exists:
                    self.active_popdown_listbox = None
            except tk.TclError:
                self.active_popdown_listbox = None

            if self.active_popdown_listbox:
                # DO NOT manually scroll the canvas OR listbox here.
                # Returning "break" halts event propagation so Ttk's native 
                # popdown scroll routine handles the listbox without canvas bleed.
                return "break"

        # -----------------------------------------------------------------
        # SCENARIO B: Normal Canvas Scrolling (Closed Comboboxes)
        # -----------------------------------------------------------------
        content_height = self.scrollable_frame.winfo_reqheight()
        canvas_height = self.canvas.winfo_height()

        if content_height > canvas_height:
            if event.num == 4:  # Linux scroll up
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Linux scroll down
                self.canvas.yview_scroll(1, "units")
            elif event.delta:  # Windows / macOS
                delta = int(-1 * (event.delta / 120)) if abs(event.delta) >= 120 else int(-1 * event.delta)
                self.canvas.yview_scroll(delta if delta != 0 else (-1 if event.delta > 0 else 1), "units")

        # Stop closed comboboxes from cycling through values when hovered
        return "break"

    def register_combobox_popdown(self, combobox):
        """Registers popdown tracking and overrides combobox default scroll behavior."""
        
        def _on_open(event):
            # Query Tcl after a tiny delay to ensure Ttk has finished creating the popdown window
            def _get_path():
                try:
                    popdown = combobox.tk.call("ttk::combobox::PopdownWindow", combobox)
                    self.active_popdown_listbox = f"{popdown}.f.l"
                except tk.TclError:
                    self.active_popdown_listbox = None
            
            combobox.after(10, _get_path)

        def _on_close(event):
            self.active_popdown_listbox = None

        # Track when dropdown opens (mouse click or down key)
        combobox.bind("<ButtonPress-1>", _on_open, add="+")
        combobox.bind("<Down>", _on_open, add="+")

        # Track when dropdown closes
        combobox.bind("<<ComboboxSelected>>", _on_close, add="+")
        combobox.bind("<FocusOut>", _on_close, add="+")
        combobox.bind("<Escape>", _on_close, add="+")

        # Route local combobox wheel events to the manager to prevent value cycling
        combobox.bind("<MouseWheel>", self._on_global_mousewheel)
        combobox.bind("<Button-4>", self._on_global_mousewheel)
        combobox.bind("<Button-5>", self._on_global_mousewheel)
