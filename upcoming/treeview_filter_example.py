from tkinter import *
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


class Application(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Volume")

        combofr = Frame(self)
        combofr.pack(expand=True, fill=X)
        self.tree = ttk.Treeview(self, show='headings')
        columns = list(inp[0].keys())

        self.filters = []

        for col in columns:
            name = 'combofilter_' + col
            self.filters.append(name)
            setattr(self, name, ttk.Combobox(combofr, values=[''] + sorted(set(x[col] for x in inp)), state="readonly"))
            getattr(self, name).pack(side=LEFT, expand=True, fill=X)
            getattr(self, name).bind('<<ComboboxSelected>>', self.select_from_filters)

        self.tree["columns"] = columns
        self.tree.pack(expand=TRUE, fill=BOTH)

        for i in columns:
            self.tree.column(i, anchor="w")
            self.tree.heading(i, text=i, anchor="w")

        for i, row in enumerate(inp):
            self.tree.insert("", "end", text=i, values=list(row.values()))

    def select_from_filters(self, event=None):
        self.tree.delete(*self.tree.get_children())

        all_filter = lambda x: all(x[f.split('_')[-1]] == getattr(self, f).get() or getattr(self, f).get() == '' for f in self.filters)
        for row in inp:
            if all_filter(row):
                self.tree.insert("", "end", values=list(row.values()))


root = Application()
root.mainloop()
