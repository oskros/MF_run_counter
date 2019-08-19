# Diablo 2 MF run counter
Supports Windows 7 and Windows 10 (have not tested on any other OS)
![GUI](https://github.com/oskros/MF_counter_releases/blob/master/UI_showcase.png?raw=true)

## How to use
1) To run on your computer, go to releases (https://github.com/oskros/MF_counter_releases/releases) and download the .exe file from the latest release. 
2) Place the .exe file in your preferred folder
3) You might be prompted by Windows not recognizing the application publisher (I am not going to pay 100$ a year for this lol). Simply click "more info" and then "Run anyway" when Windows asks. See pictures below
    
    ![winblock1](https://github.com/oskros/MF_counter_releases/blob/master/Unrecognized1.png?raw=true)
    ![winblock2](https://github.com/oskros/MF_counter_releases/blob/master/Unrecognized2.png?raw=true)
4) You can make the application trusted by following the steps suggested here: https://www.windowscentral.com/how-disable-smartscreen-trusted-app-windows-10
5) The first time you run the .exe file, a config file is created named "mf_config.ini", which can be edited in Notepad. You can edit the mf_config.ini file to change various settings for the program - Note that hotkeys should be changed from within the application. 

## Features
### System wide hotkeys
You are able to customize hotkeys for each of the commands in the application. The hotkeys are system wide, so you do not need to place focus on the application to use them. However, this means that while the application is open, it overrides any other program using this specific hotkey.
It is possible to disable a command from having a hotkey by choosing "NO_BIND"
There are 2 hidden hotkeys: 'control+shift+PgDn' and 'control+shift+PgUp' for switching between tabs in the app (eg. if you wanna confirm the drop you just added is in fact saved)

### Run counting
Start a new run by pressing the "Start new run" button, or using the assigned hotkey (default 'alt+Q'). In case a run is already active, this button will end it and start a new run.
End the run by pressing the "End this run" button, or using the assigned hotkey (default 'alt+W').
In case of mistakes, the previous run can be deleted using the assigned hotkey (default 'control+delete')
If the user desires, the current run timer can be reset using the "Reset lap" button or using the assigned hotkey (default 'alt+R').

### Drop logging
You add a drop to the current run (or previous run if no run is currently active) by pressing the "Add drop" button or using the assigned hotkey (default 'alt+A'). It will then be registered in the "Drops" tab under the run where it was found.
In case a drop was added by mistake, it can be deleted by highlighting it and clicking the "Delete selection" button under the "Drops" tab, or by pressing the Delete button on your keyboard while the drop is highlighted (this hotkey is not system wide).

### Session timer
The session timer will start as soon as you open the program and run as long as the program is open (an not put on pause).

### Pausing
In case you need to take a break from the computer, the counter can be paused by using the assigned hotkey (default 'control+space'). This will pause both the run timer (if a run is active) and the session timer.

### Saving results
The current session is saved automatically every 30 seconds (to prevent data loss in case of crashes) and also saved automatically when you close the app. You can click the "Save & reset" button to reset the session and save the session results to a .txt file with name equal to the current time stamp (YYYY-MM-DD HH:MM:SS) - Example of the .txt file is included below. 
                  
      Total session time: 00:04:30.5
      Total run time:     00:04:17.3
      Average run time:   00:01:04.3
      Fastest run time:   00:00:44.5
      Session percentage spent in runs: 95.1%
      
      
      Run   1: 00:00:57:9
      Run   2: 00:00:44:5 --- Shako, Skullders
      Run   3: 00:01:11:6 
      Run   4: 00:01:24:3 --- Nagelring 25%
                  
### Dragging
Window can be dragged on the Diablo 2 banner. Window position is saved in the config file, such that it opens where you closed it.

### Extra options
In the config file you have the option to set the following to 0 (False) or 1 (True). This is also possible from within the application under "Options" and then under "General".
- always_on_top: choose whether the app window is on top of other programs (default True)
- tab_keys_global: choose whether changing tabs with ctrl+shift+pgup/pgdn works system wide, or only when app is in focus (default True)
- check_for_new_version: choose whether app should search for a new release on GitHub when opening (default True)
- enable_sound_effects: choose whether a sound should be played when pressing start/stop buttons
