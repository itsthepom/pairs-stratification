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

# Colors of the tooltip
ttborder_color = "#ced4da"
ttbackground_color = "#FFFFE8"
ttforeground_color = "#3c5055"
ttdelay = 500

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self._timer_id = None  # Tracks the scheduled timer

    def _on_enter(self, event=None):
        """Schedules the tooltip to appear after the delay."""
        self._cancel_timer()
        # Schedule show_tip after specified delay
        self._timer_id = self.widget.after(ttdelay, self.show_tip)

    def _on_leave(self, event=None):
        """Cancels any pending timer and hides the tooltip."""
        self._cancel_timer()
        self.hide_tip()

    def _cancel_timer(self):
        """Cancels the pending scheduled delay if mouse leaves early."""
        if self._timer_id is not None:
            self.widget.after_cancel(self._timer_id)
            self._timer_id = None

    def show_tip(self):
        """Creates and renders the tooltip window."""
        self._timer_id = None
        if self.tip_window or not self.text:
            return
        
        # Calculate position (slightly below and to the right of the widget)
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Create borderless popup window
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Border container
        tw.configure(
            background=ttborder_color, 
            padx=1, 
            pady=1
        )

        # Inner label
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background=ttbackground_color,
            foreground=ttforeground_color,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 8),
            padx=6,
            pady=3
        )
        label.pack()

    def hide_tip(self):
        """Destroys the active tooltip window."""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

    def arm(self):
        """Arms the tooltip to show on hover."""
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<ButtonPress>", self._on_leave)  # Hide immediately on click

    def disarm(self):
        """Disarms the tooltip, preventing it from showing."""
        self._cancel_timer()
        self.hide_tip()
        self.widget.unbind("<Enter>")
        self.widget.unbind("<Leave>")
        self.widget.unbind("<ButtonPress>")

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

        # Flat icon button style for reset
        self.style.configure("Reset.TButton",
            font=("Segoe UI", 11, "bold"),
            foreground=text_color,
            background=light_bg,
            borderwidth=0,
            focuscolor="none",
            padding=0,
            relief="flat"
        )
        self.style.map("Reset.TButton",
            foreground=[("disabled", light_bg)],
            background=[("disabled", light_bg)]
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
            combobox.bound_button.config(state="normal")
            combobox.bound_button.tooltip.arm()  # Arm the tooltip when the button is enabled
        else:
            combobox.configure(style="Default.TCombobox")
            combobox.bound_button.config(state="disabled")
            combobox.bound_button.tooltip.disarm()  # Disarm the tooltip when the button is disabled

        # Clear text selection highlight & focus outline
        combobox.selection_clear()
        self.frame.focus()

    def _on_focus_out(self, event):
        combobox = event.widget
        combobox.selection_clear()

    def create(self, textvar, row_number, values, currentValue, origValue):
        combobox = ttk.Combobox(self.frame, textvariable=textvar, values=values, state="readonly", style="Default.TCombobox", width=15)
        combobox.grid(row=row_number, column=2, padx=5, sticky="e")
        combobox.set(currentValue)
        # Store original value on the widget instance to track actual changes
        combobox.initial_value = origValue

        # Reset Icon Button
        reset_btn = ttk.Button(self.frame, text="↺", style="Reset.TButton", width=3, command=lambda c=combobox: self._reset_combobox(c))
        reset_btn.grid(row=row_number, column=3, padx=(0, 15), sticky="e")
        reset_btn.config(state="disabled")
        combobox.bound_button = reset_btn  # Link the button to the combobox for easy access

        # Attach Tooltip to the button
        reset_btn.tooltip = ToolTip(reset_btn, "Reset to default")

        if combobox.get() != getattr(combobox, "initial_value", None):
            combobox.configure(style="Changed.TCombobox")
            reset_btn.config(state="normal")
            reset_btn.tooltip.arm()  # Arm the tooltip when the button is enabled
        else:
            combobox.configure(style="Default.TCombobox")
            reset_btn.config(state="disabled")
            reset_btn.tooltip.disarm()  # Disarm the tooltip when the button is disabled

        # Bind selection and focus events
        combobox.bind("<<ComboboxSelected>>", self._on_combobox_change)
        combobox.bind("<FocusOut>", self._on_focus_out)
        return combobox

    def _reset_combobox(self, combobox):
        if hasattr(combobox, "initial_value"):
            combobox.set(combobox.initial_value)
            combobox.configure(style="Default.TCombobox")
            combobox.bound_button.config(state="disabled")
            combobox.selection_clear()
            self.frame.focus_set()
