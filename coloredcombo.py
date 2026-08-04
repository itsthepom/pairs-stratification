###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# Custom combobox that changes color when the value is changed from the default.
###############################################################################
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

# Colours of the combobox when unchanged (default)
light_bg = "#ffffff"
dark_bg = "#e9ecef"
listbox_bg = "#ffffff"
text_color = "#212529"
border_color = "#ced4da"
arrow_color = "#495057"

# Colours of the combobox when changed (highlighted)
changed_light_bg = "#e6e9f4"
changed_dark_bg = "#cecfeb"
changed_text_color = "#1B239C"
changed_border_color = "#3440a8"

class ColoredCombo:
    def __init__(self, frame):
        self.frame = frame
        self.style = tb.Style()

        # -------------------------------------------------------------
        # 1. DEFAULT COMBOBOX STYLE
        # -------------------------------------------------------------
        self.style.configure("Default.TCombobox",
            fieldbackground=light_bg,
            background=dark_bg,        # Arrow box bg
            foreground=text_color,
            selectbackground=light_bg,  # Keeps background clean when clicked
            selectforeground=text_color,
            arrowcolor=arrow_color,
            bordercolor=border_color,
            borderwidth=1,
            relief="flat"
        )

        # Map focus and readonly states explicitly to prevent blackouts
        self.style.map("Default.TCombobox",
            fieldbackground=[
                ("readonly", light_bg),
                ("focus", light_bg)
            ],
            selectbackground=[
                ("readonly", light_bg),
                ("focus", light_bg)
            ],
            selectforeground=[
                ("readonly", text_color),
                ("focus", text_color)
            ],
            foreground=[
                ("readonly", text_color),
                ("focus", text_color)
            ]
        )

        # -------------------------------------------------------------
        # 2. CHANGED (HIGHLIGHTED) COMBOBOX STYLE
        # -------------------------------------------------------------
        self.style.configure("Changed.TCombobox",
            fieldbackground=changed_light_bg,   # Soft green background
            background=changed_dark_bg,        # Arrow button bg
            foreground=changed_text_color,        # Dark green text
            selectbackground=changed_light_bg,
            selectforeground=changed_text_color,
            arrowcolor=changed_text_color,
            bordercolor=changed_border_color,       # Green border
            borderwidth=1,
            relief="flat"
        )

        self.style.map("Changed.TCombobox",
            fieldbackground=[
                ("readonly", changed_light_bg),
                ("focus", changed_light_bg)
            ],
            selectbackground=[
                ("readonly", changed_light_bg),
                ("focus", changed_light_bg)
            ],
            selectforeground=[
                ("readonly", changed_text_color),
                ("focus", changed_text_color)
            ],
            foreground=[
                ("readonly", changed_text_color),
                ("focus", changed_text_color)
            ]
        )

        # Dropdown options list styling (global option database)
        self.frame.option_add("*TCombobox*Listbox.background", listbox_bg)
        self.frame.option_add("*TCombobox*Listbox.foreground", text_color)
        self.frame.option_add("*TCombobox*Listbox.selectBackground", changed_light_bg)
        self.frame.option_add("*TCombobox*Listbox.selectForeground", changed_text_color)

    def _on_combobox_change(self, event):
        combobox = event.widget

        # Check if current selection differs from initial state
        if combobox.get() != getattr(combobox, "initial_value", None):
            combobox.configure(style="Changed.TCombobox")
        else:
            combobox.configure(style="Default.TCombobox")

        # Clear text selection highlight & focus outline
        combobox.selection_clear()
        self.frame.focus()

    def _on_focus_out(self, event):
        combobox = event.widget
        combobox.selection_clear()

    def create(self, textvar, values, currentValue, origValue):
        combobox = ttk.Combobox(self.frame, textvariable=textvar, values=values, state="readonly", style="Default.TCombobox", width=15)
        combobox.set(currentValue)
        # Store original value on the widget instance to track actual changes
        combobox.initial_value = origValue
        if combobox.get() != getattr(combobox, "initial_value", None):
            combobox.configure(style="Changed.TCombobox")
        else:
            combobox.configure(style="Default.TCombobox")
        # Bind selection and focus events
        combobox.bind("<<ComboboxSelected>>", self._on_combobox_change)
        combobox.bind("<FocusOut>", self._on_focus_out)
        return combobox
