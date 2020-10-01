import os
import time
import logging
import tkinter as tk
import utils.other_utils
from memory_reader import reader
from utils import tk_dynamic as tkd, tk_utils, sound, other_utils
from tkinter import ttk


class MFRunTimer(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self._start = 0.0
        self._session_start = time.time()
        self.session_time = 0.0
        self._laptime = 0.0
        self.is_running = False
        self.is_paused = False
        self._waiting_for_delay = False
        self.cached_is_ingame = False
        self.sessionstr = tk.StringVar()
        self.timestr = tk.StringVar()
        self.no_of_laps = tk.StringVar()
        self.total_laps = tk.StringVar()
        self.min_lap = tk.StringVar()
        self.avg_lap = tk.StringVar()
        self.laps = []
        self._make_widgets()
        self.automode_active = self.main_frame.automode

        self._update_timers()

    def _make_widgets(self):
        flt = tkd.Frame(self)
        flt.pack(fill=tk.X, expand=tk.NO)
        self.c1, self.circ_id = tk_utils.add_circle(flt, 14, 'red')
        self.c1.grid(row=0, column=0, padx=3, pady=3)
        tkd.Label(flt, textvariable=self.sessionstr, font='arial 10').grid(row=0, column=1, sticky=tk.N, padx=20)
        self._set_time(self.session_time, for_session=True)

        tkd.Label(self, textvariable=self.timestr, font='arial 20').pack(fill=tk.X, expand=False, pady=4)
        self._set_time(0, for_session=False)

        l2f = tkd.Frame(self)
        l2f.pack(pady=2)
        tkd.Label(l2f, text='---- Run count:', font='arial 12').pack(side=tk.LEFT)
        tkd.RunLabel(l2f, textvariable=self.no_of_laps, font='arial 17').pack(side=tk.LEFT)
        tkd.RunLabel(l2f, textvariable=self.total_laps, font='helvetica 12').pack(side=tk.LEFT)
        tkd.Label(l2f, text='----', font='arial 12').pack(side=tk.LEFT)
        self._set_laps(add_lap=False)

        tkd.Label(self, textvariable=self.min_lap, font='arial 11').pack(fill=tk.X, expand=False, pady=1, padx=2)
        self._set_fastest()

        tkd.Label(self, textvariable=self.avg_lap, font='arial 11').pack(fill=tk.X, expand=False, pady=1, padx=2)
        self._set_average()

        lf0 = tkd.Frame(self)
        lf0.pack()
        scrollbar = ttk.Scrollbar(lf0, orient=tk.VERTICAL)
        self.m = tkd.Listbox(lf0, selectmode=tk.BROWSE, height=5, yscrollcommand=scrollbar.set, font='courier 12', activestyle=tk.NONE)
        self.m.bind('<FocusOut>', lambda e: self.m.selection_clear(0, tk.END))
        self.m.bind('<MouseWheel>', lambda e: self.m.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=1)

    def _update_timers(self):
        self._update_lap_time()
        self._update_session_time()
        self._timer = self.after(50, self._update_timers)

    def _update_lap_time(self):
        if self.is_running:
            self._laptime = time.time() - self._start
            self._set_time(self._laptime, for_session=False)

    def _update_session_time(self):
        if not self.is_running and not reader.one_of_processes_exists([reader.D2_SE_EXE, reader.D2_GAME_EXE]):
            self._session_start = time.time() - self.session_time
        self.session_time = time.time() - self._session_start
        self._set_time(self.session_time, for_session=True)

    def _check_entered_game(self, advanced_mode=False):
        if advanced_mode:
            if self.main_frame.d2_reader is None:
                self.main_frame.load_memory_reader(show_err=False)
                self._game_check = self.after(50, lambda: self._check_entered_game(advanced_mode=advanced_mode))
                return
            else:
                try:
                    is_ingame = self.main_frame.d2_reader.in_game()

                # Handle exceptions occurring with the memory reading (for example if d2 was closed while app is running)
                except other_utils.pymem_err_list as e:
                    logging.debug(e)
                    self.main_frame.load_memory_reader(show_err=False)
                    if self.main_frame.advanced_error_thrown:
                        self.main_frame.options_tab.tab3.automode_var.set('0')
                        self.main_frame.options_tab.tab3.toggle_automode_btn(first=False, show_error=False)
                    else:
                        self._game_check = self.after(50, lambda: self._check_entered_game(advanced_mode=advanced_mode))
                    return

            # Stop when exiting game, and start when entering game (NB: not calling stop/start)
            if self.cached_is_ingame and not is_ingame and not self.is_paused:
                if self.main_frame.stop_when_leaving:
                    self.stop()
                self.cached_is_ingame = is_ingame
            elif not self.cached_is_ingame and is_ingame and not self.is_paused:
                self.stop_start()
                self.cached_is_ingame = is_ingame
        else:
            # Simple automode - If file was moved / during runtime of the app, it doesn't crash with this line
            stamp = os.stat(self.char_file_path).st_mtime if os.path.isfile(self.char_file_path) else self.cached_file_stamp
            if stamp > (self.cached_file_stamp + 1) and not self.is_paused:
                self.stop_start()
                self.cached_file_stamp = stamp

        self._game_check = self.after(50, lambda: self._check_entered_game(advanced_mode=advanced_mode))

    def _set_time(self, elap, for_session):
        time_str = utils.other_utils.build_time_str(elap)
        if for_session:
            self.session_time_str = time_str
            self.sessionstr.set('Session time: ' + self.session_time_str)
        else:
            self.timestr.set(time_str)

    def _set_laps(self, add_lap):
        run_count = len(self.laps)
        if add_lap:
            run_count += 1
        self.no_of_laps.set(run_count)
        self.total_laps.set('(' + str(run_count + self.main_frame.profile_tab.tot_laps) + ')')

    def _set_fastest(self):
        if self.laps:
            self.min_lap.set('Fastest time: %s' % utils.other_utils.build_time_str(min(self.laps)))
        else:
            self.min_lap.set('Fastest time: --:--:--.-')

    def _set_average(self):
        if self.laps:
            self.avg_lap.set('Average time: %s' % utils.other_utils.build_time_str(sum(self.laps) / len(self.laps)))
        else:
            self.avg_lap.set('Average time: --:--:--.-')

    def load_from_state(self, state):
        self.laps = []
        self.m.delete(0, tk.END)
        self.session_time = state.get('session_time', 0)
        self._session_start = time.time() - self.session_time
        for lap in state.get('laps', []):
            self.lap(lap, force=True)
        self._set_laps(add_lap=False)
        self._set_fastest()
        self._set_average()
        self._set_time(self.session_time, for_session=True)

    def start(self, play_sound=True):
        def update_start():
            if self.is_paused:
                self.pause()
            self.c1.itemconfigure(self.circ_id, fill='green3')
            self._start = time.time() - self._laptime
            # self._update_lap_time()
            self.is_running = True
            self._set_laps(self.is_running)
            self._waiting_for_delay = False

        if not self.is_running:
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)
            delay = self.main_frame.start_run_delay_seconds
            if delay > 0:
                if self._waiting_for_delay:
                    return
                self._waiting_for_delay = True
                self.after(int(delay*1000), update_start)
            else:
                update_start()

    def stop(self, play_sound=True):
        if self.is_running:
            self.lap(self._laptime)
            self.c1.itemconfigure(self.circ_id, fill='red')
            self._laptime = 0.0
            self.is_running = False
            self._set_time(0, for_session=False)
            # self.after_cancel(self._timer)
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)

    def stop_start(self):
        self.stop(play_sound=False)
        self.start(play_sound=True)

    def lap(self, laptime, force=False):
        if self.is_running or force:
            self.laps.append(laptime)
            str_n = ' ' * max(3 - len(str(len(self.laps))), 0) + str(len(self.laps))
            self.m.insert(tk.END, 'Run ' + str_n + ': ' + utils.other_utils.build_time_str(self.laps[-1]))
            self.m.yview_moveto(1)
            self._set_laps(add_lap=False)
            self._set_fastest()
            self._set_average()

    def delete_prev(self):
        if self.laps:
            self.m.delete(tk.END)
            self.laps.pop()
            self._set_laps(add_lap=self.is_running)
            self._set_fastest()
            self._set_average()

    def delete_selected_run(self):
        if not self.m.curselection():
            return
        sel = self.m.selection_get()
        if tk_utils.mbox(msg='Do you want to delete the run:\n%s' % sel, title='Warning'):
            all_runs = self.m.get(0, tk.END)
            sel_idx = all_runs.index(sel)

            self.laps.pop(sel_idx)
            self.m.delete(sel_idx, tk.END)

            for run in all_runs[sel_idx+1:]:
                tmp = run[:run.find(':')]
                run_no = tmp[tmp.rfind(' ')+1:]
                prev_no = str(int(run_no) - 1)
                if len(prev_no) < len(run_no):
                    self.m.insert(tk.END, run.replace(run_no, ' ' + prev_no, 1))
                else:
                    self.m.insert(tk.END, run.replace(run_no, prev_no, 1))
            self.m.yview_moveto(1)

            self._set_laps(add_lap=self.is_running)
            self._set_fastest()
            self._set_average()

    def pause(self):
        if not self.is_paused:
            self.pause_lab = tkd.PauseButton(self, font='arial 24 bold', text='Resume', command=self.pause,
                                             bg=self.main_frame.theme.pause_button_color,
                                             fg=self.main_frame.theme.pause_button_text)
            self.pause_lab.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            self.c1.itemconfigure(self.circ_id, fill='red')
            self._set_time(self._laptime, for_session=False)
            self._set_time(self.session_time, for_session=True)
            # if self.is_running:
            #     self.after_cancel(self._timer)
            # self.after_cancel(self._sess_timer)
            self.after_cancel(self._timer)
            self.is_paused = True
        else:
            self.pause_lab.destroy()
            self._start = time.time() - self._laptime
            self._session_start = time.time() - self.session_time
            if self.is_running:
                self.c1.itemconfigure(self.circ_id, fill='green3')
                # self._update_lap_time()
            # self._update_session_time()
            self._update_timers()

            if self.automode_active:
                if self.main_frame.automode == 1 and os.path.isfile(self.char_file_path):
                    self.cached_file_stamp = os.stat(self.char_file_path).st_mtime
                elif self.main_frame.automode == 2:
                    try:
                        self.cached_is_ingame = self.main_frame.d2_reader.in_game()
                    except other_utils.pymem_err_list:
                        pass
            self.is_paused = False

    def reset_lap(self):
        if self.is_running:
            self._start = time.time()
            self._laptime = 0.0
            self._set_time(self._laptime, for_session=False)

    def reset_session(self):
        if self.is_running:
            self.stop()
        self._start = time.time()
        self._laptime = 0.0
        self.session_time = 0.0
        self._session_start = time.time()
        self.laps = []
        self.m.delete(0, tk.END)
        self._set_time(self._laptime, for_session=False)
        self._set_time(self.session_time, for_session=True)
        self._set_laps(add_lap=self.is_running)
        self._set_fastest()
        self._set_average()

    def save_state(self):
        return dict(laps=self.laps, session_time=self.session_time)

    def toggle_automode(self, char_name):
        if hasattr(self, '_game_check'):
            self.after_cancel(self._game_check)

        if self.main_frame.automode:
            if self.main_frame.automode == 1:
                d2_save_path = os.path.normpath(self.main_frame.game_path())
                char_extension = char_name + self.main_frame.character_file_extension()
                self.char_file_path = os.path.join(d2_save_path, char_extension)

                if utils.other_utils.test_mapfile_path(d2_save_path, char_extension):
                    self.cached_file_stamp = os.stat(self.char_file_path).st_mtime
                    self._check_entered_game(advanced_mode=False)

                    self.automode_active = True
                else:
                    self.automode_active = False
                    self.main_frame.am_lab.configure(state=tk.NORMAL)
                    self.main_frame.am_lab.delete(1.0, tk.END)
                    self.main_frame.am_lab.insert(tk.END, "Automode: ", "am")
                    self.main_frame.am_lab.insert(tk.END, "OFF", "off")
                    self.main_frame.am_lab.config(width=15)
                    self.main_frame.am_lab.configure(state=tk.DISABLED)
            elif self.main_frame.automode == 2:
                try:
                    self.cached_is_ingame = self.main_frame.d2_reader.in_game()
                except other_utils.pymem_err_list:
                    pass
                self._check_entered_game(advanced_mode=True)
                self.automode_active = True
        else:
            self.automode_active = False
