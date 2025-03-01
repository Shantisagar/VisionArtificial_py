"""
Path: src/views/tool_tip.py
Clase ToolTip para crear un tooltip en un widget.
"""
import tkinter as tk

class ToolTip:
    """
    Crea un tooltip para un widget dado.
    """
    def __init__(self, widget, text=None, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, _=None):
        """
        Muestra el tooltip
        
        Args:
            _: Parámetro de evento que recibe del binding (no utilizado)
        """
        self.schedule()

    def leave(self, _=None):
        """
        Oculta el tooltip
        
        Args:
            _: Parámetro de evento que recibe del binding (no utilizado)
        """
        self.unschedule()
        self.hidetip()

    def schedule(self):
        " programa el tooltip para que aparezca "
        self.unschedule()
        self.id = self.widget.after(self.delay, self.showtip)

    def unschedule(self):
        " cancela el tooltip "
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self):
        " muestra el tooltip "
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"), wraplength=250)
        label.pack(padx=3, pady=3)

    def hidetip(self):
        " oculta el tooltip "
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
