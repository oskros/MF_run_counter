from utils import tk_dynamic as tkd, tk_utils, autocompletion
import tkinter as tk
from tkinter import ttk


class Drops(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent.root, kw)
        self.parent = parent
        self.drops = dict()
        self.main_frame = main_frame

        self._make_widgets()

    def _make_widgets(self):
        lf = tkd.Frame(self)
        lf.pack(expand=1, fill=tk.BOTH)
        scrollbar = ttk.Scrollbar(lf, orient=tk.VERTICAL)

        self.m = tkd.Text(lf, height=5, yscrollcommand=scrollbar.set, font='courier 11', wrap=tk.WORD, state=tk.DISABLED, cursor='', exportselection=1, name='droplist')

        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(2, 1), padx=1)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(2, 1), padx=0)

        btn = tkd.Button(self, text='Delete selection', command=self.delete)
        self.m.bind('<Delete>', lambda e: self.delete())
        btn.pack(side=tk.BOTTOM, pady=(1, 2))

    def add_drop(self):
        drop = autocompletion.acbox(enable=self.parent.autocomplete, title='Add drop')
        if not drop or drop['input'] == '':
            return
        if drop['item_name'] is not None:
            for i, item in enumerate(self.main_frame.grail_tab.grail):
                if item['Item'] == drop['item_name']:
                    if item.get('Found', False) is False:
                        if tk_utils.mbox(msg="Congrats, a new drop! Add it to local grail?", title="Grail item"):
                            self.main_frame.grail_tab.update_grail_from_index(i)
                            drop['input'] = '(*) ' + drop['input']
                    break

        run_no = len(self.main_frame.timer_tab.laps)
        if self.main_frame.timer_tab.is_running:
            run_no += 1

        self.drops.setdefault(str(run_no), []).append(drop)
        self.display_drop(drop=drop, run_no=run_no)

    def display_drop(self, drop, run_no):
        line = 'Run %s: %s' % (run_no, drop['input'])
        if self.m.get('1.0', tk.END) != '\n':
            line = '\n' + line
        self.m.config(state=tk.NORMAL)
        self.m.insert(tk.END, line)
        self.m.yview_moveto(1)
        self.m.config(state=tk.DISABLED)

    def delete(self):
        if self.focus_get()._name == 'droplist':
            cur_row = self.m.get('insert linestart', 'insert lineend+1c').strip()
            resp = tk_utils.mbox(msg='Do you want to delete the row:\n%s' % cur_row, title='Warning')
            if resp is True:
                sep = cur_row.find(':')
                run_no = cur_row[:sep].replace('Run ', '')
                drop = cur_row[sep+2:]
                try:
                    self.drops[run_no].remove(next(d for d in self.drops[run_no] if d['input'] == drop))
                    self.m.config(state=tk.NORMAL)
                    self.m.delete('insert linestart', 'insert lineend+1c')
                    self.m.config(state=tk.DISABLED)
                except StopIteration:
                    pass

                self.parent.img_panel.focus_force()

    def save_state(self):
        return self.drops

    def load_from_state(self, state):
        self.m.config(state=tk.NORMAL)
        self.m.delete(1.0, tk.END)
        self.m.config(state=tk.DISABLED)
        self.drops = state.get('drops', dict())
        for k, v in self.drops.items():
            for i in range(len(v)):
                if not isinstance(v[i], dict):
                    self.drops[k][i] = {'item_name': None, 'input': v[i], 'extra': ''}
        for run in sorted(self.drops.keys(), key=lambda x: int(x)):
            for drop in self.drops[run]:
                self.display_drop(drop=drop, run_no=run)
