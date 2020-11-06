import tkinter as tk
from tkinter import ttk

inp = [{'Currency': 'EUR', 'Volume': '100', 'Country': 'SE'},
       {'Currency': 'GBP', 'Volume': '200', 'Country': 'SE'},
       {'Currency': 'CAD', 'Volume': '300', 'Country': 'SE'},
       {'Currency': 'EUR', 'Volume': '400', 'Country': 'SE'},
       {'Currency': 'EUR', 'Volume': '100', 'Country': 'DK'},
       {'Currency': 'GBP', 'Volume': '200', 'Country': 'DK'},
       {'Currency': 'CAD', 'Volume': '300', 'Country': 'DK'},
       {'Currency': 'EUR', 'Volume': '400', 'Country': 'DK'},
       ]


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Volume")

        self.tree = ttk.Treeview(self, show='headings')
        columns = list(inp[0].keys())

        self.tree["columns"] = columns
        self.tree.pack(expand=tk.TRUE, fill=tk.BOTH)

        for i in columns:
            self.tree.column(i, anchor=tk.W)
            self.tree.heading(i, text=i, anchor=tk.W)

        for row in inp:
            self.tree.insert("", "end", values=list(row.values()))


root = Application()
style = ttk.Style()
# style.theme_use('clam')
# style.theme_settings()

# style.theme_create('my_style', parent='clam')
# style.theme_use('my_style')
root.mainloop()