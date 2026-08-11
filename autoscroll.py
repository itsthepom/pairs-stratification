###############################################################################
# Pairs Stratification Program.
# Copyright Steve Pomeroy 2026
#
# Auto-hiding scrollbar
###############################################################################
import tkinter as tk
from appcolours import *

class AutoScrollbar(tk.Canvas):
    """Custom flat scrollbar with rounded thumb, arrow stepping, dynamic sizing, and auto-hiding."""

    def __init__(self, master=None, command=None, **kw):
        self.command = command or kw.pop("command", None)
        self.orient = kw.pop("orient", kw.pop("orientation", "vertical"))
        
        self.bg_color = kw.pop("bg", kw.pop("background", asb_bg_color))
        self.thumb_color = kw.pop("thumb_color", asb_thumb_color)
        self.thumb_hover = kw.pop("thumb_hover", asb_thumb_hover)
        self.arrow_color = kw.pop("arrow_color", asb_arrow_color)
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
        self._drag_offset = 0
        self._is_dragging = False
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
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", lambda e: self._set_thumb_color(self.thumb_hover))
        self.bind("<Leave>", lambda e: self._set_thumb_color(self.thumb_color))

    def _set_thumb_color(self, color):
        self.itemconfig(self.top_cap, fill=color)
        self.itemconfig(self.bottom_cap, fill=color)
        self.itemconfig(self.thumb_body, fill=color)

    def _draw_arrows(self):
        w = self.scrollbar_width
        self.create_polygon(w / 2, 3, 3, 9, w - 3, 9, fill=self.arrow_color, tags="up_arrow")
        self.bind("<Configure>", self._reposition_down_arrow)

    def _reposition_down_arrow(self, event):
        self.delete("down_arrow")
        w, h = self.winfo_width(), self.winfo_height()
        self.create_polygon(
            w / 2, h - 3, 3, h - 9, w - 3, h - 9, fill=self.arrow_color, tags="down_arrow"
        )
        self._redraw_thumb()

    def _get_thumb_y_bounds(self):
        h = self.winfo_height()
        if h <= 24:
            return 12, 12

        track_top = 12
        track_bottom = h - 12
        track_h = track_bottom - track_top

        y1 = track_top + (self.lo * track_h)
        y2 = track_top + (self.hi * track_h)

        min_thumb_h = 16
        if (y2 - y1) < min_thumb_h:
            y2 = y1 + min_thumb_h
            if y2 > track_bottom:
                y2 = track_bottom
                y1 = y2 - min_thumb_h

        return y1, y2

    def _redraw_thumb(self):
        h = self.winfo_height()
        if h <= 24:
            return

        y1, y2 = self._get_thumb_y_bounds()
        w = self.scrollbar_width
        r = (w - 2) / 2

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

    def _get_thumb_y_bounds(self):
        h = self.winfo_height()
        if h <= 24:
            return 12, 12

        track_top = 12
        track_bottom = h - 12
        total_track_h = track_bottom - track_top

        # Standard Tkinter scrollbar mapping: lo and hi span the full track
        y1 = track_top + (self.lo * total_track_h)
        y2 = track_top + (self.hi * total_track_h)

        # Enforce minimum thumb height without distorting the tracking ratio
        min_thumb_h = 16
        raw_h = y2 - y1
        if raw_h < min_thumb_h:
            # Expand thumb centered around its raw midpoint
            mid = (y1 + y2) / 2
            y1 = mid - (min_thumb_h / 2)
            y2 = mid + (min_thumb_h / 2)

            # Clamp edges to track bounds
            if y1 < track_top:
                y1 = track_top
                y2 = y1 + min_thumb_h
            elif y2 > track_bottom:
                y2 = track_bottom
                y1 = y2 - min_thumb_h

        return y1, y2
    
    def _on_click(self, event):
        if not self.command:
            return

        h = self.winfo_height()
        y = event.y

        # Top Arrow
        if y < 12:
            self.command("scroll", -1, "units")
            return

        # Bottom Arrow
        if y > (h - 12):
            self.command("scroll", 1, "units")
            return

        thumb_y1, thumb_y2 = self._get_thumb_y_bounds()

        # Clicked ON the thumb -> Record drag offset
        if thumb_y1 <= y <= thumb_y2:
            self._is_dragging = True
            self._drag_offset = y - thumb_y1
        # Clicked track above thumb -> page up
        elif y < thumb_y1:
            self.command("scroll", -1, "pages")
        # Clicked track below thumb -> page down
        else:
            self.command("scroll", 1, "pages")

    def _on_drag(self, event):
        if not self._is_dragging or not self.command:
            return

        h = self.winfo_height()
        thumb_y1, thumb_y2 = self._get_thumb_y_bounds()
        thumb_h = thumb_y2 - thumb_y1
        
        usable_track = max(1, (h - 24) - thumb_h)

        # Calculate where the top edge of the thumb should be
        target_thumb_top = event.y - self._drag_offset - 12

        # Convert back to fraction 0.0 - 1.0
        fraction = target_thumb_top / h

        self.command("moveto", max(0.0, min(1.0, fraction)))

    def _on_release(self, event):
        self._is_dragging = False