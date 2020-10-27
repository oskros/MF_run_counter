import tkinter as tk
import re
from init import *
from utils.item_name_lists import FULL_ITEM_LIST, ITEM_ALIASES, UNID_ITEM_LIST, ETH_ITEM_LIST


class AutocompleteEntry:
    def __init__(self, master, width, textvariable, enable=True, unid_mode=False):
        self.chosen = None
        self.enable = enable
        self.unid_mode = unid_mode
        self.master = master
        self.width = width
        self.var = textvariable
        self.entry = tk.Entry(master, textvariable=self.var)
        self.entry.pack(fill=tk.X, padx=4)
        self.entry.focus()

        self.var.trace_add('write', lambda name, index, mode: self.changed(name, index, mode))
        self.entry.bind("<Up>", self.move_up)
        self.entry.bind("<Down>", self.move_down)
        self.entry.bind("<Tab>", self.selection)

        self.listboxUp = False

    def changed(self, name=None, index=None, mode=None):
        var = self.var.get()
        if var == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            if self.enable:
                words = self.comparison(var)
                if var.lower().startswith('eth '):
                    words.extend(self.comparison(var[4:], eth=True))
            else:
                words = []

            if words:
                if self.listboxUp:
                    self.listbox.destroy()
                self.listbox = tk.Listbox(self.master, width=self.width, height=min(len(words), 6))
                self.listbox.bind("<Double-Button-1>", self.selection)
                self.listbox.bind("<Tab>", self.selection)
                self.listbox.place(relx=0, rely=0.3)
                self.listbox.tkraise()
                self.listboxUp = True

                self.listbox.delete(0, tk.END)
                for w in words:
                    self.listbox.insert(tk.END, w)
            else:
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False

    def selection(self, event=None):
        if self.listboxUp:  # and self.listbox.curselection():
            self.chosen = self.listbox.get(tk.ACTIVE)
            self.var.set(self.chosen + ' ')
            self.listbox.destroy()
            self.listboxUp = False
            self.entry.icursor(tk.END)

    def move_up(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = tk.END
                hl_idx = tk.END
            else:
                index = self.listbox.curselection()[0]
                hl_idx = str(int(index) - 1)

            if index != '0':
                self.listbox.selection_clear(first=index)

                self.listbox.see(hl_idx)  # Scroll!
                self.listbox.selection_set(first=hl_idx)
                self.listbox.activate(hl_idx)

    def move_down(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
                hl_idx = '0'
            else:
                index = self.listbox.curselection()[0]
                hl_idx = str(int(index) + 1)

            if index != tk.END:
                self.listbox.selection_clear(first=index)

                self.listbox.see(hl_idx)  # Scroll!
                self.listbox.selection_set(first=hl_idx)
                self.listbox.activate(hl_idx)

    def comparison(self, var, eth=False):
        out = set()
        # regex to append a [']? after all letters, which is an optional argument for adding a hyphen
        # this means that for example typing in "mavinas" and "m'avina's" will yield the same results
        hyphen_escape = re.sub('([^a-zA-Z]*)', "\\1[']?", re.escape(var))
        # encapsulating with \b ensures that searches are done only at the start of each word
        # ".*" allows anything to follow after the already typed letters
        pattern = re.compile(r"\b" + hyphen_escape + r".*\b", flags=re.IGNORECASE)

        extras = list(ITEM_ALIASES.keys()) + UNID_ITEM_LIST if self.unid_mode else list(ITEM_ALIASES.keys())
        for w in FULL_ITEM_LIST + extras:
            if re.search(pattern, w):
                # Append true entry from the alias list - if none are found, add the match from original list
                i_name = ITEM_ALIASES.get(w, w)
                if eth:
                    if i_name in ETH_ITEM_LIST:
                        out.add('Eth ' + i_name)
                else:
                    out.add(i_name)
        return sorted(out)


class ACMbox(object):
    def __init__(self, title, enable=True, unid_mode=False):
        self.root = tk.Toplevel()
        self.root.geometry(
            '200x145+%s+%s' % (self.root.winfo_screenwidth() // 2 - 100, self.root.winfo_screenheight() // 2 - 72))
        self.root.update_idletasks()
        self.root.focus_set()
        self.root.iconbitmap(media_path + 'icon.ico')
        self.root.title(title)
        self.root.wm_attributes("-topmost", True)
        self.root.resizable(False, False)

        frm_1 = tk.Frame(self.root)
        frm_1.pack(ipadx=4, ipady=2, fill=tk.BOTH, expand=tk.Y)

        tk.Label(frm_1, text='Input your drop...').pack()

        tw = tk.StringVar()
        self.entry = AutocompleteEntry(frm_1, width=32, textvariable=tw, enable=enable, unid_mode=unid_mode)

        frm_2 = tk.Frame(frm_1)
        frm_2.pack(padx=4, pady=4)

        tk.Button(frm_2, width=8, text='OK', command=self.b1_action).pack(side=tk.LEFT)
        tk.Button(frm_2, width=8, text='Cancel', command=self.close_mod).pack(side=tk.LEFT)

        self.root.bind('<KeyPress-Return>', func=self.b1_action)
        self.root.bind('<KeyPress-Escape>', func=self.close_mod)

        # call self.close_mod when the close button is pressed
        self.root.protocol("WM_DELETE_WINDOW", self.close_mod)

        # a trick to activate the window (on windows 7)
        self.root.deiconify()

    def b1_action(self, event=None):
        if self.entry.listboxUp:
            self.entry.selection(event)
        else:
            item_name = self.entry.chosen
            eth_item = False
            if item_name is not None and item_name.startswith('Eth ') and item_name != 'Eth Rune':
                item_name = item_name[4:]
                eth_item = True
            user_input = self.entry.var.get().strip()
            extra_input = user_input.replace(item_name, '').strip().replace('  ', ' ') if item_name is not None else ''
            self.returning = {'item_name': item_name, 'input': user_input, 'extra': extra_input, 'eth': eth_item}
            self.root.quit()

    def close_mod(self, event=None):
        if self.entry.listboxUp:
            self.entry.listbox.destroy()
            self.entry.listboxUp = False
        else:
            self.returning = None
            self.root.quit()


def acbox(title='Drop', enable=True, unid_mode=False):
    msgbox = ACMbox(title, enable=enable, unid_mode=unid_mode)
    msgbox.root.mainloop()

    # the function pauses here until the mainloop is quit
    msgbox.root.destroy()
    return msgbox.returning


if __name__ == '__main__':
    print(acbox(enable=True))
