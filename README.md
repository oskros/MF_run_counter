# Diablo 2 MF run counter
Supports: Windows 7 and Windows 10 (have not tested on any other OS)

1) To run on your computer, go to releases and download the .exe file from the latest release. 
2) Place the .exe file in your preferred folder
3) The first time you run the .exe file, a config file is created named "mf_config.ini", which can be edited in Notepad. You can edit the mf_config.ini file to change various settings for the program - Note that hotkeys should be changed from within the application

Features:
- SYSTEM WIDE HOTKEYS: You are able to customize hotkeys for each of the commands in the application. The hotkeys are system wide, so 
                       you do not need to place focus on the application to use them. However, this means that while the application 
                       is open, it overrides any other program using this specific hotkey.
                       It is possible to disable a command from having a hotkey by choosing "NO_BIND"
                       There are 2 hidden hotkeys: 'control+shift+PgDn' and 'control+shift+PgUp' for changing
- SESSION TIMER: The session timer will start as soon as you open the program and run as long as the program is open.
- RUN COUNTING: Start a run by pressing the "Start" button, or using the assigned hotkey (default 'alt+Q').
                End a run by pressing the "End" button, or using the assigned hotkey (default 'alt+W').
                You can also use the "StopStart" hotkey (default 'alt+E') to stop the current run if one is active, and start a new run 
                in one click.
                In case of mistakes, the previous run can be deleted using the assigned hotkey (default 'control+delete')
                If the user desires, the current run timer can be reset using the "Reset lap" button or using the assigned hotkey
                (default 'alt+R')
- DROP LOGGING: You add a drop to the current run (or previous run if no run is currently active) by pressing the "Add drop" button or
                using the assigned hotkey (default 'alt+A'). It will then be registered in the "Drops" tab under the run where it was
                found.
                In case a drop was added by mistake, it can be deleted by highlighting it and clicking the "Delete selection" button
                under the "Drops" tab, or by pressing the Delete button on your keyboard while the drop is highlighted (this hotkey is
                not system wide)
- PAUSING: In case you need to take a break from the computer, the counter can be paused by using the assigned hotkey 
           (default 'alt+space'). This will pause both the run timer (if a run is active) and the session timer.
- SAVING RESULTS: When closing the app (clicking the X in upper right corner, or alt+F4) or clicking the "Reset Session" button, you
                  are asked whether you want to save session results. Clicking yes will generate a .txt file named with the current 
                  time stamp (YYYY-MM-DD HH:MM:SS). Example of save file with 4 runs:
                  
                  """
                  Total session time: 00:04:30.5
                  Total run time:     00:04:17.3
                  Average run time:   00:01:04.3
                  Fastest run time:   00:00:44.5
                  Session percentage spent in runs: 95.1%
                  
                  
                  Run   1: 00:00:57:9
                  Run   2: 00:00:44:5 --- Shako, Skullders
                  Run   3: 00:01:11:6 
                  Run   4: 00:01:24:3 --- Nagelring 25%
                  """              
- DRAGGING: Window can be dragged on the Diablo 2 banner. Widget position is saved in the config file, such that it opens
            where you closed it.
- EXTRA CONFIG FEATURES: In the config file you have the option to set the following to 0 (False) or 1 (True).
                         This is also possible from within the application under "Options" and then under "Flags".
   - always_on_top: choose whether the app window is on top of other programs (default True)
   - tab_keys_global: choose whether changing tabs with ctrl+shift+pgup/pgdn works system wide, or only when app is in focus 
     (default True)
   - check_for_new_version: choose whether app should search for a new release on GitHub when opening (default True)
   - enable_sound_effects: choose whether a sound should be played when pressing start/stop buttons
