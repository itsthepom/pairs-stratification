###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# Auto-hiding scrollbar
###############################################################################
import tkinter as tk

class AutoScrollbar(tk.Canvas):
    """Custom flat scrollbar with rounded thumb, arrow stepping, dynamic sizing, and auto-hiding."""

    def __init__(self, master=None, command=None, **kw):
        self.command = command or kw.pop("command", None)
        self.orient = kw.pop("orient", kw.pop("orientation", "vertical"))
        
        self.bg_color = kw.pop("bg", kw.pop("background", "#F1F1F1"))
        self.thumb_color = kw.pop("thumb_color", "#C1C1C1")
        self.thumb_hover = kw.pop("thumb_hover", "#A6A6A6")
        self.arrow_color = kw.pop("arrow_color", "#555555")
        self.scrollbar_width = kw.pop("width", 12)

        super().__init__(
            master,
            width=self.scrollbar_width,
            bg=self.bg_color,
            highlightthickness=0,
            bd=0,
            **kw
        )

        self.lo = 0.0
        self.hi = 1.0
        self._geo_manager = None
        self._geo_options = {}

        # Draw static arrows
        self._draw_arrows()

        # Canvas items for the thumb caps and body
        self.top_cap = self.create_oval(0, 0, 0, 0, fill=self.thumb_color, outline="")
        self.bottom_cap = self.create_oval(0, 0, 0, 0, fill=self.thumb_color, outline="")
        self.thumb_body = self.create_rectangle(0, 0, 0, 0, fill=self.thumb_color, outline="")

        # Mouse Interaction
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Enter>", lambda e: self._set_thumb_color(self.thumb_hover))
        self.bind("<Leave>", lambda e: self._set_thumb_color(self.thumb_color))

    def _set_thumb_color(self, color):
        self.itemconfig(self.top_cap, fill=color)
        self.itemconfig(self.bottom_cap, fill=color)
        self.itemconfig(self.thumb_body, fill=color)

    def _draw_arrows(self):
        w = self.scrollbar_width
        # Up Arrow (0px to 12px height zone)
        self.create_polygon(w / 2, 3, 3, 9, w - 3, 9, fill=self.arrow_color, tags="up_arrow")
        # Down Arrow (repositioned on resize)
        self.bind("<Configure>", self._reposition_down_arrow)

    def _reposition_down_arrow(self, event):
        self.delete("down_arrow")
        w, h = self.winfo_width(), self.winfo_height()
        self.create_polygon(
            w / 2, h - 3, 3, h - 9, w - 3, h - 9, fill=self.arrow_color, tags="down_arrow"
        )
        self._redraw_thumb()

    def _redraw_thumb(self):
        h = self.winfo_height()
        if h <= 24:
            return

        track_top = 12
        track_bottom = h - 12
        track_h = track_bottom - track_top

        # Dynamic thumb range
        y1 = track_top + (self.lo * track_h)
        y2 = track_top + (self.hi * track_h)

        # Enforce minimum thumb height
        min_thumb_h = 16
        if (y2 - y1) < min_thumb_h:
            y2 = y1 + min_thumb_h
            if y2 > track_bottom:
                y2 = track_bottom
                y1 = y2 - min_thumb_h

        w = self.scrollbar_width
        r = (w - 2) / 2

        # Draw rounded pill sections
        self.coords(self.top_cap, 1, y1, w - 1, y1 + 2 * r)
        self.coords(self.bottom_cap, 1, y2 - 2 * r, w - 1, y2)
        self.coords(self.thumb_body, 1, y1 + r, w - 1, y2 - r)

    def set(self, lo, hi):
        self.lo, self.hi = float(lo), float(hi)

        if self.winfo_exists():
            mgr = self.winfo_manager() or self._geo_manager

            if self.lo <= 0.0 and self.hi >= 1.0:
                if self.winfo_ismapped():
                    if mgr == "grid":
                        self.grid_remove()
                    elif mgr == "pack":
                        self.pack_forget()
            else:
                if not self.winfo_ismapped():
                    if mgr == "grid":
                        self.grid(**self._geo_options)
                    elif mgr == "pack":
                        self.pack(**self._geo_options)

                self._redraw_thumb()

    def pack(self, **kw):
        self._geo_manager = "pack"
        self._geo_options = kw
        super().pack(**kw)

    def grid(self, **kw):
        self._geo_manager = "grid"
        self._geo_options = kw
        super().grid(**kw)

    def _on_click(self, event):
        h = self.winfo_height()
        y = event.y

        if not self.command:
            return

        # 1. Clicked Top Arrow
        if y < 12:
            self.command("scroll", -1, "units")
        # 2. Clicked Bottom Arrow
        elif y > (h - 12):
            self.command("scroll", 1, "units")
        # 3. Clicked Track or Dragged Thumb
        else:
            self._scroll_to(y)

    def _on_drag(self, event):
        # Prevent dragging outside the trough track
        h = self.winfo_height()
        if 12 <= event.y <= (h - 12):
            self._scroll_to(event.y)

    def _scroll_to(self, y):
        h = self.winfo_height()
        track_h = max(1, h - 24)
        fraction = (y - 12) / track_h
        if self.command:
            self.command("moveto", max(0.0, min(1.0, fraction)))