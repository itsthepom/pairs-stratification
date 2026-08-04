###############################################################################
# Pairs Stratification Program.
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
        self.step_size = 1

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
                units = -1 * self.step_size
            elif event.num == 5:  # Linux scroll down
                units = 1 * self.step_size
            elif event.delta:  # Windows / macOS
                # Calculate base direction (-1 for up, 1 for down)
                delta = int(-1 * (event.delta / 120)) if abs(event.delta) >= 120 else int(-1 * event.delta)
                base_direction = delta if delta != 0 else (-1 if event.delta > 0 else 1)
                
                # Apply step_size multiplier
                units = base_direction * self.step_size
            else:
                units = 0

            if units != 0:
                self.canvas.yview_scroll(units, "units")

        # Stop closed comboboxes from cycling through values when hovered
        return "break"

    def register_combobox_popdown(self, combobox):
        """Registers popdown tracking and overrides combobox default scroll behavior."""
        
        def _on_open(event):
            def _bind_popdown_unmap():
                try:
                    # Get Tcl widget path for the popdown window
                    popdown = combobox.tk.call("ttk::combobox::PopdownWindow", combobox)
                    self.active_popdown_listbox = f"{popdown}.f.l"

                    # Direct Tcl binding on the popdown frame: releases focus when popdown closes/unmaps
                    def _on_popdown_unmap(e=None):
                        self.active_popdown_listbox = None
                        try:
                            combobox.selection_clear()
                        except tk.TclError:
                            pass
                        # Shift focus back to root to restore global canvas scrolling
                        self.root.focus_set()

                    # Bind to <Unmap> so clicking outside or selecting an item releases focus instantly
                    combobox.tk.call("bind", popdown, "<Unmap>", combobox.register(_on_popdown_unmap))

                except tk.TclError:
                    self.active_popdown_listbox = None

            combobox.after(10, _bind_popdown_unmap)

        def _on_close(event):
            self.active_popdown_listbox = None
            # Clear text selection
            try:
                combobox.selection_clear()
            except tk.TclError:
                pass

        # Track when dropdown opens (mouse click or down key)
        combobox.bind("<ButtonPress-1>", _on_open, add="+")
        combobox.bind("<Down>", _on_open, add="+")

        # Track when dropdown closes
        combobox.bind("<<ComboboxSelected>>", _on_close, add="+")
        combobox.bind("<Escape>", _on_close, add="+")

        # Route local combobox wheel events to the manager to prevent value cycling
        combobox.bind("<MouseWheel>", self._on_global_mousewheel)
        combobox.bind("<Button-4>", self._on_global_mousewheel)
        combobox.bind("<Button-5>", self._on_global_mousewheel)

    def register_scrollbar(self, scrollbar):
        """
        Dismisses any open combobox popdown immediately when the user 
        interacts with or scrolls directly over the scrollbar.
        """
        def _dismiss_popdown(event=None):
            if self.active_popdown_listbox:
                try:
                    # Get the root popdown window path (e.g., '.popdown' from '.popdown.f.l')
                    popdown_window = self.active_popdown_listbox.split('.')[1]
                    # Withdraw the Tcl popdown top-level window to close it cleanly
                    self.root.tk.call("wm", "withdraw", f".{popdown_window}")
                except tk.TclError:
                    pass
                
                self.active_popdown_listbox = None
                self.root.focus_set()

        def _on_scrollbar_scroll(event):
            # Dismiss popdowns if open
            _dismiss_popdown(event)
            # Redirect scroll handling to our global step-size routine
            return self._on_global_mousewheel(event)

        # Dismiss popdown when clicking/dragging the scrollbar thumb or trough
        scrollbar.bind("<ButtonPress-1>", _dismiss_popdown, add="+")

        # Divert mousewheel events over the scrollbar to use custom step_size
        scrollbar.bind("<MouseWheel>", _on_scrollbar_scroll)
        scrollbar.bind("<Button-4>", _on_scrollbar_scroll)
        scrollbar.bind("<Button-5>", _on_scrollbar_scroll)

