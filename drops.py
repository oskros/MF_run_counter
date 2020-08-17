import tk_dynamic as tkd
import tkinter as tk
from tkinter import ttk
import autocompletion


class Drops(tkd.Frame):
    def __init__(self, tab1, parent=None, **kw):
        tkd.Frame.__init__(self, parent.root, kw)
        self.parent = parent
        self.drops = dict()
        self.tab1 = tab1

        self._make_widgets()
        # self.load_item_library()
        # a = 0

    def _make_widgets(self):
        lf = tkd.Frame(self)
        lf.pack(expand=1, fill=tk.BOTH)
        scrollbar = ttk.Scrollbar(lf, orient=tk.VERTICAL)

        self.m = tkd.Text(lf, height=5, yscrollcommand=scrollbar.set, font='courier 11', wrap=tk.WORD, state=tk.DISABLED, cursor='', exportselection=0, name='droplist')
        self.m.bind('<FocusOut>', lambda e: self.m.tag_remove('currentLine', 1.0, tk.END))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(2, 1), padx=1)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(2, 1), padx=0)

        btn = tkd.Button(self, text='Delete selection', command=self.delete)
        btn.bind_all('<Delete>', lambda e: self.delete())
        btn.pack(side=tk.BOTTOM, pady=(1, 2))

    def add_drop(self):
        drop = autocompletion.acbox(enable=self.parent.autocomplete, shortnames=self.parent.item_shortnames)
        # print(drop)
        if not drop or drop[1] == '':
            return
        run_no = len(self.tab1.laps)
        if self.tab1.is_running:
            run_no += 1
        if drop[0] is not None and self.parent.item_shortnames:
            drop_display = drop[1] + ' ' + drop[2].replace(drop[0], '').strip()
        else:
            drop_display = drop[2]
        self.drops.setdefault(str(run_no), []).append(drop_display.strip())
        self.display_drop(drop=drop_display.strip(), run_no=run_no)

    def display_drop(self, drop, run_no):
        line = 'Run %s: %s' % (run_no, drop)
        if self.m.get('1.0', tk.END) != '\n':
            line = '\n' + line
        self.m.config(state=tk.NORMAL)
        self.m.insert(tk.END, line)
        self.m.yview_moveto(1)
        self.m.config(state=tk.DISABLED)

    def delete(self):
        if self.focus_get()._name == 'droplist':
            cur_row = self.m.get('insert linestart', 'insert lineend+1c').strip()
            sep = cur_row.find(':')
            run_no = cur_row[:sep].replace('Run ', '')
            drop = cur_row[sep+2:]
            self.drops[run_no].remove(drop)
            self.m.config(state=tk.NORMAL)
            self.m.delete('insert linestart', 'insert lineend+1c')
            self.m.config(state=tk.DISABLED)

    def save_state(self):
        return self.drops

    def load_from_state(self, state):
        self.m.delete(1.0, tk.END)
        self.drops = state.get('drops', dict())
        for run in sorted(self.drops.keys(), key=lambda x: int(x)):
            for drop in self.drops[run]:
                self.display_drop(drop=drop, run_no=run)

    # def load_item_library(self):
    #     import pandas as pd
    #     lib = pd.read_csv('item_library.csv', index_col='Item')
    #     alias_cols = [c for c in lib.columns if c.lower().startswith('alias')]
    #     lib['Alias'] = lib[alias_cols].values.tolist()
    #     pre_dict = lib['Alias'].to_dict()
    #     self.item_alias = {l: k for k, v in pre_dict.items() for l in v if str(l) != 'nan'}
    #
    #     for c in alias_cols + ['Alias']:
    #         del lib[c]
    #     self.item_library = lib
    #
    # def lookup_item(self, item_alias):
    #     x = item_alias.lower()
    #     item_name = ' '.join(w.capitalize() for w in self.item_alias.get(x, x).split())
    #     return dict(Name=item_name, Alias=item_alias)
