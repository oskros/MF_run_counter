# Diablo 2 MF run counter
You can find a video where I describe the application in detail here: https://www.youtube.com/watch?v=e4vcg8MdvrY&t=46s


![GUI](https://github.com/oskros/MF_counter_releases/blob/master/media/UI_showcase.png?raw=true)

## How to use
NB: Working on Windows 7 and Windows 10 (I have not tested on any other OS, but probably it wouldn't work)
1) To run on your computer, go to releases (https://github.com/oskros/MF_counter_releases/releases) and download the .exe file from the latest release. 
2) Place the .exe file in your preferred folder
3) You might be prompted by Windows not recognizing the application publisher (I am not going to pay 100$ a year for Windows to recognize me lol). Simply click "more info" and then "Run anyway" when Windows asks. See pictures below
    
    ![winblock1](https://github.com/oskros/MF_counter_releases/blob/master/media/Unrecognized1.png?raw=true)
    ![winblock2](https://github.com/oskros/MF_counter_releases/blob/master/media/Unrecognized2.png?raw=true)
4) You can make the application trusted by following the steps suggested here: https://www.windowscentral.com/how-disable-smartscreen-trusted-app-windows-10
5) The first time you run the .exe file, a config file is created in the same directory as the .exe, named "mf_config.ini", which can be edited in Notepad. While you can edit settings directly in the config file, I would recommend doing it from within the application. At first run, there is also a "Profiles" folder created, which stores save files for each of your created profiles.

## Features
### Automode
You can active automode in Options -> Automode. The automode automatically advance the run counter every time you create a new game by monitoring the 'latest change time' registered by the OS on your local character files - The local files are a little different on single player and multiplayer, hence the need for specifying the game mode when creating a profile (.d2s files in single player, and .map files in multiplayer).
To set-up automode, enter the game path to your save folder and click 'Apply'. Also make sure the character name specified in your profile is exactly the same as your in-game name, otherwise the automode will fail to start.

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
When adding a drop, the application will try and autocomplete the name of the drop using a full library of all available sets, uniques and runes.
In case a drop was added by mistake, it can be deleted by highlighting it and clicking the "Delete selection" button under the "Drops" tab, or by pressing the Delete button on your keyboard while the drop is highlighted (this hotkey is not system wide).

### Profiles
In the profile tab it is possible to create a separate run profile for each character and run type (eg. Chaos, Cows, Meph, etc.). In the profile tab you can view each saved session in the archive browser, where it is also possible to save the results to a .txt file or copy to clipboard. Profile data is saved as a .json under the "Profiles" folder that is created the first time you run the program.

### Grail logging
There is a tab called "Grail" - Here you can track all your progress in completing the d2 holy grail of collecting all items (and runes). Every time you add a new item that hasn't been found before, it can be added to the grail! Then it will appear in your found items with a "(\*)" in front of the name, to indicate it was a grailer. Furthermore, there is support with d2-holy-grail.herokuapp.com - You can both sync your local grail with the already logged progress there, and also upload any progress back to the webpage again! 
In order to view your grail progress there is both a "Grail controller" view, which is similar to the one found on herokuapp, but also a "Item table" view, where you see all items in a table with tons of information about each item.
You can also sync your local grail with already found items. Unfortunately, it is not possible to sync with any items added in your profiles prior to version 1.2.0, sorry!

### Session timer
The session timer will start as soon as you open the program and run as long as the program is open (an not put on pause).

### Pausing
In case you need to take a break from the computer, the counter can be paused by using the assigned hotkey (default 'control+space'). This will pause both the run timer (if a run is active) and the session timer.

### Saving results
The current session is saved automatically every 30 seconds (to prevent data loss in case of crashes) and also saved automatically when you close the app. You can click the "Archive & reset" button to reset the session and archive the session results to the profile. In the archive browser, it is possible to save a session or the full profile history to a .txt or .csv file, or copy to clipboard - Example of the .txt file is included below.
                  
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

### Automatic check for updates
The program automatically checks if a new version is available on start-up, providing a link to the release pages where you can download it. This features can be disabled under "Options" and then under "General"

### Color themes
Three different themes for the application have been created, which the user can choose between under Options -> General
    ![winblock1](https://github.com/oskros/MF_counter_releases/blob/master/media/color_themes.png?raw=true)

### Extra options
In the config file you have the option to set the following to 0 (False) or 1 (True). This is also possible from within the application under "Options" and then under "General".
- always_on_top: choose whether the app window is on top of other programs (default True)
- tab_keys_global: choose whether changing tabs with ctrl+shift+pgup/pgdn works system wide, or only when app is in focus (default True)
- check_for_new_version: choose whether app should search for a new release on GitHub when opening (default True)
- enable_sound_effects: choose whether a sound should be played when pressing start/stop buttons
- pop-up_drop_window: show the drop window below the main application
- autocomplete: autocompletion of item names when typing them into the "add drop" window
- active_theme: change the theme of the application between dark/blue/vista
- start_run_delay: add an artificial delay to the start run button (requested by a user)
