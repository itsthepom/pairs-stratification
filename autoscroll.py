###############################################################################
# Pairs Stratification Utility.
# Copyright Steve Pomeroy 2026
#
# Auto-hiding scrollbar
###############################################################################
from tkinter import ttk
import tkinter as tk

class AutoScrollbar(ttk.Scrollbar):
    """A scrollbar that hides itself when content fits inside the window."""

    def __init__(self, master=None, **kw):
        # Ensure style is set to 'Custom.TScrollbar'
        # (TTK prepends 'Vertical.' to this string internally when orient="vertical")
        if "style" not in kw:
            kw["style"] = "Custom.TScrollbar"

        style = ttk.Style()

        # Define the layout before we call super().__init__()
        # Must match 'Vertical.Custom.TScrollbar' because TTK appends 'Vertical.'
        style.layout(
            "Vertical.Custom.TScrollbar",
            [
                (
                    "Scrollbar.trough",
                    {
                        "sticky": "ns",
                        "children": [
                            ("Scrollbar.uparrow", {"side": "top", "sticky": ""}),
                            ("Scrollbar.downarrow", {"side": "bottom", "sticky": ""}),
                            (
                                "Vertical.Scrollbar.thumb",
                                {"expand": "1", "sticky": "ns"},
                            ),
                        ],
                    },
                )
            ],
        )

        # Setup styling and colours
        style.configure(
            "Vertical.Custom.TScrollbar",
            arrowsize=16,
            width=24,
            relief="flat",
            troughcolor="#f8f9fa",   # Track background
        )

        # Setup the color mapping for different states (pressed, active, etc.)
        style.map(
            "Vertical.Custom.TScrollbar",
            background=[
                ("pressed", "#a0a0a0"),
                ("active", "#c0c0c0"),
            ],
            lightcolor=[
                ("pressed", "#a0a0a0"),
                ("active", "#c0c0c0"),
            ],
            darkcolor=[
                ("pressed", "#a0a0a0"),
                ("active", "#c0c0c0"),
            ],
        )

        # Initialize the underlying Tkinter widget
        super().__init__(master, **kw)

    def set(self, lo, hi):
        lo, hi = float(lo), float(hi)

        if self.winfo_exists():
            if lo <= 0.0 and hi >= 1.0:
                if self.winfo_ismapped():
                    self.pack_forget()
            else:
                if not self.winfo_ismapped():
                    self.pack(side="left", fill="y", pady=10)

        super().set(lo, hi)