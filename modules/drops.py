from utils import tk_dynamic as tkd, tk_utils, autocompletion
from utils.item_name_lists import NO_UNIQUE_MAP
import tkinter as tk
from tkinter import ttk
import time


class Drops(tkd.Frame):
    def __init__(self, main_frame, parent, **kw):
        tkd.Frame.__init__(self, parent, **kw)
        self.drops = dict()
        self.main_frame = main_frame

        self._make_widgets()

    def _make_widgets(self):
        tkd.Label(self, text='Drops', font='helvetica 14').pack()
        lf = tkd.Frame(self)
        lf.pack(expand=1, fill=tk.BOTH)
        scrollbar = ttk.Scrollbar(lf, orient=tk.VERTICAL)

        self.m = tkd.Text(lf, height=8, width=23, yscrollcommand=scrollbar.set, font='courier 11', wrap=tk.WORD, state=tk.DISABLED, cursor='', exportselection=1, name='droplist', borderwidth=2)
        self.m.bind('<Double-Button-1>', lambda _: (self.main_frame.img_panel.focus_force(), self.add_drop()))

        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(1, 2), padx=1)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(2, 1), padx=0)

    def add_drop(self):
        drop = autocompletion.acbox(enable=True, title='Add drop', unid_mode=self.main_frame.autocompletion_unids, add_to_last_run=self.main_frame.add_to_last_run)
        if not drop or drop['input'] == '':
            return

        if drop['item_name'] is not None:
            for i, item in enumerate(self.main_frame.grail_tab.grail):
                if self.main_frame.autocompletion_unids:
                    base = ' '.join(drop['item_name'].split(' ')[:-1])
                    if base in NO_UNIQUE_MAP:
                        drop['TC'] = NO_UNIQUE_MAP[base].get('TC', '')
                        drop['Item Class'] = NO_UNIQUE_MAP[base].get('Item Class', '')
                        break
                    if base == item['Base Item']:
                        drop['TC'] = item.get('TC', '')
                        drop['Item Class'] = item.get('Item Class', '')
                        break

                if item['Item'] == drop['item_name']:
                    prefix = ''
                    drop['Grailer'] = 'False'
                    drop['Eth Grailer'] = ''
                    if item.get('Found', False) is False:
                        if self.main_frame.auto_upload_herokuapp:
                            resp = self.main_frame.grail_tab.upload_to_herokuapp(
                                upd_dict={item['Item']: True},
                                show_confirm=False,
                                pop_up_msg="Congrats, a new drop! Add it to grail?\n\nHerokuapp login info:",
                                pop_up_title="Grail item")
                        else:
                            resp = tk_utils.mbox(msg="Congrats, a new drop! Add it to local grail?", title="Grail item")
                        if resp is not None:
                            self.main_frame.grail_tab.update_grail_from_index(i)
                            prefix += '(*)'
                            drop['Grailer'] = 'True'

                    if drop.get('eth', False) is True:
                        drop['Eth Grailer'] = 'False'

                    if drop.get('eth', False) is True and item.get('FoundEth', False) is False:
                        if self.main_frame.auto_upload_herokuapp:
                            resp = self.main_frame.grail_tab.upload_to_herokuapp(
                                eth_dict={item['Item']: True},
                                show_confirm=False,
                                pop_up_msg="Congrats, a new eth drop! Add it to eth grail?\n\nHerokuapp login info:",
                                pop_up_title="Eth grail item")
                        else:
                            resp = tk_utils.mbox(msg="Congrats, a new eth drop! Add it to local eth grail?", title="Eth grail item")
                        if resp is not None:
                            self.main_frame.grail_tab.grail[i].update({'FoundEth': True})
                            prefix += '(*)'
                            drop['Eth Grailer'] = 'True'

                    drop['input'] = (prefix + ' ' + drop['input']).strip()
                    drop['TC'] = item.get('TC', '')
                    drop['QLVL'] = item.get('QLVL', '')
                    drop['Item Class'] = item.get('Item Class', '')
                    drop['Rarity'] = item.get('Rarity', '')
                    break

        last_run = drop.pop('last_run', False)
        run_no = len(self.main_frame.timer_tab.laps)
        if self.main_frame.timer_tab.is_running:
            run_no += 1
        if last_run and run_no > 0:
            run_no -= 1
        self.main_frame.add_to_last_run = last_run

        drop['Real time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        drop['Profile'] = self.main_frame.active_profile

        self.drops.setdefault(str(run_no), []).append(drop)
        self.display_drop(drop=drop, run_no=run_no)

    def display_drop(self, drop, run_no):
        line = 'Run %s: %s' % (run_no, drop['input'].strip())
        if self.m.get('1.0', tk.END) != '\n':
            line = '\n' + line
        self.m.config(state=tk.NORMAL)
        self.m.insert(tk.END, line)
        self.m.yview_moveto(1)
        self.m.config(state=tk.DISABLED)

    def delete_selected_drops(self):
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

            self.main_frame.img_panel.focus_force()

    def save_state(self):
        return dict(drops=self.drops)

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

    def reset_session(self):
        self.drops = dict()
        self.m.config(state=tk.NORMAL)
        self.m.delete(1.0, tk.END)
        self.m.config(state=tk.DISABLED)
