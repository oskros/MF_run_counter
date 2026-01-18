import os
import time
import logging
import tkinter as tk
from memory_reader import reader, reader_utils
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
        self.is_user_paused = False
        self._waiting_for_delay = False
        self.cached_is_ingame = False
        self.session_running = False
        self.sessionstr = tk.StringVar()
        self.run_display_str = tk.StringVar()
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

        tkd.Label(self, textvariable=self.run_display_str, font='arial 20').pack(fill=tk.X, expand=False, pady=4)
        if self.main_frame.track_kills_min:
            self._set_kills_per_min(0)
        else:
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
        # Determine if we should be paused based on all automatic pause conditions
        should_be_paused = False
        if not self.is_user_paused:
            if self.main_frame.pause_on_esc_menu:
                memory_pause = getattr(self.main_frame.d2_reader, 'is_game_paused', lambda: False)()
                if memory_pause:
                    should_be_paused = True
            if self.main_frame.pause_in_town:
                in_town = getattr(self.main_frame.d2_reader, 'is_player_in_town', lambda: False)()
                if in_town:
                    should_be_paused = True
        
        # Only toggle pause if the state doesn't match what it should be
        if not self.is_user_paused and self.is_paused != should_be_paused:
            self.pause(user_paused=False)
        
        self._update_run_display()
        self._update_session_time()
        self._timer = self.after(50, self._update_timers)

    def _update_run_display(self):
        if self.is_running and not self.is_paused:
            self._laptime = time.time() - self._start
        if self.main_frame.track_kills_min:
            self._set_kills_per_min(self._laptime)
        else:
            self._set_time(self._laptime, for_session=False)

    def is_game_open(self):
        if self.main_frame.automode == 2:
            return self.main_frame.d2_reader is not None
        else:
            return reader_utils.one_of_processes_exists([reader.D2_SE_EXE, reader.D2_GAME_EXE, reader.D2R_EXE])

    def _update_session_time(self):
        if not (self.is_running or self.is_game_open()) or self.is_paused:
            self._session_start = time.time() - self.session_time
            self.session_running = False
        else:
            self.session_running = True
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
                        self.main_frame.options_tab.tab4.automode_var.set('0')
                        self.main_frame.options_tab.tab4.toggle_automode_btn(first=False, show_error=False)
                    else:
                        self._game_check = self.after(50, lambda: self._check_entered_game(advanced_mode=advanced_mode))
                    return

            # Stop when exiting game, and start when entering game. (NB: not calling stop/start)
            logging.debug(f'cached_is_ingame={self.cached_is_ingame}, is_ingame={is_ingame}, is_paused={self.is_user_paused}')
            if self.cached_is_ingame and not is_ingame and not self.is_user_paused:
                logging.debug(f'Left game: Bool end_run_in_menu={self.main_frame.end_run_in_menu}')
                if self.main_frame.end_run_in_menu:
                    logging.debug(f'Left game: Stopping run. Bool is_running={self.is_running}')
                    self.stop()
                self.cached_is_ingame = is_ingame
            elif not self.cached_is_ingame and is_ingame and not self.is_user_paused:
                logging.debug(f'Joined game: Starting run. Bool is_running={self.is_running}')
                self.stop_start()
                self.cached_is_ingame = is_ingame
        else:
            # Simple automode - if any file is updated, run is started
            d2_save_path = os.path.normpath(self.main_frame.game_path)
            extensions = ('ctl', 'ctlo', 'd2x')
            files = [os.path.join(d2_save_path, f) for f in other_utils.listdir(d2_save_path) if f.endswith(extensions)]
            if files:
                cur_file = max(files, key=lambda f: os.stat(f).st_mtime)
                stamp = os.stat(cur_file).st_mtime

                if stamp > (self.cached_file_stamp + 1) and not self.is_paused:
                    self.stop_start()
                    self.cached_file_stamp = stamp

        self._game_check = self.after(50, lambda: self._check_entered_game(advanced_mode=advanced_mode))

    def _set_time(self, elap, for_session):
        time_str = other_utils.build_time_str(elap)
        if for_session:
            self.session_time_str = time_str
            self.sessionstr.set('Session time: ' + self.session_time_str)
        else:
            self.run_display_str.set(time_str)

    def _calculate_kills_per_min(self, total_kills, run_time):
        """Calculate kills/min from total kills and run time."""
        try:
            total_kills_int = int(total_kills or 0)
            return other_utils.safe_divide(total_kills_int * 60, run_time, decimals=2, default=0)
        except (ValueError, TypeError):
            return 0

    def _set_kills_per_min(self, elap):
        """Set the display to show kills/min for the current run."""
        kills_per_min = 0
        if hasattr(self.main_frame, 'advanced_stats_tracker'):
            total_kills = self.main_frame.advanced_stats_tracker.tot_kills_sv.get()
            kills_per_min = self._calculate_kills_per_min(total_kills, elap)

        self.run_display_str.set(f'{kills_per_min:.2f} kpm')

    def _set_laps(self, add_lap):
        run_count = len(self.laps)
        if add_lap:
            run_count += 1
        self.no_of_laps.set(run_count)
        self.total_laps.set('(' + str(run_count + self.main_frame.profile_tab.tot_laps) + ')')

    def _set_fastest(self):
        if self.main_frame.track_kills_min:
            kpm_lst = [l.get('Kills/min', 0) for l in self.laps if isinstance(l, dict)]
            self.min_lap.set(f'Highest kpm: {max(kpm_lst):.2f}' if kpm_lst else 'Highest kpm: --')
        else:
            if self.laps:
                self.min_lap.set('Fastest time: %s' % other_utils.build_time_str(min(l['Run time'] for l in self.laps)))
            else:
                self.min_lap.set('Fastest time: --:--:--.-')

    def _set_average(self):
        if self.main_frame.track_kills_min:
            kpm_lst = [l.get('Kills/min', 0) for l in self.laps if isinstance(l, dict)]
            avg_kpm = other_utils.safe_avg(kpm_lst, decimals=2, default='')
            self.avg_lap.set(f'Average kpm: {avg_kpm:.2f}' if avg_kpm != '' else 'Average kpm: --')
        else:
            if self.laps:
                self.avg_lap.set('Average time: %s' % other_utils.build_time_str(sum(l['Run time'] for l in self.laps) / len(self.laps)))
            else:
                self.avg_lap.set('Average time: --:--:--.-')

    def load_from_state(self, state):
        self.laps = []
        self.m.delete(0, tk.END)
        self.session_time = state.get('session_time', 0)
        self._session_start = time.time() - self.session_time
        for lap_info in state.get('laps', []):
            # Backwards compatibility with old profiles
            if not isinstance(lap_info, dict):
                self.lap({'Run time': lap_info})
            else:
                self.lap(lap_info)
        self._set_laps(add_lap=False)
        self._set_fastest()
        self._set_average()
        self._set_time(self.session_time, for_session=True)

    def build_lap(self):
        out = dict()
        out['Run time'] = self._laptime
        out['Real time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        out['MF'] = self.main_frame.advanced_stats_tracker.mf_sv.get()
        out['Min MF'] = self.main_frame.advanced_stats_tracker.min_mf
        out['Max MF'] = self.main_frame.advanced_stats_tracker.max_mf
        out['Players X'] = self.main_frame.advanced_stats_tracker.players_x_sv.get()
        out['XP Gained'] = self.main_frame.advanced_stats_tracker.run_char_xp
        out['Uniques kills'] = self.main_frame.advanced_stats_tracker.unique_kills_sv.get()
        out['Champions kills'] = self.main_frame.advanced_stats_tracker.champ_kills_sv.get()
        out['Minion kills'] = self.main_frame.advanced_stats_tracker.minion_kills_sv.get()
        out['Total kills'] = self.main_frame.advanced_stats_tracker.tot_kills_sv.get()
        out['Level'] = self.main_frame.advanced_stats_tracker.level_sv.get()
        out['Name'] = self.main_frame.advanced_stats_tracker.name_sv.get()
        out['Map seed'] = self.main_frame.advanced_stats_tracker.map_seed
        out['Areas visited'] = sorted(self.main_frame.advanced_stats_tracker.run_areas_visited)
        
        # Calculate and store kills/min for this run
        out['Kills/min'] = self._calculate_kills_per_min(out['Total kills'], self._laptime)

        return out

    def start(self, play_sound=True):
        def update_start():
            if self.is_paused:
                self.pause()
            self.c1.itemconfigure(self.circ_id, fill='green3')
            self._start = time.time() - self._laptime
            # self._update_run_display()
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
            self.lap(self.build_lap())
            self.main_frame.advanced_stats_tracker.reset_at_new_run()

            self.c1.itemconfigure(self.circ_id, fill='red')
            self._laptime = 0.0
            self.is_running = False
            if self.main_frame.track_kills_min:
                self._set_kills_per_min(0)
            else:
                self._set_time(0, for_session=False)
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)

    def stop_start(self):
        self.stop(play_sound=False)
        self.start(play_sound=True)

    def _format_run_display(self, lap_info):
        """Format run display string based on track_kills_min setting."""
        if self.main_frame.track_kills_min:
            kpm = lap_info.get('Kills/min', 0)
            return f"{kpm:.2f} kpm"
        else:
            return other_utils.build_time_str(lap_info['Run time'])

    def _refresh_run_list(self):
        """Refresh the run list display based on current track_kills_min setting."""
        self.m.delete(0, tk.END)
        for idx, lap_info in enumerate(self.laps, 1):
            str_n = ' ' * max(3 - len(str(idx)), 0) + str(idx)
            self.m.insert(tk.END, 'Run ' + str_n + ': ' + self._format_run_display(lap_info))
        self.m.yview_moveto(1)

    def lap(self, lap_info):
        self.laps.append(lap_info)
        str_n = ' ' * max(3 - len(str(len(self.laps))), 0) + str(len(self.laps))
        self.m.insert(tk.END, 'Run ' + str_n + ': ' + self._format_run_display(lap_info))
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
        if tk_utils.MessageBox(msg='Do you want to delete the run:\n%s' % sel, title='Warning').returning:
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

    def pause(self, user_paused=True):
        if not self.is_paused:
            self.pause_lab = tkd.PauseButton(self, font='arial 24 bold', text='Resume', command=self.pause,
                                             bg=self.main_frame.theme.colors['pause_button_color'],
                                             fg=self.main_frame.theme.colors['pause_button_text'])
            self.pause_lab.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            self.c1.itemconfigure(self.circ_id, fill='red')
            self.is_paused = True
        else:
            self.pause_lab.destroy()
            self._start = time.time() - self._laptime
            self._session_start = time.time() - self.session_time
            if self.is_running:
                self.c1.itemconfigure(self.circ_id, fill='green3')

            if self.automode_active:
                if self.main_frame.automode == 1:
                    files = self.get_char_files()
                    if files:
                        self.cached_file_stamp = max(os.stat(f).st_mtime for f in files)
                elif self.main_frame.automode == 2 and user_paused:
                    try:
                        self.cached_is_ingame = self.main_frame.d2_reader.in_game()
                    except other_utils.pymem_err_list:
                        pass
            self.is_paused = False
        if user_paused:
            self.is_user_paused = self.is_paused

    def reset_lap(self):
        if self.is_running:
            self._start = time.time()
            self._laptime = 0.0
            if self.main_frame.track_kills_min:
                self._set_kills_per_min(0)
            else:
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
        if self.main_frame.track_kills_min:
            self._set_kills_per_min(0)
        else:
            self._set_time(self._laptime, for_session=False)
        self._set_time(self.session_time, for_session=True)
        self._set_laps(add_lap=self.is_running)
        self._set_fastest()
        self._set_average()

    def save_state(self):
        return dict(laps=self.laps, session_time=self.session_time)

    def get_char_files(self):
        d2_save_path = os.path.normpath(self.main_frame.game_path)
        extensions = ('ctl', 'ctlo', 'd2x')
        files = [os.path.join(d2_save_path, f) for f in other_utils.listdir(d2_save_path) if f.endswith(extensions)]
        return files

    def toggle_automode(self):
        if hasattr(self, '_game_check'):
            self.after_cancel(self._game_check)

        if self.main_frame.automode:
            if self.main_frame.automode == 1:
                files = self.get_char_files()
                if files:
                    self.cached_file_stamp = max(os.stat(f).st_mtime for f in files)
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
