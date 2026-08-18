###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# About box
###############################################################################
import ttkbootstrap as tb
from baseclasses import AppName, AppVersion
from uiparts import UIParts
import webbrowser
from tkinter import PhotoImage

class about:
    def __init__(self, uiparts: UIParts):
        self.uiparts = uiparts
        uiparts.about = self

    def open_url(self, event):
        webbrowser.open_new("https://github.com/itsthepom/pairs-stratification")

    def show(self):
        about_win = tb.Toplevel(self.uiparts.root)
        about_win.title("About Pairs Stratification")

        # Define window dimensions
        width = 340
        height = 340
        
        # Calculate x and y coordinates to center on the SCREEN
        screen_width = about_win.winfo_screenwidth()
        screen_height = about_win.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Set geometry with offsets: "WIDTHxHEIGHT+X+Y"
        about_win.geometry(f"{width}x{height}+{x}+{y}")
        about_win.resizable(False, False)

        # Make modal
        about_win.transient(self.uiparts.root)
        about_win.grab_set()

        # Load PNG image
        # Note: PNG support is built into Tkinter 8.6+ (Python 3.4+)
        logo_img = PhotoImage(file="resources\\PairsStratificationAbout.png")
        
        # Image Label (CRITICAL: Keep a reference so Python's garbage collector doesn't delete it)
        logo_label = tb.Label(about_win, image=logo_img)
        logo_label.image = logo_img  # Reference retention
        logo_label.pack(pady=(20, 5))

        # App Title & Version
        tb.Label(about_win, text=AppName, font=("Helvetica", 16, "bold")).pack(pady=2)
        tb.Label(about_win, text="Version " + AppVersion, font=("Helvetica", 9)).pack(pady=2)

        # Clickable Link Label
        link_label = tb.Label(about_win, text="Visit Website", font=("Helvetica", 10, "underline"), cursor="hand2")
        link_label.pack(pady=10)
        link_label.bind("<Button-1>", self.open_url)

        # Close Button
        tb.Button(about_win, text="Close", bootstyle="primary", command=about_win.destroy).pack(pady=(5, 15))
